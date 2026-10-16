import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { COOKIE_NAME } from "../shared/const";
vi.mock("./db", () => ({ getDb: vi.fn() }));
vi.mock("@simplewebauthn/server", () => ({
  generateRegistrationOptions: vi.fn().mockResolvedValue({ challenge: "register-challenge" }),
  generateAuthenticationOptions: vi.fn().mockResolvedValue({ challenge: "auth-challenge" }),
  verifyRegistrationResponse: vi.fn().mockResolvedValue({ verified: false }),
  verifyAuthenticationResponse: vi.fn().mockResolvedValue({ verified: false }),
}));
import { getDb } from "./db";
import { verifyRegistrationResponse, verifyAuthenticationResponse } from "@simplewebauthn/server";
import {
  clearVerification, isRecentlyVerified, markVerified, rpFromRequest,
  verificationScope, vaultLockBlockReason, setVaultLock, removePasskey,
  startRegistration, finishRegistration, startAuthentication, finishAuthentication,
  VERIFY_WINDOW_MS,
} from "./webauthn";

const scope = "7:session-one";
const other = "7:session-two";
function database(rows: unknown[]) {
  const select = { from: vi.fn(), where: vi.fn(), limit: vi.fn() };
  select.from.mockReturnValue(select);
  select.where.mockReturnValue(Object.assign(Promise.resolve(rows), { limit: select.limit }));
  select.limit.mockResolvedValue(rows);
  const db = { select: vi.fn(() => select), insert: vi.fn(), delete: vi.fn(), update: vi.fn() };
  vi.mocked(getDb).mockResolvedValue(db as never);
  return db;
}
beforeEach(() => { clearVerification(scope); clearVerification(other); vi.mocked(getDb).mockResolvedValue(null); });
afterEach(() => { vi.useRealTimers(); vi.unstubAllEnvs(); vi.clearAllMocks(); });

describe("session-bound verification", () => {
  it("does not unlock another session of the same owner", () => {
    markVerified(scope);
    expect(isRecentlyVerified(scope)).toBe(true);
    expect(isRecentlyVerified(other)).toBe(false);
  });
  it("expires exactly at five minutes and rejects a clock rollback", () => {
    vi.useFakeTimers(); vi.setSystemTime(1000000); markVerified(scope);
    vi.advanceTimersByTime(VERIFY_WINDOW_MS);
    expect(isRecentlyVerified(scope)).toBe(false);
    markVerified(scope); vi.setSystemTime(1);
    expect(isRecentlyVerified(scope)).toBe(false);
  });
  it("clears unlock and outstanding challenges on logout", async () => {
    database([]);
    await startRegistration({ id: 7, name: null, email: null }, "example.com", scope);
    markVerified(scope); clearVerification(scope);
    expect(isRecentlyVerified(scope)).toBe(false);
    expect((await finishRegistration(7, {} as never, "example.com", "https://example.com", null, scope)).ok).toBe(false);
    expect(verifyRegistrationResponse).not.toHaveBeenCalled();
  });
  it("hashes tokens and isolates owners and sessions", () => {
    const req = { headers: { cookie: `${COOKIE_NAME}=secret-session` } };
    expect(verificationScope(7, req)).not.toContain("secret-session");
    expect(verificationScope(7, req)).not.toBe(verificationScope(8, req));
    expect(() => verificationScope(7, { headers: {} })).toThrow();
  });
});

describe("trusted origin", () => {
  it("uses configured HTTPS origin despite forged proxy headers", () => {
    vi.stubEnv("NODE_ENV", "production"); vi.stubEnv("PASSKEY_ORIGIN", "https://passport.example.com:8443");
    expect(rpFromRequest({ headers: { host: "evil.example", "x-forwarded-host": "evil.example", "x-forwarded-proto": "http" } }))
      .toEqual({ rpID: "passport.example.com", origin: "https://passport.example.com:8443" });
  });
  it("requires explicit production configuration", () => {
    vi.stubEnv("NODE_ENV", "production"); vi.stubEnv("PASSKEY_ORIGIN", "");
    expect(() => rpFromRequest({ headers: { host: "localhost:3000" } })).toThrow();
  });
  it.each(["http://example.com", "https://u:p@example.com", "https://example.com/path", "https://example.com?x=1", "https://example.com/#x"])("rejects invalid origin %s", value => {
    vi.stubEnv("PASSKEY_ORIGIN", value);
    expect(() => rpFromRequest({ headers: {} })).toThrow();
  });
  it("permits local development without trusting forwarded headers", () => {
    vi.stubEnv("NODE_ENV", "test"); vi.stubEnv("PASSKEY_ORIGIN", "");
    expect(rpFromRequest({ protocol: "http", headers: { host: "localhost:3000", "x-forwarded-host": "evil.example" } }))
      .toEqual({ rpID: "localhost", origin: "http://localhost:3000" });
  });
});

