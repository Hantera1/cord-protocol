# CORD Security-First Engineering Gates v0.1

**Status:** Proposed mandatory engineering and release policy.  
**Scope:** Every CORD specification, implementation, SDK, API, profile, agent, deployment, and integration.  
**Security objective:** Minimize attack surface, make trust assumptions explicit, fail safely, and prevent unsupported assurance claims. This policy does not claim that any system can be made perfectly secure.

## 1. Non-negotiable principles

1. **Security before feature velocity.** A component MUST NOT advance to integration or production merely because its happy-path tests pass.
2. **Zero Trust.** No input, producer, observer, issuer, signer, timestamp, model, tool, service, dependency, build artifact, or administrator is trusted by default.
3. **Fail closed, report uncertainty.** Missing, malformed, conflicting, stale, unauthenticated, or unsupported information MUST NOT be silently promoted to PASS, VALID, trusted, or complete.
4. **Separate assurance dimensions.** Integrity, authenticity, authorization, freshness, trusted time, observation, coverage, factual correctness, safety, and legal compliance MUST be reported separately.
5. **Independent verification.** A verifier MUST be able to validate evidence without trusting the producer's implementation or infrastructure beyond explicitly documented trust anchors.
6. **Least privilege and compartmentalization.** Components MUST receive only the permissions, secrets, data, and network access required for their function.
7. **Reproducibility and auditability.** Versioned inputs, policies, schemas, tools, builds, test vectors, and decisions MUST be identifiable and reproducible where technically feasible.
8. **Honest claims.** Documentation, UI, APIs, and marketing MUST state exactly what each result proves and does not prove.

## 2. Mandatory component security dossier

Before implementation is approved for integration, each component MUST have a version-controlled dossier containing:

- purpose, scope, non-goals, assets, trust boundaries, and data classification;
- threat model covering attacker capabilities, attack paths, abuse cases, and security assumptions;
- security invariants and explicit acceptance criteria;
- input/output schemas, size limits, nesting/depth limits, timeouts, resource limits, and parser behavior;
- cryptographic design, algorithm identifiers, domain separation, key custody, rotation, revocation, and trust-anchor distribution where applicable;
- authorization model and least-privilege requirements;
- replay, rollback, equivocation, omission, downgrade, and denial-of-service analysis where applicable;
- privacy, retention, deletion, and data-minimization requirements;
- failure-state semantics, including PASS, FAIL, INDETERMINATE, and UNSUPPORTED where appropriate;
- test strategy, adversarial cases, known limitations, residual risks, and review history.

A missing dossier is a release blocker.

## 3. Secure implementation requirements

### 3.1 Input handling

Implementations MUST:

- parse strictly and reject duplicate keys, invalid encodings, ambiguous representations, unknown fields where schemas are closed, and unsupported versions;
- impose documented byte, nesting-depth, collection-size, string-length, CPU, memory, and execution-time limits;
- reject malformed Unicode and non-finite numeric values where relevant;
- avoid unsafe deserialization, shell interpolation, path traversal, and implicit network fetching;
- return controlled errors without leaking secrets or sensitive internal state;
- test parser differentials across every supported runtime.

### 3.2 Cryptography and trust

Implementations MUST:

- use reviewed, standard cryptographic libraries and explicit algorithm/version identifiers;
- use domain separation for signatures and hashes across different message types;
- define exact bytes covered by every digest and signature;
- obtain trust anchors through independently authenticated or pinned channels;
- never trust a key, certificate, policy, timestamp authority, or trust-store update solely because the evidence package supplies it;
- define key generation, protected storage, rotation, compromise response, revocation, and historical validation;
- prevent algorithm downgrade and ambiguous canonicalization;
- distinguish cryptographic validity from identity, authority, factual truth, and trusted time.

Custom cryptographic primitives and custom general-purpose canonicalization schemes are prohibited unless an approved design review demonstrates necessity and provides independent interoperability vectors.

### 3.3 Runtime and supply chain

Builds MUST be reproducible where feasible and MUST pin or constrain dependencies. CI MUST detect vulnerable dependencies and secret exposure. Release artifacts MUST identify source revision, build process, dependency set, and verification results. Signing keys MUST NOT be exposed to untrusted build jobs. Production secrets MUST NOT be stored in source control.

### 3.4 Service and agent boundaries

Network-facing services and agents MUST authenticate and authorize each privileged operation, enforce tenant/data boundaries, validate tool outputs as untrusted input, and apply rate, size, and execution limits. Agent instructions or retrieved content MUST NOT override system policy or grant permissions. High-impact actions require explicit policy authorization and auditable approval.

