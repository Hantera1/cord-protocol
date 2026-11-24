# CORD Authenticated Change Events — Design Proposal v0.1

**Status:** Architecture/design proposal. Not yet a normative extension or implementation.
**Purpose:** Define the security boundary between a reported change, an authenticated change, an authorized change, and a change whose history is externally anchored.

This proposal is deliberately separate from CORD Core v0.1, EVC v0.1, Signed Receipt v0.1, Trust Store v0.1, and Event Chain v0.1. It connects those concepts without silently changing their semantics.

## 1. Problem statement

EVC v0.1 compares declared dependency digests with a supplied current-state snapshot. It can report that a declared dependency is stale, but it does not establish who supplied that snapshot or whether the source was authorized.

The existing Event Chain extension detects edits and reordering relative to a trusted chain head, but a hash chain alone can be rewritten in full. Signed Receipt authenticates a receipt relative to a trusted key. Trust Store resolves keys and deployment-assigned roles, but its current snapshot is operator configuration rather than an authenticated append-only history.

CORD therefore needs a distinct change-event layer that binds:
- what changed;
- which subject and dependency were affected;
- which issuer asserted the change;
- whether that issuer was trusted and authorized for that event type;
- where the event sits in a stream's history;
- whether the history is anchored outside the producer's control.

## 2. Non-goals and compatibility

This proposal MUST NOT:
- change CORD Core v0.1 fields, hashes, or PASS semantics;
- change EVC v0.1's freshness algorithm;
- treat a hash, signature, role string, or producer timestamp as proof that a real-world statement is true;
- treat a producer-controlled event log as tamper-proof;
- make a CORD-operated server, account, registry, or cloud service mandatory;
- infer revocation or trusted time from an ordinary change event.

The extension is optional and independently versioned. Core verification remains possible offline without it. An EVC result remains a freshness result; authenticated change-event results are additional, separately reported checks.

## 3. Threat model

The design must consider an attacker who can:
- alter, delete, reorder, duplicate, or fabricate events in a producer-controlled store;
- replace an entire event stream and recompute its hashes;
- replay a previously valid event into another stream or subject;
- sign with an untrusted, expired, retired, revoked, or wrong-role key;
- submit conflicting events for the same stream sequence;
- omit a change event or provide a false current-state snapshot;
- exploit ambiguous JSON parsing, duplicate keys, unknown fields, Unicode differences, or algorithm downgrade;
- control the evidence producer while not controlling the verifier's independently configured trust anchors or external witnesses.

The design cannot protect against compromise of every trust anchor, signer key, verifier, and independent checkpoint witness simultaneously. It must report which trust assumptions remain unverified.

## 4. Trust and verification layers

A verifier MUST keep these states distinct:

1. **REPORTED** — syntactically valid event data was received. No authenticity claim.
2. **CHAIN_CONSISTENT** — event hash and sequence linkage validate relative to the supplied predecessor or stream genesis. This does not prove the stream is complete or externally anchored.
3. **SIGNATURE_VALID** — the event signature verifies under the public key identified by the event.
4. **ISSUER_TRUSTED** — that key resolves from verifier-side trust configuration whose exact digest is independently pinned or delivered through an authenticated administrative channel.
5. **ISSUER_AUTHORIZED** — the trusted key is authorized by local policy for this subject, stream, event type, and scope.
6. **CHECKPOINTED** — a checkpoint covering this event is independently retained or witnessed, and its proof validates under the verifier's configured checkpoint policy.
7. **TIME_VALIDATED** — trusted time evidence is independently validated under a separately specified timestamp policy. Producer-declared time alone never qualifies.

These are separate checks, not a single ladder that may be collapsed without policy. For example, an event can have a valid signature but an unauthorized issuer; a chain can be internally consistent but not checkpointed.

A verifier MUST report each check as PASS, FAIL, INDETERMINATE, or UNSUPPORTED where applicable. Missing trust configuration, missing required checkpoints, or insufficient trusted-time evidence MUST NOT be silently treated as PASS.

## 5. Proposed event model

A normative schema must define exact fields, types, limits, and event-specific payloads. The proposed common event body is:

| Field | Purpose |
|---|---|
| `event_version` | Exact extension version, initially `0.1` |
| `stream_id` | Stable identifier for one ordered event stream |
| `event_id` | Unique event identifier within the stream |
| `sequence` | Monotonically increasing unsigned integer, starting at zero |
| `previous_event_hash` | Prior event hash; all-zero digest only for genesis |
| `event_type` | Enumerated event type |
| `subject_id` | Identifier of the assessed subject |
| `dependency_type` | Typed dependency affected, where applicable |
| `dependency_id` | Identifier of the affected dependency, where applicable |
| `before_sha256` | Previous declared dependency digest, where applicable |
| `after_sha256` | New declared dependency digest, where applicable |
| `issuer_key_id` | Key lookup hint; never a trust anchor by itself |
| `issued_at` | Producer-declared RFC 3339 UTC time; not trusted time |
| `payload` | Strict event-type-specific fields |

Initial event types should be narrowly scoped:
- `DEPENDENCY_CHANGED`
- `DEPENDENCY_ADDED`
- `DEPENDENCY_REMOVED`
- `POLICY_CHANGED`
- `KEY_STATUS_CHANGED` (only an assertion; it cannot itself establish key revocation authority)
- `CHECKPOINT_REFERENCE`

Unknown event types MUST be rejected as UNSUPPORTED. Unknown fields MUST be rejected. Event-specific required and forbidden fields MUST be explicit. A dependency-change event MUST identify both the prior and new digest when both are known; an unknown prior value must be represented explicitly as unknown, not fabricated.

The event MUST bind the subject, stream, sequence, event type, dependency identity, and digest transition into the signed content. A signature over only a free-form message is insufficient.

## 6. Canonicalization and cryptographic binding

The normative specification must choose one byte-exact canonicalization profile and publish cross-language vectors before implementation.

Proposed direction:
- strict UTF-8 JSON object parsing;
- reject BOM, duplicate object keys, invalid UTF-8, unpaired surrogates, non-finite numbers, unknown fields, and oversized/nested inputs;
- use RFC 8785 JSON Canonicalization Scheme (JCS) for the event body, with its number and string constraints stated explicitly;
- use domain-separated SHA-256 for the event hash;
- use Ed25519 for the initial signature profile, with algorithm identifiers explicit and no silent fallback.

Proposed formulas:

`event_hash = SHA256(UTF8("CORD-CHANGE-EVENT-HASH\\0v0.1\\0") || JCS(event_body))`

`signature = Ed25519.Sign(private_key, UTF8("CORD-CHANGE-EVENT-SIGNATURE\\0v0.1\\0") || raw_32_byte_event_hash)`

The detached signature envelope should contain exactly the version, algorithm, issuer key ID, and Base64 signature. The verifier MUST resolve the public key from independently configured trust material, never from the event package alone.

This is a design direction, not a finalized canonicalization decision. It must be validated against existing CORD canonicalization conventions and independent implementations before becoming normative.

## 7. Stream integrity, replay, and forks

A verifier MUST check:
- exact stream ID and subject binding;
- sequence continuity and predecessor hash;
- event hash recomputation;
- uniqueness of event IDs within the verified stream;
- no sequence reuse;
- expected predecessor or independently retained stream head where supplied.

A valid event from one stream MUST NOT be accepted as an event in another stream. Replaying an event with a different stream ID, subject, sequence, or predecessor must fail signature/hash binding.

Two different events claiming the same stream ID and sequence are a **fork/equivocation** condition. A verifier MUST report the conflict and MUST NOT choose one silently. Resolution requires an explicit policy and evidence from independent witnesses or an authorized recovery process.

A chain proves ordering and internal consistency only. It does not prove that no events were omitted, that the producer did not create a competing chain, or that the entire chain was not replaced.

## 8. External checkpoints and independent witnesses

To detect full-stream replacement, a verifier needs a trusted checkpoint obtained independently of the stream producer.

A checkpoint should bind at least:
- stream ID;
- sequence number;
- event hash at that sequence;
- checkpoint format/version;
- checkpoint issuer or witness identity;
- checkpoint time assertion, if any.

A checkpoint is trusted only when its witness key or publication channel is independently configured and verified. A checkpoint stored only beside the event stream is not independent.

The protocol should permit multiple independent witnesses and portable checkpoint receipts. Threshold requirements, witness discovery, transparency-log integration, and gossip/equivocation detection require a separate specification. No single CORD-operated witness should be mandatory.

## 9. Issuer authorization and key lifecycle

The Trust Store provides key resolution and role metadata, but a role string is only a local trust decision. The event verifier must apply policy to the exact combination of:
- trusted key ID and key material;
- issuer role;
- subject and stream scope;
- event type;
- effective policy version;
- key status and applicable time evidence.

A key authorized to sign receipts is not automatically authorized to report dependency changes, revoke another key, or issue checkpoints.

