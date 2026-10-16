/**
 * WebAuthn (passkey) support for the Agent Passport portal.
 *
 * Owners may enroll Face ID / fingerprint / security-key passkeys and enable
 * the "vault lock": once enabled, sensitive actions (vault .env export,
 * embed bundle, owner dossier export) require a passkey verification within
 * the last VERIFY_WINDOW_MS.
 *
 * Challenges and recent verifications are kept in in-process maps — fine for
 * a single-instance deployment; they are short-lived and safe to lose on
 * restart (the user simply re-verifies).
 */
import {
  generateAuthenticationOptions,
  generateRegistrationOptions,
  verifyAuthenticationResponse,
  verifyRegistrationResponse,
  type AuthenticationResponseJSON,
  type AuthenticatorTransportFuture,
  type RegistrationResponseJSON,
} from "@simplewebauthn/server";
import { createHash } from "node:crypto";
import { parse as parseCookieHeader } from "cookie";
import { COOKIE_NAME } from "../shared/const";
import { eq } from "drizzle-orm";
import { passkeys, users, type Passkey } from "../drizzle/schema";
import { getDb } from "./db";

const RP_NAME = "Agent Passport";
const CHALLENGE_TTL_MS = 5 * 60 * 1000;
/** How long a passkey verification unlocks sensitive actions. */
export const VERIFY_WINDOW_MS = 5 * 60 * 1000;

type ChallengeEntry = { challenge: string; expires: number };
const regChallenges = new Map<string, ChallengeEntry>();
const authChallenges = new Map<string, ChallengeEntry>();
const recentVerifications = new Map<string, number>(); // user/session digest → verifiedAt ms

function putChallenge(map: Map<string, ChallengeEntry>, scope: string, challenge: string) {
  map.set(scope, { challenge, expires: Date.now() + CHALLENGE_TTL_MS });
}

function takeChallenge(map: Map<string, ChallengeEntry>, scope: string): string | null {
  const entry = map.get(scope);
  map.delete(scope);
  if (!entry || entry.expires <= Date.now()) return null;
  return entry.challenge;
}

/** Bind ceremonies and unlocks to the authenticated session, without retaining tokens. */
export function verificationScope(userId: number, req: { headers: Record<string, unknown> }): string {
  const cookie = req.headers.cookie;
  const token = typeof cookie === "string" ? parseCookieHeader(cookie)[COOKIE_NAME] : undefined;
  if (!token) throw new Error("An authenticated session is required for passkey verification.");
  return `${userId}:${createHash("sha256").update(token).digest("hex")}`;
}

export function clearVerification(scope: string) {
  recentVerifications.delete(scope);
  regChallenges.delete(scope);
  authChallenges.delete(scope);
}

/** Production trust comes from deployment configuration, never forwarded headers. */
export function rpFromRequest(req: { protocol?: string; headers: Record<string, unknown> }): {
  rpID: string;
  origin: string;
} {
  const configured = process.env.PASSKEY_ORIGIN;
  if (!configured && process.env.NODE_ENV === "production") {
    throw new Error("PASSKEY_ORIGIN must be configured in production.");
  }
  const raw = configured || `${req.protocol || "http"}://${req.headers.host || "localhost"}`;
  const url = new URL(raw);
  const local = url.hostname === "localhost" || url.hostname === "127.0.0.1";
  if (url.username || url.password || url.pathname !== "/" || url.search || url.hash ||
      (url.protocol !== "https:" && !(local && url.protocol === "http:")) ||
      (!configured && !local)) {
    throw new Error("Set PASSKEY_ORIGIN to the exact trusted HTTPS origin.");
  }
  return { rpID: url.hostname, origin: url.origin };
}

/* ============ registration ============ */

