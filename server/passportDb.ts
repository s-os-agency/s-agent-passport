/*
 * Query helpers for the Agent Passport product tables.
 */
import { and, desc, eq } from "drizzle-orm";
import {
  passportRequests,
  passports,
  vaultSecrets,
  type PassportRequest,
  type PassportRow,
  type InsertPassportRequest,
  type InsertPassportRow,
} from "../drizzle/schema";
import { getDb } from "./db";

function parseStoredJson(value: unknown): unknown {
  if (typeof value !== "string") return value;
  try {
    return JSON.parse(value);
  } catch {
    throw new Error("Stored Passport JSON is invalid.");
  }
}

function hydrateRequest(row: PassportRequest): PassportRequest {
  const toolIds = parseStoredJson(row.toolIds);
  const secretKeys = parseStoredJson(row.secretKeys);
  if (!Array.isArray(toolIds) || toolIds.some((item) => typeof item !== "string")
      || !Array.isArray(secretKeys) || secretKeys.some((item) => typeof item !== "string")) {
    throw new Error("Stored Passport request fields are invalid.");
  }
  return { ...row, toolIds, secretKeys };
}

function hydratePassport(row: PassportRow): PassportRow {
  const payload = parseStoredJson(row.payload);
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("Stored Passport payload is invalid.");
  }
  return { ...row, payload: payload as Record<string, unknown> };
}

async function requireDb() {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return db;
}

/* ===== Vault ===== */
export async function listVaultSecrets(userId: number) {
  const db = await requireDb();
  return db.select().from(vaultSecrets).where(eq(vaultSecrets.userId, userId)).orderBy(desc(vaultSecrets.createdAt));
}

export async function addVaultSecret(userId: number, keyName: string, valueEncrypted: string) {
  const db = await requireDb();
  await db.insert(vaultSecrets).values({ userId, keyName, valueEncrypted });
}

export async function deleteVaultSecret(userId: number, id: number) {
  const db = await requireDb();
  await db.delete(vaultSecrets).where(and(eq(vaultSecrets.id, id), eq(vaultSecrets.userId, userId)));
}

export async function getVaultSecretsByNames(userId: number, names: string[]) {
  const db = await requireDb();
  const all = await db.select().from(vaultSecrets).where(eq(vaultSecrets.userId, userId));
  return all.filter((s) => names.includes(s.keyName));
}

/* ===== Requests ===== */
export async function createRequest(values: InsertPassportRequest) {
  const db = await requireDb();
  const res = await db.insert(passportRequests).values(values);
  return res;
}

export async function listMyRequests(userId: number) {
  const db = await requireDb();
  const rows = await db.select().from(passportRequests).where(eq(passportRequests.userId, userId)).orderBy(desc(passportRequests.createdAt));
  return rows.map(hydrateRequest);
}

export async function listAllRequests() {
  const db = await requireDb();
  const rows = await db.select().from(passportRequests).orderBy(desc(passportRequests.createdAt));
  return rows.map(hydrateRequest);
}

export async function getRequestById(id: number) {
  const db = await requireDb();
  const rows = await db.select().from(passportRequests).where(eq(passportRequests.id, id)).limit(1);
  return rows[0] ? hydrateRequest(rows[0]) : undefined;
}

export async function decideRequest(
  id: number,
  status: "approved" | "denied",
  decidedBy: string,
  denialReason?: string,
) {
  const db = await requireDb();
  const result = await db
    .update(passportRequests)
    .set({ status, decidedBy, decidedAt: new Date(), denialReason: denialReason ?? null })
    .where(and(eq(passportRequests.id, id), eq(passportRequests.status, "pending")));
  return result[0].affectedRows === 1;
}

export async function approveRequest(
  id: number,
  decidedBy: string,
  createPassport: (request: PassportRequest) => InsertPassportRow,
) {
  const db = await requireDb();
  return db.transaction(async (tx) => {
    const [request] = await tx.select().from(passportRequests)
      .where(eq(passportRequests.id, id)).limit(1).for("update");
    if (!request) return { status: "not_found" } as const;
    if (request.status !== "pending") return { status: "already_decided" } as const;

    const passport = createPassport(hydrateRequest(request));
    await tx.insert(passports).values(passport);
    await tx.update(passportRequests)
      .set({ status: "approved", decidedBy, decidedAt: new Date(), denialReason: null })
      .where(and(eq(passportRequests.id, id), eq(passportRequests.status, "pending")));
    return { status: "approved", passportId: passport.passportId } as const;
  });
}

/* ===== Passports ===== */
export async function insertPassport(values: InsertPassportRow) {
  const db = await requireDb();
  await db.insert(passports).values(values);
}

export async function listMyPassports(userId: number) {
  const db = await requireDb();
  const rows = await db.select().from(passports).where(eq(passports.userId, userId)).orderBy(desc(passports.issuedAt));
  return rows.map(hydratePassport);
}

export async function listAllPassports() {
  const db = await requireDb();
  const rows = await db.select().from(passports).orderBy(desc(passports.issuedAt));
  return rows.map(hydratePassport);
}

export async function getPassportByRequestId(requestId: number) {
  const db = await requireDb();
  const rows = await db.select().from(passports).where(eq(passports.requestId, requestId)).limit(1);
  return rows[0] ? hydratePassport(rows[0]) : undefined;
}

export async function getPassportById(id: number) {
  const db = await requireDb();
  const rows = await db.select().from(passports).where(eq(passports.id, id)).limit(1);
  return rows[0] ? hydratePassport(rows[0]) : undefined;
}

export async function revokePassport(id: number, reason: string) {
  const db = await requireDb();
  await db.update(passports).set({ status: "revoked", revokedAt: new Date(), revokeReason: reason }).where(eq(passports.id, id));
}
