# Cord Repository Change Plan

Status: proposed implementation sequence. No production security claim is made.

## Repository boundary
Public repository is limited to open Core specification and implementation, non-sensitive synthetic examples and test vectors, public extension specifications and SDK interfaces, security policy, contribution rules and release documentation.

Keep outside the public repository: customer/prospect data, personal names/contact details and identity documents; signed customer contracts, license registry and billing records; API keys, signing keys, tokens and passwords; private pricing, partner terms, commercial templates and proprietary model assets; raw watch serial numbers linked to owners, invoices, addresses and private provenance documents; legal advice, penetration-test details and confidential incident reports.

## Immediate public hygiene
1. Remove personal identity, personal profile links and donation/payment addresses from public README and examples where not required for protocol attribution.
2. Search tracked files for names, emails, phone numbers, addresses, wallet/payment identifiers, secrets, tokens, private URLs and realistic customer data.
3. Scan full Git history, branches, tags, issues, pull requests, discussions, releases and CI artifacts. Current-file cleanup does not erase prior commits or cached copies.
4. If a secret was exposed, revoke/rotate it first; history rewriting alone is insufficient.
5. If personal data was exposed, assess legal obligations and deletion/notification options; do not promise complete erasure from public forks or caches.
6. Use synthetic fixtures and a neutral security contact channel.

## Proposed repository structure
- spec/ — normative Core and extension specifications.
- docs/architecture/ — public architecture and trust boundaries.
- docs/security/ — public security model, threat model and disclosure process.
- docs/privacy/ — public privacy principles and data classification.
- docs/integrations/ — provider-neutral integration contracts.
- schemas/ — versioned public schemas.
- examples/synthetic/ — synthetic examples only.
- tests/ — positive, negative, fuzz and cross-language vectors.
- sdk/ — open SDKs and Core adapters.
- Proprietary commercial materials do not belong in this public repository.

## CI and repository protections
Add secret scanning and push protection where available; dependency and static analysis scanning; secret-safe fixtures and log-redaction checks; schema validation and cross-language vectors; branch protection, required reviews and status checks; CODEOWNERS; release provenance and dependency inventory; and a vulnerability reporting route that does not expose reporter data publicly.

CI must never echo secrets or upload sensitive fixtures as artifacts.

## Change sequence
### P0 — Contain and inventory
Review current README, tracked files and visible repository metadata. Remove unnecessary personal references and payment identifiers from current public docs. Review repository owner/profile visibility and commit identity configuration. Run secret and personal-data scans across current tree and full history. Rotate exposed credentials and handle exposures under an incident process.

### P1 — Establish architecture boundaries
Publish Master Architecture and Legal/Privacy Requirements. Clarify Core vs extensions vs commercial services vs Cord Analysis. Define data classification and public/private repository rules. Keep commercial implementation in a separate private repository after legal entity and IP rights are confirmed.

### P2 — Build safe foundations
Add security scanning, protected branches, CODEOWNERS and CI checks. Define tenant model, access control, key management, webhook authentication and audit logging. Implement privacy controls, retention, deletion and export before onboarding real users.

### P3 — Build first vertical
Define synthetic watch schemas and private-field handling. Implement source provenance and data-license register for market data. Separate asking prices from completed sales and expose uncertainty. Validate expert-attestation workflow; do not claim Cord itself authenticates watches.

### P4 — Commerce and payment evidence
Define order/payment/fulfilment event profiles. Integrate only through provider-approved APIs/webhooks. Keep payment credentials and funds outside Cord. Perform legal perimeter review before expanding payment functionality.

### P5 — Production gates
Independent code/security review and penetration testing; cross-language interoperability tests; legal review per target market and signed customer contracts; incident-response and restore exercises; documented operational readiness and release approval.

## Acceptance criteria
- No known personal data, secrets or confidential business data in the current public tree.
- Full-history scan completed and findings triaged.
- No secrets in CI logs/artifacts.
- Public examples use synthetic data.
- Public docs distinguish integrity from truth, identity, title, authenticity, payment settlement and delivery.
- Commercial code and customer data reside in access-controlled private systems.
- No production or compliance claim without independent evidence and documented approval.
