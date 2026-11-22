# Cord Roadmap

This roadmap is a plan, not a claim that the listed capabilities already exist.

## Stage 0 — Establish a trustworthy baseline

- [x] Inventory Core formats, verifier, examples, and test vectors.
- [x] Define exact canonical JSON behavior and strict Core schemas.
- [x] Publish deterministic test vectors and positive/negative tests.
- [x] Publish the security model and limitations.

**Remaining exit criterion:** an independent implementation outside this repository reproduces the normative vectors and passes adversarial interoperability tests.

## Stage 1 — Reliable Core implementation

- [x] Harden the Python reference verifier and CLI.
- [x] Provide bundle/receipt creation and verification examples.
- [x] Add continuous integration for Python and TypeScript tests.
- [x] Document reproducible local verification.

## Stage 2 — Developer adoption

- [x] Add a minimal Python SDK helper.
- [x] Add an experimental TypeScript Core SDK and Node.js tests.
- [ ] Publish versioned SDK packages and compatibility guarantees.
- [ ] Add integration examples for common AI application patterns.
- [ ] Add a public verifier demo that runs locally in the browser where practical.

The TypeScript SDK accepts parsed objects and exact bundle bytes. A duplicate-key-rejecting JSON parser remains the caller's responsibility at the file boundary.

## Stage 3 — Trust extensions

- [x] Specify an experimental Ed25519 signed-receipt profile.
- [x] Implement signature verification against an externally pinned public key.
- [x] Implement an experimental receipt hash chain with optional trusted checkpoint.
- [ ] Specify and implement RFC 3161 timestamp-token verification and trust anchors.
- [ ] Define key rotation, revocation, algorithm agility, and key custody.
- [ ] Add test vectors and threat analysis for every trust extension.

## Stage 4 — Trade evidence extension (experimental)

- [x] Define a detached Trade evidence architecture without changing Core.
- [x] Define a versioned JSON Schema for business-event evidence.
- [x] Add Python schema validation helper and negative tests.
- [x] Add synthetic watch-sale and silver-lot examples.
- [ ] Add deterministic extension canonicalization test vectors and event-chain transition rules.
- [ ] Add TypeScript Trade validator and cross-language conformance tests.
- [ ] Add signed actor/provider attestations and timestamp-token verification.
- [ ] Add real payment, e-signature, logistics and assay adapters only after provider and legal review.

## Stage 5 — Optional services and sustainability

- [ ] Offer a hosted verification API as a convenience, while preserving offline verification.
- [ ] Define authentication, rate limits, abuse controls, privacy, retention, export, and deletion before accepting customer evidence.
- [ ] Deploy with infrastructure-as-code, monitoring, backups, incident response, and documented recovery.
- [ ] Consider managed evidence storage and organization audit dashboards.
- [ ] Consider paid support or service-level agreements for businesses.

## Architecture decision

Cord Core remains provider-neutral and offline-first. A hosted service is optional and must never be required to verify evidence. The first hosted deployment should be stateless and replaceable; evidence files should remain exportable and customer-controlled. Private signing keys must not be stored in application configuration or source control. Use a managed KMS/HSM when signing service keys are introduced. Trusted timestamps must be independently verifiable from RFC 3161 tokens and configured trust anchors.

Do not introduce a proprietary token, mandatory blockchain, mandatory account, or cloud dependency into Core.

## Release gates

A release must identify:
- protocol version and status (draft, candidate, stable);
- supported verifier and SDK versions;
- test-vector version and interoperability results;
- known limitations and security considerations;
- backward-compatibility expectations;
- independent review status.

## Current status

Core v0.1, Python reference verifier, Python helper, experimental TypeScript verifier helper, Ed25519 receipt signatures, and experimental receipt chain are implemented in the repository. CI covers Python and TypeScript. Cord remains an experimental draft, not a production security certification.

Production blockers:
- independent third-party implementation and formal protocol review;
- duplicate-key-rejecting TypeScript JSON file parser and cross-language canonicalization vectors;
- RFC 3161 token validation and trusted TSA roots;
- key registry, rotation, revocation, and hardware-backed custody;
- threat-model review, penetration testing, and operational controls;
- hosted API, authentication, privacy/retention policies, and monitored deployment.

Do not mark Cord stable or claim regulatory compliance until these release gates are met.
