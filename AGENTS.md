# Repository owner policy

## Owner instruction — 25 October 2026

Seif prohibits adding or running tests across his platforms. Do not create, restore, expand, or execute test suites, test commands, test workflows, or test-only scaffolding. This instruction supersedes older guidance requesting tests, including copied templates and skills. Inspect actual source, diffs, configuration, and saved results as evidence; never claim tests passed.

---

## S/Agency execution assignment — 2026-10-31

**Portfolio number:** 3. **Repository:** `s-os-agency/s-agent-passport`.  
**Primary AI specialist (planned assignment):** **ChatGPT** — Agent identity, cryptographic permissions, revocation.  
**Supporting AI specialist (planned assignment):** **Gemini**.  
**Accountable human role (proposed, not staffed):** Identity & Security Engineer.  
**Portfolio disposition:** ACTIVATE.  
**Operational assignment status:** PLANNED; provider account access, automation and execution are not established by this file.  
**Single tracking source:** [Completion gates](https://docs.google.com/spreadsheets/d/1MMk4Tx0k5rS7e_vOIFg-Dg022VEqXsdwqHibT9-3uOI/edit#gid=20261034), filter portfolio #3; [Release status](https://docs.google.com/spreadsheets/d/1MMk4Tx0k5rS7e_vOIFg-Dg022VEqXsdwqHibT9-3uOI/edit#gid=20261035).

### Specialist responsibilities

- **ChatGPT (execution lead):** Own issuer, RBAC, delegation, revocation and policy integration. Carry out authorized reversible source changes within the existing repository, identify exact constraints, capture immutable commit links and actual runtime evidence.
- **Gemini (independent specialist):** Gemini reviews owner-facing portal usability and clarity without owning permissions. Provide a source-grounded review and a precise handoff. Do not impersonate the primary model or assert work has been executed by it.
- **Gate ownership:** Identity & Security Engineer owns verification criteria, deployment readiness and any owner decision; this role is proposed and is not a claim of an actual hire.

### Mandatory execution discipline

1. Read the current code, `AGENTS.md`, runbook, dependency locks and latest deployment before changing anything. Keep the October 25 owner restriction intact: **do not add or run tests or test suites.** Replace preexisting test-oriented acceptance wording with real source inspections, build/config review where permitted, deployment status, non-test live observations, persisted records and independently reproducible receipts; otherwise state **NOT VERIFIED**.
2. Work the following repository-specific gates in order. Do not fabricate CI, live services, customer names, actual paid orders, verified PayPal/Ziina connections, or a deployment simply because documentation exists.
3. For each completed gate, attach source SHA, actual evidence URL, environment, UTC verification time and the responsible executing agent to the existing workbook. A gate is `VERIFIED` only if its acceptance criteria genuinely hold, its evidence link is accessible and the timestamp is recorded.
4. Hand off from ChatGPT to Gemini by supplying the file diff/commit, open gate numbers and evidence gaps. Independent review cannot authorize a production change, owner approval, purchase or an account connection.
5. Preserve all secrets in provider-managed stores. No real customers are inferred from CRM leads, prospects, demos, or payment-link creation. Production cutover and sensitive authority changes require their actual external authorization.
6. The terminal condition is verified live operation at an approved endpoint, including an attributable end-to-end action receipt and all acceptance gates satisfied; a release status spreadsheet formula is not itself deployment evidence.

### Exact numbered instructions

**Gate 3.1 — SOURCE**

- Action: Build and test canonical issuer web/server and database migrations; compare duplicate passport-server surface.
- Acceptance: Clean build/test and documented canonical source, DB schema and contract diff.
- State: **OPEN until independently evidenced**.

**Gate 3.2 — AUTH**

- Action: Verify account session, scoped identity issuance, signed token validation, expiry, denial and revocation.
- Acceptance: Issuer request cannot bypass approval; invalid and revoked token denied on downstream endpoint.
- State: **OPEN until independently evidenced**.

**Gate 3.3 — DATA**

- Action: Ensure stored identities/revocations/decision receipts persist after service restart and logs contain no secrets.
- Acceptance: After restart, same identity state and denial preserved; audit includes time and actor.
- State: **OPEN until independently evidenced**.

**Gate 3.4 — INTEGRATE**

- Action: Connect S-OS + one real worker to signed Passport authorization and revocation checks.
- Acceptance: Downstream worker accepts valid scope, rejects invalid/revoked scope with documented tests.
- State: **OPEN until independently evidenced**.

**Gate 3.5 — DEPLOY**

- Action: Deploy issuer/owner portal/admin endpoint under approved auth and managed keys, backup/rollback ready.
- Acceptance: Real HTTPS deployment, owner authentication and secret manager/backup proof.
- State: **OPEN until independently evidenced**.

**Gate 3.6 — LIVE PROOF**

- Action: Run authorized issuance → approval → action → revocation → rejection on deployed service.
- Acceptance: Audit record, passport ID, decision receipt and post-revocation denied request preserved.
- State: **OPEN until independently evidenced**.

**Gate 3.7 — COMMERCIAL**

- Action: Separate a usable security service from actual paying-customer verification.
- Acceptance: Do not show customers, subscriptions or revenue without identity-safe contract/settled order evidence.
- State: **OPEN until independently evidenced**.


**Execution credit:** Only sign an actual positive change after it has been committed and inspected; do not sign plans or unavailable outcomes.