## 4. Evidence and observation requirements

CORD MUST keep these questions distinct:

- Were the supplied bytes preserved? (integrity)
- Who signed or issued them, under which key? (authenticity)
- Was that issuer authorized for this claim and scope? (authorization)
- Was the evidence current at a trusted evaluation time? (freshness and time)
- Was the relevant source actually observed by an independent observer? (observation)
- What source, interval, event types, and population were covered? (coverage)
- What could have been omitted, blocked, delayed, or falsified? (completeness limits)
- Does the evidence support the factual claim? (claim assessment)

A hash chain alone MUST NOT be described as proof that no events were omitted or that a complete history exists. Periodic checkpoints MUST state their observation boundary and cannot prove events that the witness never received. Silence or missing telemetry MUST be represented as a gap or INDETERMINATE state, never as proof that nothing happened.

Proof-of-Observation designs MUST define independent observation, source authentication, coverage contracts, sequence/gap handling, witness independence, checkpoint policy, equivocation handling, and failure-domain assumptions before normative implementation.

## 5. Mandatory verification and adversarial testing

Every component MUST have:

- positive and negative unit tests;
- malformed-input and boundary tests;
- adversarial tests derived from its threat model;
- property-based or fuzz testing for parsers and complex state machines where feasible;
- cross-runtime conformance vectors for multi-language implementations;
- regression tests for every confirmed security defect;
- tests proving that uncertainty, missing trust, unsupported algorithms, and policy conflicts cannot yield an unjustified success result.

Security-sensitive changes MUST run the full relevant repository suite. CI success is necessary but is not an independent security audit.

## 6. Review gates

A component advances only after the applicable gates are recorded:

| Gate | Required evidence |
|---|---|
| G0 — Scope | Purpose, non-goals, assets, trust boundaries |
| G1 — Threat model | Abuse cases, attacker model, residual risks |
| G2 — Design | Security invariants, schemas, trust and failure semantics |
| G3 — Implementation | Hardened code, bounded resources, least privilege |
| G4 — Verification | Negative tests, fuzz/property tests, conformance and regression tests |
| G5 — Independent review | Reviewer not responsible for the implementation; findings dispositioned |
| G6 — Release | Versioned artifacts, operational controls, rollback and incident plan |

A gate MUST be marked **PASS**, **FAIL**, or **NOT APPLICABLE with rationale**. Unknown or incomplete evidence is **NOT PASSED**. No gate may be waived by a green happy-path CI run.

## 7. Release classification

- **Experimental:** may be evaluated in isolated environments; limitations and missing gates are prominent.
- **Preview:** design and implementation gates are complete for the stated scope; independent review and deployment controls may still be outstanding.
- **Production candidate:** all applicable gates, independent security review, operational readiness, incident response, and rollback evidence are complete.
- **Production:** release owner has accepted residual risk in writing and all mandatory release criteria are met.

No CORD component may be described as certified, fully secure, tamper-proof, complete, or proof of truth unless a separately defined and independently substantiated standard supports that exact claim.

## 8. Vulnerability handling and security response

Security reports MUST have a private reporting path, severity triage, affected-version analysis, remediation owner, regression test, and coordinated disclosure process. Critical vulnerabilities MUST block releases and trigger assessment of previously issued evidence and affected deployments. Key compromise requires a documented revocation, replacement, and historical-impact procedure.

## 9. Exceptions

Exceptions MUST be narrow, time-limited, documented with rationale and compensating controls, assigned an owner, and approved by the designated security reviewer and release owner. An exception MUST NOT convert an unknown or failed security property into PASS. Core protocol semantics MUST NOT be weakened silently for convenience or compatibility.

## 10. Current project application

This policy is a proposed engineering gate, not a statement that current CORD components already satisfy it.

Before advancing the current roadmap:

1. Audit Core v0.1, Signed Receipt, Trust Store, RFC 3161 timestamp handling, Event Chain, EVC, Verify API, Profile Engine, and all open proposals against this policy.
2. Reproduce and resolve parser, Unicode, resource-exhaustion, cryptographic, key-lifecycle, authorization, replay, rollback, fork, omission, and coverage risks.
3. Keep EVC freshness separate from authenticity and observation.
4. Freeze Proof-of-Observation requirements and trust boundaries before implementing a verifier.
5. Require independent review and cross-runtime/adversarial conformance before production claims.

**Status note:** This document establishes proposed release gates. It does not itself implement security controls, certify existing code, or prove that CORD is secure.
