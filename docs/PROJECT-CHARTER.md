# Cord Project Charter

## Mission

Cord is an open, implementation-neutral protocol for creating and independently verifying cryptographic evidence about digital and AI-related events.

## What Cord guarantees

The Cord Core is designed to let an independent verifier check whether evidence files match the cryptographic commitments recorded in a receipt.

A successful integrity check does **not**, by itself, prove:
- that an AI model produced the output;
- that the declared model identity is truthful;
- that an event happened at the claimed time;
- that the input, output, or policy was correct, safe, lawful, or unbiased;
- that the person or system creating the evidence was authorized.

Those claims require separate, explicitly identified mechanisms such as signatures, trusted timestamps, identity systems, and external audits.

## Product principles

1. **Open core protocol.** Core formats and verification rules are public and usable by independent implementations.
2. **Offline verification.** A verifier must not need Cord-operated infrastructure or a network connection to check a complete evidence package.
3. **Vendor neutrality.** Cord must not require a particular AI provider, cloud, database, or programming language.
4. **Small stable core.** Optional capabilities belong in versioned extensions, not ad hoc changes to the core format.
5. **Evidence before claims.** Documentation and product interfaces must distinguish integrity, authenticity, identity, and trusted time.
6. **Interoperability first.** Normative rules require test vectors and independent implementation checks.
7. **Sustainable, transparent funding.** Donations and optional paid services may fund development, but must not change the meaning or validity of a Core proof.

## Architecture

- **Cord Core:** versioned bundle, receipt, canonicalization, hashing, and offline verification.
- **Extensions:** separately versioned signature, timestamp, provenance, and policy metadata profiles.
- **SDKs and adapters:** language libraries and integrations for AI frameworks and applications.
- **Optional hosted services:** APIs, managed evidence storage, dashboards, organization administration, and support. These services must not be required for Core verification.

## Governance and compatibility

- Changes to normative Core behavior require a documented proposal, review, updated test vectors, and a versioning decision.
- A verifier must reject unsupported major protocol versions rather than silently guessing.
- Existing released versions and test vectors must remain available.
- No extension may silently redefine the meaning of a Core field.
- Security-sensitive changes require review and regression tests before release.

## Project status

Cord v0.1 is an experimental draft. It must not be presented as a finalized standard or production security guarantee until the specification, verifier, test vectors, and independent interoperability checks are complete.
