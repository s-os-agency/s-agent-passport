# s-agent-passport — Agent execution instructions

**Portfolio:** 3/16 (source row 3); **Lead agent:** ChatGPT; **specialty:** Identity, cryptography and revocation; **independent reviewer:** Grok (Independent adversarial source review).
**Repository:** https://github.com/s-os-agency/s-agent-passport
**Authoritative gates:** https://docs.google.com/spreadsheets/d/1MMk4Tx0k5rS7e_vOIFg-Dg022VEqXsdwqHibT9-3uOI/edit#gid=20261034
**Release dashboard:** https://docs.google.com/spreadsheets/d/1MMk4Tx0k5rS7e_vOIFg-Dg022VEqXsdwqHibT9-3uOI/edit#gid=20261035
**Disposition:** ACTIVATE; **accountable proposed engineering role:** Identity & Security Engineer.

## Mandatory operating rules
- Existing root AGENTS.md owner instruction controls: do not add, restore or run software test suites, test-only workflows or scaffolding. Existing spreadsheet references to tests are superseded: obtain real source/build/configuration and operational readback evidence within the owner policy. Never claim tests were run or passed.
- Inspect canonical README, source, existing diffs and deployments before changes. Make the smallest reversible implementation change required. Do not merely write plans or invent launch statuses.
- The named lead is a proposed execution assignment, **not proof of an active external agent session**, OpenRouter invocation, or authority to use another agent's account. A reviewer is an independent second-pass assignment, not an approval already provided.
- Use only scoped provider access actually available. No blind deployment, destructive migrations, new permissions, purchases or exposure of credentials. Preserve backups and rollback.
- Attach evidence URL, UTC date, version/commit, deployed environment and observed result to the corresponding Exact Completion Gates row. Mark VERIFIED only for evidence-backed completion. Leave other gates OPEN; no fabricated real customer, revenue, PayPal or Ziina status.
- Production launch requires a provider-backed deployment receipt and actual live runtime observation, not a green document or UI screenshot.

## Exact execution order

### Gate 3.1 — SOURCE
**Action:** Build and test canonical issuer web/server and database migrations; compare duplicate passport-server surface.
**Acceptance outcome:** Clean build/test and documented canonical source, DB schema and contract diff.
**Evidence required:** actual source/commit, environment, timestamp, direct output/receipt, and reviewer; record in sheet. **Initial state: OPEN.**

### Gate 3.2 — AUTH
**Action:** Verify account session, scoped identity issuance, signed token validation, expiry, denial and revocation.
**Acceptance outcome:** Issuer request cannot bypass approval; invalid and revoked token denied on downstream endpoint.
**Evidence required:** actual source/commit, environment, timestamp, direct output/receipt, and reviewer; record in sheet. **Initial state: OPEN.**

### Gate 3.3 — DATA
**Action:** Ensure stored identities/revocations/decision receipts persist after service restart and logs contain no secrets.
**Acceptance outcome:** After restart, same identity state and denial preserved; audit includes time and actor.
**Evidence required:** actual source/commit, environment, timestamp, direct output/receipt, and reviewer; record in sheet. **Initial state: OPEN.**

### Gate 3.4 — INTEGRATE
**Action:** Connect S-OS + one real worker to signed Passport authorization and revocation checks.
**Acceptance outcome:** Downstream worker accepts valid scope, rejects invalid/revoked scope with documented tests.
**Evidence required:** actual source/commit, environment, timestamp, direct output/receipt, and reviewer; record in sheet. **Initial state: OPEN.**

### Gate 3.5 — DEPLOY
**Action:** Deploy issuer/owner portal/admin endpoint under approved auth and managed keys, backup/rollback ready.
**Acceptance outcome:** Real HTTPS deployment, owner authentication and secret manager/backup proof.
**Evidence required:** actual source/commit, environment, timestamp, direct output/receipt, and reviewer; record in sheet. **Initial state: OPEN.**

### Gate 3.6 — LIVE PROOF
**Action:** Run authorized issuance → approval → action → revocation → rejection on deployed service.
**Acceptance outcome:** Audit record, passport ID, decision receipt and post-revocation denied request preserved.
**Evidence required:** actual source/commit, environment, timestamp, direct output/receipt, and reviewer; record in sheet. **Initial state: OPEN.**

### Gate 3.7 — COMMERCIAL
**Action:** Separate a usable security service from actual paying-customer verification.
**Acceptance outcome:** Do not show customers, subscriptions or revenue without identity-safe contract/settled order evidence.
**Evidence required:** actual source/commit, environment, timestamp, direct output/receipt, and reviewer; record in sheet. **Initial state: OPEN.**

## Completion handoff
Update each gate's verification state in Google Sheets and attach proof. Distinguish implementation from launch, customer acceptance from inquiries and settled payments from checkout creation. The lead produces the change receipt; the reviewer checks evidence independently. Do not announce completion until all required applicable gates pass. Report any unavoidable external authorization boundary specifically.

**Agent document author:** GPT-6 (instructions only; not a launch attestation).