describe("vault policy", () => {
  it("blocks when database or owner policy is unavailable", async () => {
    expect(await vaultLockBlockReason(7, scope)).toBeTruthy();
    database([]); expect(await vaultLockBlockReason(7, scope)).toBeTruthy();
  });
  it("enforces the current lock state and current session", async () => {
    database([{ vaultLockEnabled: 1 }]); markVerified(other);
    expect(await vaultLockBlockReason(7, scope)).toBeTruthy();
    markVerified(scope); expect(await vaultLockBlockReason(7, scope)).toBeNull();
    database([{ vaultLockEnabled: 0 }]); expect(await vaultLockBlockReason(7, other)).toBeNull();
  });
  it("blocks unverified lock changes and credential deletion", async () => {
    const db = database([{ id: 1, userId: 7 }]);
    expect((await setVaultLock(7, false, scope)).ok).toBe(false);
    await expect(removePasskey(7, 1, scope)).rejects.toThrow();
    expect(db.update).not.toHaveBeenCalled(); expect(db.delete).not.toHaveBeenCalled();
  });
  it("requires an existing passkey to approve additional enrollment", async () => {
    database([{ id: 1, userId: 7 }]);
    await expect(startRegistration({ id: 7, name: null, email: null }, "example.com", scope)).rejects.toThrow();
  });
});

describe("ceremony guards", () => {
  it("requires server-side user verification and consumes registration challenges once", async () => {
    database([]);
    await startRegistration({ id: 7, name: null, email: null }, "example.com", scope);
    await finishRegistration(7, {} as never, "example.com", "https://example.com", null, scope);
    expect(verifyRegistrationResponse).toHaveBeenCalledWith(expect.objectContaining({ requireUserVerification: true, expectedChallenge: "register-challenge", expectedOrigin: "https://example.com" }));
    await finishRegistration(7, {} as never, "example.com", "https://example.com", null, scope);
    expect(verifyRegistrationResponse).toHaveBeenCalledTimes(1);
    expect(isRecentlyVerified(scope)).toBe(false);
  });
  it("rejects cross-session and expired challenges before verification", async () => {
    vi.useFakeTimers(); database([]);
    await startRegistration({ id: 7, name: null, email: null }, "example.com", scope);
    expect((await finishRegistration(7, {} as never, "example.com", "https://example.com", null, other)).ok).toBe(false);
    vi.advanceTimersByTime(VERIFY_WINDOW_MS);
    expect((await finishRegistration(7, {} as never, "example.com", "https://example.com", null, scope)).ok).toBe(false);
    expect(verifyRegistrationResponse).not.toHaveBeenCalled();
  });
  it("requires user verification on authentication and rejects unknown owners", async () => {
    database([{ userId: 7, credentialId: "cred", publicKey: "AA", counter: 0 }]);
    await startAuthentication(7, "example.com", scope);
    await finishAuthentication(7, { id: "cred" } as never, "example.com", "https://example.com", scope);
    expect(verifyAuthenticationResponse).toHaveBeenCalledWith(expect.objectContaining({ requireUserVerification: true }));
    database([{ userId: 8 }]);
    await startAuthentication(7, "example.com", scope);
    expect((await finishAuthentication(7, { id: "cred" } as never, "example.com", "https://example.com", scope)).ok).toBe(false);
    expect(verifyAuthenticationResponse).toHaveBeenCalledTimes(1);
  });
});
