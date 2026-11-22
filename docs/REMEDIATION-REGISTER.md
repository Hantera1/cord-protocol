# Cord Hardening Audit and Remediation Register

**Status:** Initial repository-level triage; not a completed security audit.
**Baseline reviewed:** `main` at commit `219ee7f68f6d00ceb5ae452dc49e90c2e584711f` (2026-11-22).
**Purpose:** Track verifiable defects, required evidence, owners and release gates. This document must not be represented as proof that any item is fixed.

## 1. Current verified state

- The default branch is `main`; it was reported as unprotected during the initial repository review.
- Pull requests #2 through #8 are open and unmerged. PR #7 and #8 are draft PRs; PR #8 targets PR #7's branch and must be reviewed as a dependency stack.
- PR #1 is merged. Its description reports Python Core, experimental Ed25519 receipt signatures and an experimental receipt chain. The reported CI success applies to the cited workflow runs and commit only.
- Recent CI runs for PR #8 completed successfully, but this is not an independent security review or production certification.
- The current README identifies Cord as an experimental draft and explicitly limits what a Core PASS means. Preserve this caution.
- The current README contains donation wallet addresses and links to image assets. Decide deliberately whether these belong in a protocol repository; do not treat their presence alone as proof of compromise.
- The current repository contains both `logo.png.PNG` and `logo_dark.png.PNG`. Branding assets and README references need a deliberate, tested replacement plan.
- The repository description and README currently describe the project using different levels of scope. Establish one canonical product definition and reuse it consistently.

## 2. Release-blocking remediation register

### A. Repository security and governance

- [ ] Enable branch protection or a repository ruleset for `main`: require pull requests, required CI checks, block force-push and deletion, and require review where practical.
- [ ] Add dependency and secret scanning appropriate to the repository and enable private vulnerability reporting if available.
- [ ] Scan the complete Git history, all branches, tags, issues, PRs, workflow logs and artifacts for secrets and personal/confidential data. A current-tree scan is insufficient.
- [ ] If any credential is found, revoke/rotate it first, then remediate history with a documented impact assessment.
- [ ] Pin third-party GitHub Actions to full commit SHAs; review permissions and set least-privilege workflow token permissions.
- [ ] Define CODEOWNERS/review ownership and a release approval procedure.

### B. Protocol and verifier correctness

- [ ] Independently review the normative specification against every implementation and test vector.
- [ ] Verify canonical JSON rules for Unicode, escaping, number representation, duplicate keys, invalid UTF-8, BOMs, trailing data and parser differentials.
- [ ] Verify exact byte-level hash inputs, schema closure, unknown-field handling, timestamp parsing and size/depth/resource limits.
- [ ] Add adversarial tests for truncated files, oversized/deep JSON, duplicate keys, malformed Unicode, numeric edge cases, path traversal and symlink handling where files are read.
- [ ] Confirm errors fail closed and produce stable machine-readable results without leaking sensitive data.
- [ ] Confirm no implementation reports stronger claims than the protocol actually verifies.

### C. Cross-language interoperability

- [ ] Add normative shared vectors consumed by Python and TypeScript.
- [ ] Require both SDKs to produce identical canonical bytes, hashes, validation outcomes and error categories.
- [ ] Resolve the documented TypeScript limitation: parsed-object APIs cannot detect duplicate JSON keys after ordinary `JSON.parse`; provide a safe file-parsing entry point or make the limitation explicit in every relevant API.
- [ ] Test supported Node/Python versions and lock dependencies reproducibly.
- [ ] Publish SDKs only after versioning, compatibility policy and release automation are reviewed.

### D. Cryptographic trust extensions

- [ ] Treat Ed25519 signatures as proof of possession of a key, not real-world identity.
- [ ] Specify key identifiers, key distribution, rotation, revocation, compromise response and algorithm agility.
- [ ] Require independently trusted key material; never trust a key merely because it is included in the evidence bundle.
- [ ] For event chains, document checkpoint custody and demonstrate detection of truncation/reordering relative to an independently retained checkpoint.
- [ ] Do not claim trusted time until RFC 3161 token validation, trust-anchor management and adversarial vectors exist.
- [ ] Obtain independent cryptographic/protocol review before stable release.

### E. Architecture, privacy and product boundaries

- [ ] Keep Core offline-verifiable and vendor-neutral.
- [ ] Define the boundary between Core, Trade extensions, commercial modules and any future hosted analysis service.
- [ ] Minimise personal data in evidence bundles; document data classification, retention, deletion and export.
- [ ] Threat-model uploads, parsers, browser demos, APIs, tenant isolation, logs and backups before any hosted service launches.
- [ ] State clearly that Cord does not by itself prove truth, authorship, identity, model execution, physical authenticity, legal title, payment finality, delivery or regulatory compliance.

### F. Commercial, IP and legal controls

- [ ] Confirm asset-by-asset chain of title, contributor assignments and third-party licence compatibility.
- [ ] Keep Apache-2.0 Core rights intact; do not impose commercial royalties or KentPH attribution on Core-only use.
- [ ] Identify the actual legal licensor before granting commercial or trademark rights.
- [ ] Obtain trademark clearance and jurisdiction-specific advice before licensing CORD/KENTPH marks.
- [ ] Keep UAE royalty term sheets explicitly non-binding until counsel review, signed schedules, tax treatment and reporting controls are complete.
- [ ] Do not promise zero legal liability or imply Cord is a payment operator, certification body or regulated trust-service provider.

### G. Documentation, branding and release hygiene

- [ ] Align repository description, README, specification, roadmap, SECURITY and trademark policy around one accurate product definition.
- [ ] Separate normative requirements from examples, proposals and future roadmap items.
- [ ] Label experimental features consistently and document unsupported claims and limitations.
- [ ] Replace logo assets only after correct binary assets, dimensions, contrast, favicon/social variants and README references are verified.
- [ ] Remove or retain donation addresses only by an explicit maintainer decision; check QR images match the published addresses.
- [ ] Publish release notes, checksums, source tag, supported versions, test results and known limitations.

## 3. Merge order and dependency policy

Do not merge the open PR stack blindly. Review each diff and its base/head relationship first. Resolve the technical dependency chain (#2 before #3), then the commercial architecture/licensing stack (#4/#5/#6/#7/#8) only after reconciling overlapping documents and confirming legal boundaries. A green CI run is necessary but not sufficient.

## 4. Acceptance criteria for a stable release

A stable release requires all of the following evidence:

1. Required CI checks pass from a clean checkout.
2. Python and TypeScript implementations pass the same normative and adversarial vectors.
3. Independent implementation/interoperability review is documented.
4. Threat model and external security review are completed with findings closed or formally accepted.
5. Branch protection, secret scanning, dependency controls and release permissions are enabled and tested.
6. Legal/IP ownership and public licence statements are verified by qualified advisers.
7. Privacy and operational controls are implemented for any hosted service.
8. Release artefacts are reproducible, checksummed and accompanied by an accurate security statement.

Until then, status remains **Experimental draft**.

## 5. Audit limitations

This initial triage reviewed repository metadata, the default-branch tree and README, selected security/trademark documents, open PR metadata and portions of PR patches, plus recent CI run summaries. It did not execute code, inspect every source line, scan Git history or artifacts, perform fuzzing, test deployed services, validate legal ownership, or conduct an independent penetration test. No item may be marked complete solely because this register exists.
