# CORD Authenticated Change Events — Security Design Review v0.1

**Review status:** Internal architecture review completed; independent review still required.  
**Reviewed proposal:** `spec/AUTHENTICATED-CHANGE-EVENTS.md`  
**Maturity:** Design-only. No implementation or conformance claim.

## 1. Executive finding

The original design direction was sound but too permissive in three areas that could create circular trust or overstate what a hash chain proves:

1. It allowed policy/key-status events and checkpoint references to sit in the same event stream as ordinary dependency changes.
2. It did not define the checkpoint witness's independent observation boundary precisely enough.
3. It left canonicalization open, despite CORD already having multiple canonicalization profiles with different sorting semantics.

The revised proposal addresses these issues. It separates trust-policy governance and checkpoint receipts from ordinary dependency events, defines an independently pinned authorization policy, narrows the initial event types, and provisionally adopts RFC 8785 JCS for the new extension.

This is a design improvement, not a security certification. The remaining protocol decisions and implementation gates are listed below.

## 2. Circular-trust analysis

### Required trust-root direction

The verifier must obtain these inputs independently of the event package and event stream:

- trust-store digest and trusted public keys;
- issuer authorization-policy digest and policy rules;
- checkpoint-witness trust configuration;
- required checkpoint coverage and trusted-time policy.

The event's `issuer_key_id` is a lookup hint only. It must never select or introduce its own trusted public key. The event cannot add its signer to the trust store, authorize its own event type, alter the policy used to verify itself, or revoke a competing key.

Policy changes must be delivered through an authenticated administrative channel or signed by a separately configured policy authority. A key-status assertion inside an ordinary change event is not a revocation.

### Role separation

The design separates three capabilities:

- `change_event_issuer`: may attest to defined dependency-change event types and scopes;
- `checkpoint_witness`: may attest to observed stream heads;
- `trust_policy_authority`: may authorize changes to verifier-side trust/authorization policy.

One key may hold more than one capability only as an explicit local policy decision. Separate keys and operators are recommended to reduce common-mode compromise.

**Finding:** No circular trust is introduced if verifier-side trust material and authorization policy are pinned independently and event content cannot modify either. If a deployment loads its trust store or policy from the same untrusted package it is verifying, this guarantee does not hold.

## 3. Checkpoint and completeness analysis

A hash chain alone cannot detect full-chain replacement. A detached checkpoint can detect replacement after a trusted observed head, but it does not automatically prove that all real-world events were submitted.

The revised design therefore distinguishes:

- **chain consistency:** hashes and sequence links are internally valid;
- **checkpoint validity:** an independently trusted witness signed a particular stream head;
- **observation coverage:** the witness or independent source actually received or observed events over a defined interval;
- **real-world completeness:** all relevant changes were captured, which requires an independent source or operational process and cannot be inferred from cryptography alone.

A periodic checkpoint supplied by the producer can anchor a head but cannot prove that the producer did not omit an event before presenting that head. Omission detection requires an independent ingestion/observation path, such as a witness receiving events as they are committed, or an authoritative source emitting the changes.

A checkpoint MUST NOT be stored only beside the stream and then described as independent. Its witness key or publication channel must be configured independently. The witness's `issued_at` is still self-declared unless separately timestamped.

**Finding:** The protocol can provide tamper evidence relative to a trusted witness and declared observation boundary. It cannot claim complete real-world history from a producer-controlled log alone.

## 4. Canonicalization decision

The revised proposal provisionally adopts RFC 8785 JSON Canonicalization Scheme (JCS) for this extension.

This is deliberately separate from EVC v0.1 canonicalization. EVC sorts object keys by Unicode code point. JCS sorts property names by UTF-16 code units, as specified in RFC 8785. Implementations must not reuse the EVC canonicalizer for change events.

To reduce cross-runtime ambiguity:
- event and checkpoint bodies prohibit JSON number values;
- sequence numbers are canonical unsigned 64-bit decimal strings;
- Unicode strings are preserved exactly without normalization;
- duplicate property names, invalid Unicode, and malformed UTF-8 are rejected;
- array order remains significant;
- nested object properties use JCS sorting.

The event hash and detached Ed25519 signature use separate, versioned domain separators. The exact byte formulas are recorded in the proposal.

**External standard reference:** [RFC 8785 — JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785.html). Its I-JSON constraints include unique property names, valid Unicode, and IEEE-754-compatible numbers; its sorting uses UTF-16 code units. The v0.1 profile forbids JSON numbers in signed event/checkpoint bodies to avoid numeric precision ambiguity.

