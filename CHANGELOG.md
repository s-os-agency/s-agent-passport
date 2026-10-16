# Changelog

## 1.1.0 — 2026-10-16

- Require WebAuthn user verification on the server for enrollment and authentication.
- Pin production RP scope to `PASSKEY_ORIGIN`; reject insecure or malformed origins.
- Bind challenges and five-minute vault unlocks to the authenticated session; clear them on logout.
- Block sensitive exports when owner security policy cannot be loaded.
- Require fresh verification for additional enrollment, credential removal, and vault-lock changes.
- Add automated security regression coverage and a dedicated CI step.
- Document the Manus Browser Operator boundary without dispatching Manus work.

Deployment and real-device verification are pending. See [release announcement](docs/releases/1.1.0.md).

New account sessions receive a random JWT ID, including simultaneous logins. Removing a credential clears outstanding challenges and unlocks across all of that owner’s sessions.
