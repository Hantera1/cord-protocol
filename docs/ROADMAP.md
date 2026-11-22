# Cord Roadmap

This roadmap is a plan, not a claim that the listed capabilities already exist.

## Stage 0 — Establish a trustworthy baseline

- [ ] Inventory every current format, example, verifier, and test vector.
- [ ] Resolve field-name mismatches between the specification, verifier, and fixtures.
- [ ] Define exact canonical JSON behavior, including Unicode, numbers, duplicate keys, and invalid values.
- [ ] Define strict bundle and receipt schemas and timestamp rules.
- [ ] Replace placeholder hashes with independently reproducible test vectors.
- [ ] Add positive and negative verifier tests.
- [ ] Publish the security model and limitations.

**Exit criteria:** two independently written implementations produce the same results for every normative test vector.

## Stage 1 — Reliable Core implementation

- [x] Harden the Python reference verifier.
- [x] Provide a command-line interface with machine-readable output and clear exit codes.
- [ ] Add a bundle/receipt creation example.
- [x] Add continuous integration for tests (format/lint gate remains pending).
- [ ] Document reproducible local verification with no network access.

**Exit criteria:** a new developer can create, verify, tamper with, and reject a sample package using the documented commands.

## Stage 2 — Developer adoption

- [x] Add a minimal Python SDK helper (initial reference; packaging/release still pending).
- [ ] Publish a JavaScript/TypeScript SDK.
- [ ] Provide integration examples for common AI application patterns.
- [ ] Add a public verifier demo that runs locally in the browser where practical.
- [ ] Add versioned API and extension documentation.

**Exit criteria:** external developers can integrate Cord without depending on a Cord-hosted service.

## Stage 3 — Trust extensions

- [x] Specify an experimental Ed25519 signed-receipt profile and key identifier.
- [x] Draft an offline Trust Store v0.1 format and JSON Schema for pinned public keys and deployment-defined roles.
- [x] Implement strict offline trust-store parsing, raw-byte SHA-256 pinning, duplicate key-ID rejection, strict Ed25519 public-key decoding, and role/lifecycle policy evaluation (experimental Python reference).
- [x] Define fail-closed historical key validity and revocation results; without independently validated trusted time, return `INDETERMINATE`.
- [x] Specify experimental RFC 3161 timestamp profile binding TSA message imprint to exact Ed25519 signature bytes.
- [x] Add OpenSSL-backed RFC 3161 token, message-imprint, TSA-chain and timestamping-purpose verification (experimental reference; OCSP/CRL checks remain pending).
- [ ] Add independently generated interoperability fixtures and TSA revocation validation.
- [ ] Specify key rotation, revocation, and algorithm agility.
- [ ] Define provenance and policy metadata extensions.
- [ ] Add test vectors and threat analysis for every extension.

**Exit criteria:** extensions are independently verifiable and do not weaken or redefine Core.

## Stage 4 — Optional services and sustainability

- [ ] Offer a hosted verification API as a convenience, while preserving offline verification.
- [ ] Consider managed evidence storage with clear retention, export, and deletion controls.
- [ ] Consider organization audit dashboards and team administration.
- [ ] Add transparent donation and sponsorship information.
- [ ] Consider paid support or service-level agreements for businesses.

**Exit criteria:** paid services add convenience and operations, never exclusive access to the protocol or the ability to validate Core evidence.

## What we should not build first

- A proprietary token or blockchain requirement.
- A mandatory Cord account or cloud dependency.
- A large plugin marketplace before the Core is stable.
- Claims that a hash proves truth, authorship, model identity, or time.
- Multiple SDKs before one reference implementation and the test suite are reliable.

## Release gates

A release should identify:
- protocol version and status (draft, candidate, stable);
- supported verifier versions;
- test-vector version;
- known limitations and security considerations;
- backward-compatibility expectations.


## Current implementation status (2026-11-22)

