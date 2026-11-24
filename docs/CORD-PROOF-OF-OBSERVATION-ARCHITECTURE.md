# CORD Proof-of-Observation — Research Architecture v0.1

**Status:** Research proposal; non-normative. No implementation or security claim.
**Purpose:** Define the boundary between an internally consistent event stream and a history whose coverage has been independently observed.
**Relationship:** Proposed layer above CORD Core, EVC, authenticated change events, and interoperable transparency services. Existing semantics remain unchanged.

## 1. Executive thesis

CORD should not compete by inventing another signature format or generic append-only log. Those are established building blocks.

The research target is a harder question:

> Given a declared system, event class, observation interval, and independently identified source boundary, what can a verifier prove about events that were expected, observed, omitted, delayed, contradicted, or outside the observation boundary?

The proposed capability is **Proof-of-Observation (PoO)**: a protocol for binding an explicit observation contract to evidence from one or more event sources, independent observers, and transparency witnesses, then reconciling those views into a verifiable coverage result.

The differentiator is not absolute completeness. It is a machine-verifiable, scope-bounded statement of coverage, including explicit proof gaps and residual assumptions.

## 2. Fundamental limitation

A producer-controlled log cannot prove that it contains every real-world event. A producer can omit an event before signing or logging it. Hash chains, signatures, Merkle inclusion proofs, and checkpoints authenticate the material presented; by themselves they do not establish that an external event occurred or that every relevant event was submitted.

CORD MUST NOT emit an unqualified claim such as “complete history” based only on a producer-controlled stream.

A completeness claim is meaningful only relative to:
- a defined subject and event predicate;
- a defined source or set of sources able to observe those events;
- a bounded interval or source epoch;
- an explicit collection/forwarding obligation;
- a known failure and independence model;
- a verifiable boundary marker (source sequence, cursor, epoch, watermark, or signed batch commitment);
- independently retained evidence that the observer covered that boundary.

If the authoritative source itself can silently omit events before exposing them, PoO cannot prove those events existed. The result must state that limitation.

## 3. Research hypotheses

**H1 — Coverage-bound reconciliation:** If an observation contract identifies a source that emits a verifiable, gap-detectable sequence or batch boundary, and an independently administered observer receives and commits to that sequence under a declared policy, then a verifier can distinguish producer-only history, observed history with verifiable coverage over the declared source boundary, detectable gaps/conflicts, and unestablished coverage.

**H2 — Multi-view equivocation detection:** If independently administered observers retain commitments for the same subject, source epoch, and coverage interval, incompatible views can be detected when commitments or proofs are compared. This does not guarantee detection if all observers collude, share a common compromised dependency, or never exchange views.

**H3 — Composable evidence:** Coverage proofs can travel with CORD evidence bundles and be checked offline. Online services are optional discovery/distribution mechanisms, not mandatory verification authorities.

These hypotheses require experiments and formal review. They are not established properties of the current CORD implementation.

## 4. Architecture

### 4.1 Observation Contract

A versioned, signed or independently pinned contract defines:
- contract ID and version;
- subject and environment identity;
- source identity and source-epoch semantics;
- event predicate and event classes in scope;
- observation interval or start/end boundary;
- expected source sequence, cursor, watermark, or batch-boundary semantics;
- required observers and their failure-domain declarations;
- forwarding and acknowledgement obligations;
- maximum permitted observation and publication delay;
- privacy classification and disclosure rules;
- coverage policy and minimum witness threshold;
- policy digest and effective interval.

The contract is an input to verification, not something the event producer can redefine retroactively. Contract updates require separately authorized policy governance and a new versioned effective boundary.

### 4.2 Source Evidence

A source adapter emits or exports evidence with as many of these properties as the source supports:
- stable source identifier;
- source epoch, boot, or generation identifier;
- monotonic sequence or cursor;
- event or batch commitment;
- predecessor commitment;
- source-authenticated boundary marker;
- source-declared event time, distinguished from trusted time;
- source adapter version and measurement method.

