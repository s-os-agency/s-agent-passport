import { afterEach, describe, expect, it, vi } from "vitest";
vi.mock("./_core/env", () => ({ ENV: {
  appId: "test-app", cookieSecret: "test-only-session-key-32-characters", oAuthServerUrl: "https://auth.example.invalid",
} }));
import { sdk } from "./_core/sdk";
import { verificationScope } from "./webauthn";
import { COOKIE_NAME } from "../shared/const";
afterEach(() => vi.useRealTimers());
describe("session identity", () => {
  it("issues distinct verifiable tokens for simultaneous logins by the same owner", async () => {
    vi.useFakeTimers(); vi.setSystemTime(new Date("2026-10-16T05:00:00Z"));
    const first = await sdk.createSessionToken("owner", { name: "Owner" });
    const second = await sdk.createSessionToken("owner", { name: "Owner" });
    expect(first).not.toBe(second);
    expect(await sdk.verifySession(first)).toMatchObject({ openId: "owner" });
    expect(await sdk.verifySession(second)).toMatchObject({ openId: "owner" });
    const req = (token: string) => ({ headers: { cookie: `${COOKIE_NAME}=${token}` } });
    expect(verificationScope(7, req(first))).not.toBe(verificationScope(7, req(second)));
  });
});
