# Customer-readiness and publication gate

Recorded: 2026-10-31 (Asia/Dubai)
Status: **NOT VERIFIED READY TO PUBLISH**. This is a gap-and-acceptance record, not proof of deployment, a sale, or a passed test.

## Exact product outcome
Gate agent actions with verifiable issuance, scope and revocation.

## Surgical acceptance checks (not yet passed)
1. [ ] Owner request and authorized admin decision persist in the database.
2. [ ] Signature, expiry, scope and revocation enforcement tested on protected endpoint.
3. [ ] Revoked or expired Passport denied after refresh; errors logged without secrets.
4. [ ] /demo artifacts must not be counted as production authority.

## Verified limitations / missing evidence
- Live issuer keys/database/auth not verified.
- Enforcement against downstream worker services not verified.
- No verified external customer transaction.

## Immediate next executable action
Execute issuance → authorized approval → downstream validation → revocation in an isolated environment.

## Customer evidence rule
Only identify a customer if a customer-specific contract, purchase/order, invoice and settled-payment receipt, or documented accepted delivery identifies the project. A source repository, GitHub issue, demo, live URL or CRM lead by itself does **not** prove a paying customer. Customer name, source reference, date, product mapping, amount and currency must be verified before adding revenue claims. No customer or payment transaction is asserted by this record.

## Payments: PayPal and Ziina
- Provider integration: **NOT CONNECTED / NOT VERIFIED** for this repository.
- Never commit API credentials, account details or webhook secrets.
- Before enabling a live checkout, confirm account ownership, platform approval, appropriate product/service, merchant terms, currency/tax handling, redirect URLs, authenticated callback/webhook verification, idempotency, refund and failure flow, and a provider-recorded transaction linked to this product.
- Do not substitute a manually supplied payment link for a verified merchant integration or claim a settlement from a checkout screen.

## Publication rule
No “live,” “customer-ready,” “selling,” or “payments enabled” label unless the corresponding independent evidence is attached with a timestamp, environment, test result, and accountable reviewer. Reversible preparation is allowed; production changes remain subject to actual external authorization/security boundaries.

Executing agent for this documentation change: GPT-6.