A source without a gap-detectable counter, cursor, or authoritative export boundary cannot support the strongest coverage profile. It may support weaker observation claims.

### 4.3 Independent Observer

An observer receives source evidence through a separately administered path and produces a signed observation receipt. The receipt binds:
- observation contract digest;
- source and source epoch;
- observed interval and boundary;
- first and last sequence/cursor where available;
- event or batch commitment;
- missing-range and conflict findings;
- observer identity and policy role;
- receipt sequence and predecessor;
- observer-declared time and any separately validated trusted-time evidence.

A different signing key does not, by itself, make an observer independent. Deployments must document administrative, infrastructure, software, credential, network, and operator failure domains.

The observer MUST distinguish **received**, **parsed**, **validated**, **durably committed**, and **forwarded to transparency service**. These are different events.

### 4.4 Transparency and witness layer

Observation receipts and relevant commitments may be registered with one or more transparency services. Reuse interoperable mechanisms where possible:
- SCITT Signed Statements and Receipts for transparent registration;
- RFC 9162-style Merkle inclusion and consistency proofs where applicable;
- Sigstore Rekor-compatible transparency evidence where useful;
- independent witnesses and checkpoint gossip to reduce split-view risk.

CORD should define portable evidence envelopes and policy semantics, not require one log operator or public network.

### 4.5 Reconciliation engine

The engine compares the producer event stream, source sequence/cursor or batch commitments, observer receipts, independent transparency receipts/checkpoints, contract-required coverage, policy, and trusted-time evidence.

It produces a deterministic result with machine-readable reasons and retained proof references. It MUST preserve each input and provenance rather than silently normalizing conflicting histories into one selected history.

## 5. Candidate evidence objects

These are conceptual objects, not frozen schemas.

**ObservationContract** — defines what is expected to be observed and under which policy.

**SourceBoundaryStatement** — a source- or source-adapter-authenticated statement binding a source epoch to a sequence/cursor/batch boundary. Its strength is limited by the source and adapter.

**ObservationReceipt** — a signed observer statement describing exactly what it received, checked, and committed to. It distinguishes receipt, parsing, validation, durable commitment, and transparency publication.

**CoverageProof** — a portable collection of the contract reference/digest, source boundary evidence, observer receipts, sequence/cursor continuity evidence, event/batch inclusion proofs, transparency receipts and consistency proofs, witness attestations, and explicit gaps/conflicts.

**ReconciliationResult** — a deterministic result containing coverage status, covered interval/boundaries, required and satisfied observer threshold, detected gaps/conflicts, unavailable evidence, trust/time sub-results, assumptions, policy digest, and verifier version.

## 6. Result model

PoO MUST NOT collapse integrity, authenticity, authorization, observation, and completeness into one PASS.

Proposed coverage statuses:

- **COVERAGE_VERIFIED:** all requirements of the selected observation contract are satisfied within the declared source boundary and trust assumptions.
- **COVERAGE_INCOMPLETE:** required ranges, receipts, boundaries, or observer acknowledgements are missing.
- **COVERAGE_CONFLICTED:** incompatible source or observer views, duplicate sequence claims, or conflicting commitments were found.
- **COVERAGE_UNATTESTED:** evidence exists but lacks required independent observation or trust.
- **COVERAGE_UNSUPPORTED:** the source lacks capabilities required by the selected coverage profile.
- **COVERAGE_INDETERMINATE:** available evidence cannot decide the required property.

COVERAGE_VERIFIED means verified relative to the contract and its source/observer model. It does NOT mean every real-world event was captured, that the source was honest, or that underlying assertions are true.

Report separately: content integrity, issuer authenticity, issuer authorization, source authentication, observer independence assessment, boundary continuity, transparency inclusion/consistency, trusted-time validation, and coverage status.

## 7. Threat model and limits