export async function startRegistration(
  user: { id: number; name: string | null; email: string | null },
  rpID: string,
  scope: string,
) {
  const db = await getDb();
  if (!db) throw new Error("Database unavailable.");
  const existing: Passkey[] = await db.select().from(passkeys).where(eq(passkeys.userId, user.id));

  if (existing.length && !isRecentlyVerified(scope)) {
    throw new Error("Verify an existing passkey before enrolling another one.");
  }
  const options = await generateRegistrationOptions({
    rpName: RP_NAME,
    rpID,
    userName: user.email || user.name || `owner-${user.id}`,
    userDisplayName: user.name || "Owner",
    attestationType: "none",
    excludeCredentials: existing.map((p) => ({
      id: p.credentialId,
      transports: (p.transports?.split(",") ?? []) as AuthenticatorTransportFuture[],
    })),
    authenticatorSelection: {
      residentKey: "preferred",
      userVerification: "required",
    },
  });
  putChallenge(regChallenges, scope, options.challenge);
  return options;
}

export async function finishRegistration(
  userId: number,
  response: RegistrationResponseJSON,
  rpID: string,
  origin: string,
  label: string | null,
  scope: string,
): Promise<{ ok: boolean; reason?: string }> {
  const expectedChallenge = takeChallenge(regChallenges, scope);
  if (!expectedChallenge) return { ok: false, reason: "Challenge expired — try again." };

  const verification = await verifyRegistrationResponse({
    response,
    expectedChallenge,
    expectedOrigin: origin,
    expectedRPID: rpID,
    requireUserVerification: true,
  });
  if (!verification.verified || !verification.registrationInfo) {
    return { ok: false, reason: "Registration could not be verified." };
  }

  const info = verification.registrationInfo;
  const db = await getDb();
  if (!db) return { ok: false, reason: "Database unavailable." };

  const existing = await db.select().from(passkeys).where(eq(passkeys.userId, userId));
  if (existing.length && !isRecentlyVerified(scope)) {
    return { ok: false, reason: "Verify an existing passkey before enrolling another one." };
  }

  await db.insert(passkeys).values({
    userId,
    credentialId: info.credential.id,
    publicKey: Buffer.from(info.credential.publicKey).toString("base64url"),
    counter: info.credential.counter,
    transports: (info.credential.transports ?? []).join(",") || null,
    deviceType: info.credentialDeviceType,
    backedUp: info.credentialBackedUp ? 1 : 0,
    label,
  });
  // Enrolling counts as a fresh verification.
  recentVerifications.set(scope, Date.now());
  return { ok: true };
}

/* ============ authentication (unlock) ============ */

export async function startAuthentication(userId: number, rpID: string, scope: string) {
  const db = await getDb();
  const creds: Passkey[] = db
    ? await db.select().from(passkeys).where(eq(passkeys.userId, userId))
    : [];
  if (creds.length === 0) return null;

  const options = await generateAuthenticationOptions({
    rpID,
    userVerification: "required",
    allowCredentials: creds.map((p) => ({
      id: p.credentialId,
      transports: (p.transports?.split(",") ?? []) as AuthenticatorTransportFuture[],
    })),
  });
  putChallenge(authChallenges, scope, options.challenge);
  return options;
}

export async function finishAuthentication(
  userId: number,
  response: AuthenticationResponseJSON,
  rpID: string,
  origin: string,
  scope: string,
): Promise<{ ok: boolean; reason?: string }> {
  const expectedChallenge = takeChallenge(authChallenges, scope);
  if (!expectedChallenge) return { ok: false, reason: "Challenge expired — try again." };

  const db = await getDb();
  if (!db) return { ok: false, reason: "Database unavailable." };

  const rows = await db
    .select()
    .from(passkeys)
    .where(eq(passkeys.credentialId, response.id))
    .limit(1);
  const cred = rows[0];
  if (!cred || cred.userId !== userId) {
    return { ok: false, reason: "Unknown credential." };
  }

  const verification = await verifyAuthenticationResponse({
    response,
    expectedChallenge,
    expectedOrigin: origin,
    expectedRPID: rpID,
    requireUserVerification: true,
    credential: {
      id: cred.credentialId,
      publicKey: Buffer.from(cred.publicKey, "base64url"),
      counter: cred.counter,
      transports: (cred.transports?.split(",") ?? []) as AuthenticatorTransportFuture[],
    },
  });
  if (!verification.verified) return { ok: false, reason: "Verification failed." };

  await db
    .update(passkeys)
    .set({ counter: verification.authenticationInfo.newCounter, lastUsedAt: new Date() })
    .where(eq(passkeys.id, cred.id));
  recentVerifications.set(scope, Date.now());
  return { ok: true };
}

