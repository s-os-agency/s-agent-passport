# Manus Browser Operator integration boundary

The owner supplied a saved documentation page named `manus-browser-operator.html`. It describes Manus's local browser extension, use of existing sessions, a dedicated visible tab, and per-task owner authorization. It provides no callable bridge from ChatGPT to Manus and no zero-credit execution guarantee. An authenticated browser session alone is not a Zero Trust authorization decision.

## Current implementation

S/Passport passkey operations use the existing authenticated application session over the deployment's HTTPS origin. Passkey private keys and local biometric data stay with the authenticator. The server verifies WebAuthn signatures, origin, RP ID, challenge, credential ownership, and user verification using SimpleWebAuthn. The server retains only the credential public key and metadata. Session tokens are hashed for the in-memory verification scope and are not logged or shared with Manus.

The five-minute unlock only applies to the same authenticated session. Credential management requires a fresh verification. The passport export gate reads current owner lock policy on every request and denies access when that policy cannot be loaded. Existing GatePass checks still govern agent capabilities and expiry.

## Live connection boundary

There is no supported Browser Operator transport exposed in this session. No browser session, cookie, token, vault secret, or passkey material may be exported to construct one. No Manus tasks are dispatched: the owner reserves Manus usage for important work.

To activate a future integration, first establish a documented supported transport and verify its execution cost. Use an allowlist of the exact Passport origin and intended operations, short-lived scoped authorization, visible task receipts, and an immediate revoke/stop path. A local extension session requires the owner authorization described by Manus. A passkey ceremony or a local IP address does not silently authorize a new Manus task. This is a rollout prerequisite, not an active connection.

## Verification before deployment

1. Configure `PASSKEY_ORIGIN` and HTTPS on the existing public hostname.
2. On a real device, enroll the first passkey, enable vault lock, verify, and export an owned passport.
3. Confirm a separate browser session stays locked; confirm expiry and logout relock it.
4. Verify enrollment of an additional credential, removal, and lock changes require a verified session.
5. Confirm a database outage blocks exports and a forged forwarded host cannot change RP scope.

Automated security tests cover policy and verifier configuration. They do not claim a hardware authenticator ceremony or live Manus connectivity.