## 5. Threat coverage matrix

| Threat | Required control | Residual limitation |
|---|---|---|
| Event modified | Event hash + Ed25519 signature | A compromised authorized key can sign false content |
| Event reordered/deleted | Sequence + predecessor hash | Only detectable relative to a known head/checkpoint |
| Entire chain rewritten | Independently retained/witnessed checkpoint | Replacement before the first trusted checkpoint remains possible |
| Event replayed in another stream | Signed stream ID, subject, sequence, predecessor | Same-stream replay needs duplicate/sequence checks |
| Conflicting fork | Detect same stream/sequence with different hashes; fail closed | Unseen competing forks require witness/gossip observation |
| Unauthorized issuer | Independently pinned trust store and scope policy | Trust administrator or policy authority compromise |
| Self-authorized signer | Event cannot modify trust store or policy | Misconfigured verifier may still load untrusted policy |
| Key revoked/rotated | Separate trust governance and historical snapshots | Historical status may be INDETERMINATE without trusted time |
| Omitted real-world change | Independent source or event-ingestion witness | Cryptography alone cannot prove producer completeness |
| False dependency digest | Independent measurement/attestation where required | Signature authenticates assertion, not truth |
| Timestamp backdating | Trusted timestamp evidence separately validated | Producer `issued_at` is not trusted time |
| Parser/canonicalization ambiguity | Strict parser, JCS, shared positive/negative vectors | Requires independent cross-runtime validation |

## 6. Event-type scope

The initial event stream is restricted to:
- `DEPENDENCY_CHANGED`;
- `DEPENDENCY_ADDED`;
- `DEPENDENCY_REMOVED`.

Policy changes, key status/revocation, and checkpoint receipts are separate trust-governance or witness artifacts. This avoids allowing an ordinary dependency-change issuer to grant roles, change trust roots, revoke keys, or attest its own checkpoint.

For dependency transitions:
- ADDED: prior digest is absent/null; new digest is required;
- CHANGED: both prior and new digests are required and must differ;
- REMOVED: prior digest is required; new digest is absent/null.

The normative schema must make nullability and forbidden fields exact. No arbitrary free-form event text may replace the typed dependency identity and digest transition.

## 7. EVC integration boundary

The event verifier may produce a candidate current-state snapshot only when the selected policy's required conditions are satisfied:
- baseline snapshot and provenance are available;
- event chain has no unresolved gap or fork;
- issuer signatures and authorization pass;
- required checkpoint coverage is valid;
- event observation/completeness boundary is adequate for the use case.

If any required condition is missing, the current-state snapshot is INDETERMINATE. EVC then evaluates freshness against the candidate snapshot; it does not authenticate the event stream itself.

Historical EVC graphs and evaluations remain immutable. A new event or observation creates a new snapshot and evaluation record.

## 8. Remaining design gates before implementation

1. Freeze exact JSON field sets and event-specific required/forbidden fields.
2. Decide whether `payload` is needed at all in v0.1; prefer no generic extension object unless a concrete interoperable use case requires it.
3. Define stream genesis, stream ID generation, event ID format, sequence exhaustion, and authorized stream migration/recovery.
4. Freeze checkpoint signature envelope, witness observation protocol, checkpoint cadence/coverage semantics, and witness quorum policy.
5. Define authorization-policy schema and historical policy snapshot selection.
6. Define trusted-time integration for event signatures and witness receipts, without reusing the existing receipt-only RFC 3161 profile by assumption.
7. Publish cross-runtime positive/negative vectors, including RFC 8785 edge cases, signatures, replay, forks, missing events, checkpoint mismatch, and authorization failures.
8. Implement at least two independent runtimes and run the vectors byte-for-byte.
9. Obtain independent protocol and security review before interoperability or production claims.

## 9. Validation status

- Repository change is documentation-only.
- No runtime code, schema, or executable test vectors were added.
- No new test suite was run for this design-only revision.
- Existing EVC CI results are not evidence that this new extension is implemented or tested.
- No changes were made to CORD Core v0.1 or EVC v0.1 semantics.
- PR #23 remains a draft and is not merged.

**Review conclusion:** proceed to schema design only after the remaining gates are explicitly decided. Do not implement a verifier or market authenticated change history as complete until the independent observation, trust-policy, and checkpoint semantics are specified and tested.