/* ============ vault-lock gate ============ */

export function markVerified(scope: string) {
  recentVerifications.set(scope, Date.now());
}

export function isRecentlyVerified(scope: string): boolean {
  const at = recentVerifications.get(scope);
  if (at === undefined) return false;
  const age = Date.now() - at;
  if (age < 0 || age >= VERIFY_WINDOW_MS) {
    recentVerifications.delete(scope);
    return false;
  }
  return true;
}

/**
 * Throws-free gate check used by sensitive procedures.
 * Returns null when access is allowed, otherwise a human-readable reason.
 */
export async function vaultLockBlockReason(userId: number, scope: string): Promise<string | null> {
  const db = await getDb();
  if (!db) return "Security policy unavailable — retry when the database is available.";
  const rows = await db.select().from(users).where(eq(users.id, userId)).limit(1);
  const u = rows[0];
  if (!u) return "Owner security policy unavailable.";
  if (!u.vaultLockEnabled) return null;
  if (isRecentlyVerified(scope)) return null;
  return "Vault lock is on — verify with your passkey (Face ID / fingerprint) first.";
}

/* ============ management ============ */

export async function listPasskeys(userId: number) {
  const db = await getDb();
  if (!db) return [];
  const rows = await db.select().from(passkeys).where(eq(passkeys.userId, userId));
  return rows.map((p) => ({
    id: p.id,
    label: p.label,
    deviceType: p.deviceType,
    backedUp: !!p.backedUp,
    createdAt: p.createdAt,
    lastUsedAt: p.lastUsedAt,
  }));
}

export async function removePasskey(userId: number, id: number, scope: string): Promise<boolean> {
  const db = await getDb();
  if (!db) return false;
  const rows = await db.select().from(passkeys).where(eq(passkeys.id, id)).limit(1);
  if (!rows[0] || rows[0].userId !== userId) return false;
  if (!isRecentlyVerified(scope)) throw new Error("Verify your passkey before removing a credential.");
  await db.delete(passkeys).where(eq(passkeys.id, id));

  // If that was the last passkey, disable the vault lock so the owner is not locked out.
  const remaining = await db.select().from(passkeys).where(eq(passkeys.userId, userId));
  if (remaining.length === 0) {
    await db.update(users).set({ vaultLockEnabled: 0 }).where(eq(users.id, userId));
  }
  // Credential changes invalidate every existing unlock for this owner.
  const scopes = Array.from(recentVerifications.keys())
    .concat(Array.from(regChallenges.keys()), Array.from(authChallenges.keys()));
  scopes.forEach(key => {
    if (key.startsWith(`${userId}:`)) clearVerification(key);
  });
  return true;
}

export async function setVaultLock(userId: number, enabled: boolean, scope: string): Promise<{ ok: boolean; reason?: string }> {
  const db = await getDb();
  if (!db) return { ok: false, reason: "Database unavailable." };
  if (!isRecentlyVerified(scope)) return { ok: false, reason: "Verify your passkey before changing vault lock." };
  if (enabled) {
    const creds = await db.select().from(passkeys).where(eq(passkeys.userId, userId));
    if (creds.length === 0) {
      return { ok: false, reason: "Enroll a passkey first — otherwise you would lock yourself out." };
    }
  }
  await db.update(users).set({ vaultLockEnabled: enabled ? 1 : 0 }).where(eq(users.id, userId));
  return { ok: true };
}