| Threat | Detection/control | Residual limitation |
|---|---|---|
| Producer edits an event | Hash/signature validation | Authorized compromised issuer can sign false data |
| Producer deletes a committed event | Sequence/cursor gap and external boundary | No detection if source never exposed a gap-detectable boundary |
| Producer rewrites whole history | Independently retained receipts/checkpoints | Rewrite before first external observation may remain undetected |
| Producer omits event before logging | Independent source/observer path | Cannot detect if every source and observer omits it |
| Observer presents conflicting views | Cross-observer commitment comparison and gossip | Unseen views or collusion may evade detection |
| Observer signs without durable storage | Operational controls, audit evidence, independent replication | Cryptography alone cannot prove durable storage |
| Source counter resets | Explicit source epoch/generation transition | Epoch authority must be trusted |
| Source adapter compromised | Reproducible adapter, measured deployment, independent adapter comparison | Attestation does not eliminate common-mode compromise |
| Witness collusion | Diverse operators and threshold policy | Threshold guarantees depend on independence assumptions |
| Timestamp backdating | Separate trusted timestamp validation | Producer/observer clocks are not trusted by default |
| Privacy leakage | Commitments, selective disclosure, batching | Metadata and timing can still leak information |

## 8. Independence model

“Independent” must be an explicit, reviewable property, not a marketing adjective.

A deployment profile should declare failure domains for legal/administrative control, cloud/account ownership, identity provider and key custody, network path, source software and adapter, storage and backup, operator personnel, and policy authority.

A threshold such as 2-of-3 is meaningful only if the three witnesses do not share the same relevant failure domain. CORD should support policy-defined thresholds and expose common-mode dependencies. It must not imply Byzantine fault tolerance without a specified protocol, synchrony assumptions, membership model, and adversary bound.

## 9. Formal properties to specify

Before implementation, define precise properties and counterexamples:

1. **Boundary soundness:** a verified coverage result identifies the exact source boundary it covers.
2. **Gap visibility:** any missing sequence/cursor range within a gap-detectable source epoch causes INCOMPLETE or CONFLICTED.
3. **No silent conflict resolution:** different commitments for the same source epoch and sequence remain visible as a conflict.
4. **Receipt binding:** every observer receipt binds contract digest, source epoch, covered boundary, and commitment.
5. **Policy non-circularity:** evidence under evaluation cannot authorize its own contract, trust roots, observer membership, or threshold policy.
6. **Offline reproducibility:** a verifier with the complete proof package and pinned policy reproduces the same result without contacting producer or CORD service.
7. **Monotonic coverage:** a later result may extend coverage but cannot silently rewrite an earlier verified interval or historical result.
8. **Explicit uncertainty:** absence of a required source capability or trust input cannot be treated as successful coverage.

Consider TLA+/PlusCal or another state-machine model for stream epochs, observer acknowledgements, forks, and policy transitions before choosing implementation details.

## 10. Relationship to existing standards and systems

CORD should reuse, profile, and interoperate rather than fork established cryptographic primitives.

- **IETF SCITT, RFC 9943:** architecture for signed statements, transparency services, receipts, and auditable histories. SCITT does not prevent dishonest issuers and recognizes selective non-submission by issuers. PoO's research question is how to bind a declared observation contract and independently observed source boundary to a coverage result.
- **RFC 9162 Certificate Transparency:** established Merkle inclusion and consistency proof model. It addresses log consistency, not whether an external producer submitted every event that should exist.
- **Sigstore Rekor:** practical transparency log design with inclusion/consistency proofs, checkpoints, and monitoring/witness concepts. CORD should compare evidence formats and witness assumptions before specifying a parallel mechanism.
- **in-toto / SLSA provenance:** relevant models for describing and verifying supply-chain steps and provenance. CORD should map its subject, predicate, signer, and attestation model against these ecosystems.
- **CORD Core and EVC:** retain current semantics. PoO may provide an authenticated, bounded current-state input to EVC, but must not redefine EVC VALID or Core PASS.