Implemented on the work branch:
- Strict Python Core verifier and receipt creation CLI.
- Deterministic Core v0.1 specification and fixed test vector.
- GitHub Actions test workflow.
- Experimental Ed25519 detached receipt signatures verified against an externally trusted/pinned public key.
- Experimental receipt hash-chain helper with optional externally trusted head checkpoint.
- Minimal Python SDK helper and end-to-end example.

Not yet production-ready:
- No independent second-language implementation or interoperability vectors.
- No RFC 3161 timestamp-token verification or configured trust anchors.
- No key registry, rotation, revocation, or hardware-backed key custody.
- No hosted API, authentication, managed storage, or operational deployment.
- No independent security audit or formal protocol review.

Do not mark Cord stable or claim regulatory compliance until these release gates are met.


## Application profile reservation — Luxury Asset Verification

- [x] Add a proposed application-profile document for high-value physical assets, with luxury watches as the initial use case.
- [ ] Define normative profile manifest and evidence schemas (AssetIdentity, Authenticity, Condition, Components, Service, Ownership, Transfer, Custody, Valuation, Clock, and Dispute evidence).
- [ ] Define privacy-preserving identity and disclosure rules.
- [ ] Define issuer trust, examiner qualification, key lifecycle, and revocation policy.
- [ ] Integrate independently validated trusted timestamps; do not treat producer-declared time as trusted.
- [ ] Publish profile test vectors and implement a profile-aware verifier.
- [ ] Complete independent interoperability and security review.

**Status:** profile area documented only. This does not mean watch authentication, legal ownership verification, trusted timestamping, or a production registry has been implemented.


## Application portfolio reservation — CORD cross-industry scope

- [x] Record the cross-industry application portfolio and reserved use cases in `spec/APPLICATION-PORTFOLIO.md`.
- [x] Document the proposed Clock Verification application profile in `spec/CLOCK-VERIFICATION.md`.
- [x] Document the proposed Luxury Asset Verification application profile in `spec/LUXURY-ASSET-VERIFICATION.md`.
- [ ] Define normative schemas, manifests, trust policies, privacy rules, and test vectors for each profile before implementation.
- [ ] Implement and test profile-aware verification, beginning with Clock Verification and Luxury Asset Verification.
- [ ] Add further profiles for identity/key trust, provenance, AI events/agents, financial transactions, real estate, supply chain, and public-sector evidence as specified in the portfolio.

**Status:** use cases are reserved and profile drafts are documented. This is not a claim that all listed capabilities are implemented, interoperable, certified, or production-ready.


## Architecture governance — CORD Architecture Charter

- [x] Establish the project-wide Architecture Charter in `docs/PROJECT-CHARTER.md`.
- [x] Record the layered architecture: stable Core, trust/evidence extensions, application profiles, SDKs/integrations, and optional services.
- [x] Record cross-industry strategic scope and the maturity vocabulary used for all capability claims.
- [ ] Review the charter through public project feedback and adopt a stable charter version after review.
- [ ] Apply the charter's versioning, security, privacy, and release requirements to each normative profile and extension.

**Status:** Architecture Charter v1.0 draft committed. The charter governs project direction; individual technical specifications and implementation evidence govern conformance and maturity.


## Profile manifest and common verifier foundation

- [x] Define the proposed CORD application profile manifest and staged verification model in `spec/PROFILE-MANIFEST.md`.
- [x] Publish the draft JSON Schema at `schemas/profile-manifest-0.1.schema.json`.
- [ ] Publish immutable manifest/evidence fixtures for Clock Verification and Luxury Asset Verification.
- [ ] Implement strict manifest parsing, local pinned profile registry, profile receipt validation, and structured result reporting.
- [ ] Add profile-aware verification without changing Core v0.1 behavior.
- [ ] Publish conformance vectors and complete independent interoperability and security review.

**Status:** manifest specification and JSON Schema are draft artifacts. The current Python verifier remains Core-only; profile-aware verification is not implemented.