Key rotation must use a new key ID and key material. Historical verification must retain the relevant trust-store snapshots, exact digests, and policy versions. A current trust-store status cannot by itself prove the historical status of a key.

A `KEY_STATUS_CHANGED` event is only a signed assertion until validated under a separately defined authority and policy. Revocation requires an authorized revocation authority, explicit scope, reason semantics, effective-time rules, and trusted time or a clearly stated conservative policy. An ordinary dependency-change event MUST NOT imply revocation.

## 10. Time semantics

`issued_at` is self-declared and useful for display and diagnostics only. It MUST NOT establish event time, signing time, key validity at signing, or revocation ordering.

Trusted time must come from a separately validated timestamp authority or equivalent independent mechanism. If the event signature is timestamped, the timestamp token must cover the exact defined signature bytes and the verifier must validate the TSA chain, purpose, policy, and revocation requirements. The existing RFC 3161 profile is currently scoped to CORD Signed Receipt signatures; it must not be assumed to cover change-event signatures without an explicit extension.

When trusted time is absent and historical key status matters, the result is INDETERMINATE unless the verifier's explicit policy requires a conservative FAIL.

## 11. EVC integration

The event layer must not replace EVC's deterministic comparison.

Proposed processing sequence:
1. Verify event syntax, canonical hash, and stream linkage.
2. Verify signature against independently pinned trust material.
3. Apply issuer authorization policy.
4. Validate required external checkpoint and trusted-time evidence.
5. Derive a candidate current-state snapshot from authorized dependency-change events.
6. Compare that snapshot with the EVC graph and evaluate claim-scoped freshness.
7. Report EVC freshness separately from event authenticity, issuer authorization, checkpoint status, and time status.

A consumer MUST NOT mark a dependency as authoritatively changed solely because an unauthenticated event says so. If the event stream is incomplete or unanchored under the selected policy, the resulting current state may be INDETERMINATE.

The event stream must not silently mutate a historical EVC graph or overwrite an earlier evaluation. New observations produce new graph snapshots and new evaluation records.

## 12. Result model

At minimum, an integrated verifier should expose independent fields for:
- event parsing and version support;
- event hash validity;
- chain continuity;
- signature validity;
- trust-store pin validity;
- issuer key resolution and status;
- issuer authorization;
- replay/fork detection;
- checkpoint validity and coverage;
- trusted-time validity;
- EVC freshness result;
- overall policy result.

Overall PASS is permitted only when every check required by the selected policy passes. Any required failed check yields FAIL. Any required missing or unverifiable input yields INDETERMINATE. Unsupported algorithms or versions yield UNSUPPORTED. The policy and all input digests used to reach the result must be included in the verification record.

## 13. Privacy and operational boundaries

Events SHOULD contain identifiers and digests rather than raw prompts, personal data, source documents, secrets, private keys, or confidential payloads. A digest of low-entropy personal data is not anonymization. Evidence bytes should remain in access-controlled storage and be referenced by digest where appropriate.

Private keys MUST NOT be stored in event packages, repositories, logs, or public trust stores. Trust-store pins, checkpoint witness configuration, and authorization policies are security-sensitive verifier inputs.

## 14. Required work before implementation

No implementation should begin until the following design gates are closed:

1. **Protocol review:** finalize the event field set, event-type payloads, stream lifecycle, canonicalization profile, and exact signature coverage.
2. **Threat review:** review replay, fork, omission, full-chain replacement, compromised issuer, key rotation, revocation, checkpoint compromise, parser abuse, and downgrade behavior.
3. **Interoperability plan:** publish positive and negative vectors, including byte-exact canonicalization, Unicode, duplicate keys, malformed signatures, stream forks, replay, and checkpoint mismatch.
4. **Trust policy:** define role/scope authorization, trust-store snapshot retention, historical verification, trusted-time requirements, and conservative failure semantics.
5. **Compatibility review:** prove that Core v0.1, EVC v0.1, Signed Receipt, Trust Store, Event Chain, and existing API/profile work remain unchanged.
6. **Independent review:** obtain at least one independent implementation or protocol review before describing the extension as interoperable or production-ready.

## 15. Maturity statement

This document is a design proposal only. It defines no production-ready format, schema, implementation, or security guarantee. Its purpose is to settle architecture and security semantics before code is written.

**Design principle:** a change may be reported, recorded, cryptographically authenticated, authorized, and externally anchored. CORD must never treat these as interchangeable states.
