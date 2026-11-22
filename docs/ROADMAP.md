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

- [ ] Harden the Python reference verifier.
- [ ] Provide a command-line interface with machine-readable output and clear exit codes.
- [ ] Add a bundle/receipt creation example.
- [ ] Add continuous integration for tests and formatting.
- [ ] Document reproducible local verification with no network access.

**Exit criteria:** a new developer can create, verify, tamper with, and reject a sample package using the documented commands.

## Stage 2 — Developer adoption

- [ ] Publish a Python SDK.
- [ ] Publish a JavaScript/TypeScript SDK.
- [ ] Provide integration examples for common AI application patterns.
- [ ] Add a public verifier demo that runs locally in the browser where practical.
- [ ] Add versioned API and extension documentation.

**Exit criteria:** external developers can integrate Cord without depending on a Cord-hosted service.

## Stage 3 — Trust extensions

- [ ] Specify signature profiles and key identification.
- [ ] Specify trusted timestamp evidence and its trust assumptions.
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
