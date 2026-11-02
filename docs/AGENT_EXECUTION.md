# s-agent-passport — Work instructions and current evidence

**Portfolio:** 3/16 (source row 3); **Proposed lead (not dispatched):** ChatGPT; **specialty:** Identity, cryptography and revocation; **Proposed reviewer (not dispatched):** Grok (Independent adversarial source review).
**Repository:** https://github.com/s-os-agency/s-agent-passport
**Existing work-item records:** https://docs.google.com/spreadsheets/d/1MMk4Tx0k5rS7e_vOIFg-Dg022VEqXsdwqHibT9-3uOI/edit#gid=20261034
**Existing release record:** https://docs.google.com/spreadsheets/d/1MMk4Tx0k5rS7e_vOIFg-Dg022VEqXsdwqHibT9-3uOI/edit#gid=20261035
**Suggested work:** Complete the identity service; **Proposed human role (not staffed):** Identity & Security Engineer.

## Rules for actual work
- Existing root AGENTS.md owner instruction controls: do not add, restore or run software test suites, test-only workflows or scaffolding. Existing spreadsheet references to tests are superseded: obtain real source/build/configuration and operational readback evidence within the owner policy. Never claim tests were run or passed.
- Inspect canonical README, source, existing diffs and deployments before changes. Make the smallest reversible implementation change required. Do not merely write plans or invent launch statuses.
- The named lead is a proposed execution assignment, **not proof of an active external agent session**, OpenRouter invocation, or authority to use another agent's account. A reviewer is an independent second-pass assignment, not an approval already provided.
- Use only scoped provider access actually available. No blind deployment, destructive migrations, new permissions, purchases or exposure of credentials. Preserve backups and rollback.
- Attach evidence URL, UTC date, version/commit, deployed environment and observed result to the corresponding Exact Completion Gates row. Mark VERIFIED only for evidence-backed completion. Leave other gates OPEN; no fabricated real customer, revenue, PayPal or Ziina status.
- Production launch requires a provider-backed deployment receipt and actual live runtime observation, not a green document or UI screenshot.

## Work that still needs evidence

### Work item 3.1 — SOURCE
**Action:** Inspect the identity server, website and database changes; compare any duplicate server code without running tests.
**Expected result:** Identify the source used by the service, its database structure and actual differences from duplicate code. Do not claim tests passed.
**Proof needed:** Real source or commit, environment, time and observed result; add independent review only if it actually happened. Record verified results in the existing sheet. **Recorded state: OPEN; not rechecked here.**

### Work item 3.2 — AUTH
**Action:** Verify account session, scoped identity issuance, signed token validation, expiry, denial and revocation.
**Acceptance outcome:** Issuer request cannot bypass approval; invalid and revoked token denied on downstream endpoint.
**Proof needed:** Real source or commit, environment, time and observed result; add independent review only if it actually happened. Record verified results in the existing sheet. **Recorded state: OPEN; not rechecked here.**

### Work item 3.3 — DATA
**Action:** Ensure stored identities/revocations/decision receipts persist after service restart and logs contain no secrets.
**Acceptance outcome:** After restart, same identity state and denial preserved; audit includes time and actor.
**Proof needed:** Real source or commit, environment, time and observed result; add independent review only if it actually happened. Record verified results in the existing sheet. **Recorded state: OPEN; not rechecked here.**

### Work item 3.4 — INTEGRATE
**Action:** Connect S-OS + one real worker to signed Passport authorization and revocation checks.
**Expected result:** Confirm the worker respects allowed permissions and rejects invalid or revoked ones using actual authorized operational evidence, not tests.
**Proof needed:** Real source or commit, environment, time and observed result; add independent review only if it actually happened. Record verified results in the existing sheet. **Recorded state: OPEN; not rechecked here.**

### Work item 3.5 — DEPLOY
**Action:** Deploy issuer/owner portal/admin endpoint under approved auth and managed keys, backup/rollback ready.
**Acceptance outcome:** Real HTTPS deployment, owner authentication and secret manager/backup proof.
**Proof needed:** Real source or commit, environment, time and observed result; add independent review only if it actually happened. Record verified results in the existing sheet. **Recorded state: OPEN; not rechecked here.**

### Work item 3.6 — LIVE PROOF
**Action:** Run authorized issuance → approval → action → revocation → rejection on deployed service.
**Acceptance outcome:** Audit record, passport ID, decision receipt and post-revocation denied request preserved.
**Proof needed:** Real source or commit, environment, time and observed result; add independent review only if it actually happened. Record verified results in the existing sheet. **Recorded state: OPEN; not rechecked here.**

### Work item 3.7 — COMMERCIAL
**Action:** Separate a usable security service from actual paying-customer verification.
**Acceptance outcome:** Do not show customers, subscriptions or revenue without identity-safe contract/settled order evidence.
**Proof needed:** Real source or commit, environment, time and observed result; add independent review only if it actually happened. Record verified results in the existing sheet. **Recorded state: OPEN; not rechecked here.**

## How to report completed work
Update each gate's verification state in Google Sheets and attach proof. Distinguish implementation from launch, customer acceptance from inquiries and settled payments from checkout creation. The lead produces the change receipt; the reviewer checks evidence independently. Do not announce completion until all required applicable gates pass. Report any unavoidable external authorization boundary specifically.

**Original document author:** GPT-6. This text does not prove a launch, an agent assignment or any running service.