References:
- RFC 9943: https://www.rfc-editor.org/rfc/rfc9943.html
- RFC 9162: https://www.rfc-editor.org/rfc/rfc9162.html
- Sigstore Rekor overview: https://docs.sigstore.dev/logging/overview/
- Rekor architecture: https://github.com/sigstore/architecture-docs/blob/main/rekor-spec.md
- in-toto attestation: https://github.com/in-toto/attestation

This is a focused architecture comparison, not an exhaustive literature review, standards conformance assessment, or patent search. No claim of global novelty or freedom to operate is made.

## 11. Candidate differentiator to test

The candidate innovation is a **contract-bound, multi-source observation reconciliation protocol** that makes coverage claims depend on explicit source boundaries, observer receipts, and independent failure-domain policy.

Potential differentiating features:
- expected-event semantics are defined before observation, not inferred only from submitted logs;
- source epoch and monotonic boundary are bound to independently retained observer receipts;
- multiple observation paths can be reconciled without pretending they are independent when they share failure domains;
- coverage is a separate, scoped result with a proof package, not a boolean attached to a signature;
- gaps and conflicts are first-class outputs and cannot be hidden by selecting one convenient log;
- the evidence package remains portable and offline-verifiable.

This combination may overlap prior art. Search academic literature, standards, deployed systems, and patent claims before describing it as unique or making IP claims.

## 12. Experimental plan

### Phase A — adversarial model
Build a small formal state model with one producer, one authoritative source, two or three observers, one or more transparency logs, a policy authority, and a verifier with pinned policy.

Model omission before ingestion, deletion after ingestion, sequence reset, fork, split view, observer collusion, delayed receipts, policy rotation, and clock rollback.

### Phase B — reference simulator
Create a deterministic simulator generating complete source sequences, producer omissions, observer omissions, duplicate/conflicting events, sequence gaps and epoch resets, inconsistent log checkpoints, and independent/common-mode observer failures.

The simulator must report exactly which attacks are detectable under each contract and which are fundamentally undetectable.

### Phase C — proof format
Only after the model is stable, freeze JSON schemas and cryptographic envelopes. Prefer existing standard formats and algorithms. Any new commitment construction needs domain separation, versioning, strict parsing, and cross-runtime vectors.

### Phase D — two independent implementations
Implement Python and TypeScript independently. Require byte-identical commitments, identical reconciliation outcomes, malformed-input rejection, and deterministic negative vectors.

### Phase E — external review
Obtain protocol, cryptographic, distributed-systems, privacy, and legal/IP review before production or novelty claims.

## 13. Go/no-go criteria

Do not proceed to a normative PoO v0.1 protocol until:
- the observation boundary is defined for at least one real source class;
- formal properties and impossibility limits are documented;
- attacks are reproducible in the simulator;
- the proposed method offers measurable capability beyond SCITT/Rekor plus ordinary source logging;
- no existing standard is needlessly duplicated;
- privacy and operational costs are acceptable;
- independent implementations reproduce results;
- prior-art and patent review is completed.

If the approach does not outperform the baseline, do not force it into CORD. Retain useful interoperability work and abandon the claimed differentiator.

## 14. Immediate next decisions

1. Select the first source class: AI model deployment/configuration changes, inference/tool-call audit events, or AI supply-chain/build provenance.
2. Define what the authoritative source can expose: monotonic sequence, cursor, signed batch root, hardware-backed counter, or another verifiable boundary.
3. Define observer failure domains and required threshold.
4. Build the formal state model and attack simulator before choosing a final event schema.
5. Reassess PR #23 against the resulting architecture; do not merge it or claim it is the final event design.

**Current conclusion:** Proof-of-Observation is a research direction, not a proven unique invention. Its value will be established only if experiments demonstrate a precise, independently verifiable coverage guarantee that existing interoperable components do not already provide.
