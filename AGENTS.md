# Repository owner policy

## Owner instruction — 25 October 2026

Seif prohibits adding or running tests across his platforms. Do not create, restore, expand, or execute test suites, test commands, test workflows, or test-only scaffolding. This instruction supersedes older guidance requesting tests, including copied templates and skills. Inspect actual source, diffs, configuration, and saved results as evidence; never claim tests passed.

---

## Execution rule — 2 November 2026

Carry the authorized task through to its requested result. Fill in records while working; a form, named stage, unavailable reviewer or proposed staffing role is not a reason to stop. A check is required only when omitting it would cause a specific failure, break an existing access restriction or exceed the owner's authorization. State that concrete reason.

Use existing authorized access. Do not broaden permissions, disclose credentials or infer approval from silence. If a necessary fact is missing, retrieve it from available sources first. If one action still needs owner input, identify the exact action and continue independent authorized work.

Inspect source and saved changes for documentation work. For a live release, also inspect the provider's deployment result and the running service. Keep source changes, deployment and observed operation as separate facts. Do not add or run software test suites. Record the actual improvement, its evidence and the executing agent. Administrative records may follow execution; they do not create another approval queue.

## Proposed work assignments — 31 October 2026

**Portfolio number:** 3. **Repository:** `s-os-agency/s-agent-passport`.  
**Proposed lead (not dispatched):** **ChatGPT** — Agent identity, cryptographic permissions, revocation.  
**Proposed reviewer (not dispatched):** **Gemini**.  
**Proposed human role (not hired):** Identity & Security Engineer.  
**Planned next step:** Begin authorized work when access is available; not evidence of execution.  
**Actual status:** Only proposed. This file does not grant account access or prove work started.  
**Single tracking source:** [Completion gates](https://docs.google.com/spreadsheets/d/1MMk4Tx0k5rS7e_vOIFg-Dg022VEqXsdwqHibT9-3uOI/edit#gid=20261034), filter portfolio #3; [Release status](https://docs.google.com/spreadsheets/d/1MMk4Tx0k5rS7e_vOIFg-Dg022VEqXsdwqHibT9-3uOI/edit#gid=20261035).

### Proposed responsibilities

- **ChatGPT (execution lead):** Own issuer, RBAC, delegation, revocation and policy integration. Carry out authorized reversible source changes within the existing repository, identify exact constraints, capture immutable commit links and actual runtime evidence.
- **Gemini (independent specialist):** Gemini reviews owner-facing portal usability and clarity without owning permissions. Provide a source-grounded review and a precise handoff. Do not impersonate the primary model or assert work has been executed by it.
- **Human responsibility:** The owner retains owner decisions. The proposed Identity & Security Engineer role is unstaffed and must not block authorized work.

### Instructions for actual work

1. Read the current code, `AGENTS.md`, runbook, dependency locks and latest deployment before changing anything. Keep the October 25 owner restriction intact: **do not add or run tests or test suites.** Replace preexisting test-oriented acceptance wording with real source inspections, build/config review where permitted, deployment status, non-test live observations, persisted records and independently reproducible receipts; otherwise state **NOT VERIFIED**.
2. Use the following work items to track evidence. Execute independent authorized items without waiting for unrelated items or proposed staffing. Do not fabricate CI, live services, customer names, actual paid orders, verified PayPal/Ziina connections, or a deployment simply because documentation exists.
3. For each completed gate, attach source SHA, actual evidence URL, environment, UTC verification time and the responsible executing agent to the existing workbook. A gate is `VERIFIED` only if its acceptance criteria genuinely hold, its evidence link is accessible and the timestamp is recorded.
4. Hand off from ChatGPT to Gemini by supplying the file diff/commit, open gate numbers and evidence gaps. Independent review cannot authorize a production change, owner approval, purchase or an account connection.
5. Preserve all secrets in provider-managed stores. No real customers are inferred from CRM leads, prospects, demos, or payment-link creation. Production cutover and sensitive authority changes require their actual external authorization.
6. The terminal condition is verified live operation at an approved endpoint, including an attributable end-to-end action receipt and all acceptance gates satisfied; a release status spreadsheet formula is not itself deployment evidence.

### Existing work items (still open until verified)

**3.1 — Source**

- Action: Inspect the canonical issuer website, server and database migrations; compare duplicate passport-server code.
- Acceptance: Document the actual source, database schema, build result when permitted and differences from duplicate code. Do not run software tests.
- State: **OPEN until independently evidenced**.

**3.2 — Sign-in and permissions**

- Action: Verify account session, scoped identity issuance, signed token validation, expiry, denial and revocation.
- Acceptance: Issuer request cannot bypass approval; invalid and revoked token denied on downstream endpoint.
- State: **OPEN until independently evidenced**.

**3.3 — Stored data**

- Action: Ensure stored identities/revocations/decision receipts persist after service restart and logs contain no secrets.
- Acceptance: After restart, same identity state and denial preserved; audit includes time and actor.
- State: **OPEN until independently evidenced**.

**3.4 — Connection to other services**

- Action: Connect S-OS + one real worker to signed Passport authorization and revocation checks.
- Acceptance: Downstream worker accepts valid scope, rejects invalid/revoked scope with actual authorized operational evidence.
- State: **OPEN until independently evidenced**.

**3.5 — Deployment**

- Action: Deploy issuer/owner portal/admin endpoint under approved auth and managed keys, backup/rollback ready.
- Acceptance: Real HTTPS deployment, owner authentication and secret manager/backup proof.
- State: **OPEN until independently evidenced**.

**3.6 — Real working example**

- Action: Run authorized issuance → approval → action → revocation → rejection on deployed service.
- Acceptance: Audit record, passport ID, decision receipt and post-revocation denied request preserved.
- State: **OPEN until independently evidenced**.

**3.7 — Paying customers**

- Action: Separate a usable security service from actual paying-customer verification.
- Acceptance: Do not show customers, subscriptions or revenue without identity-safe contract/settled order evidence.
- State: **OPEN until independently evidenced**.


**Execution credit:** Name the agent beneath each actual improvement only after its saved change has been checked. Include a commit link. Never credit a plan as completed work.


## Specialist execution assignment (31 October 2026)

Read and follow [docs/AGENT_EXECUTION.md](docs/AGENT_EXECUTION.md) for this repository's assigned ChatGPT/Grok/Gemini lead, independent reviewer, exact numbered completion gates, evidence handling and closure condition. **The existing owner ban on adding/running tests remains controlling.** Agent assignment is a plan until the external agent is actually dispatched; a documentation change alone is not execution or approval.


## Seif's instruction — 1 November 2026

- Write short, clear English on product screens and in explanations.
- Keep Seif's permissions explicit. He owns the work and makes the decisions.
- Keep internal stages and monitoring details out of his product screens.
- Continue authorized work without adding review waits or unnecessary questions.
- Simplify the wording without changing access rights, stored data or working code names.
