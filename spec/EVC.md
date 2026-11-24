# CORD Evidence Validity Calculus (EVC) v0.1

**Status:** Experimental prototype specification. Not a production trust framework, certification scheme, or independently audited standard.

## 1. Purpose

EVC evaluates whether a claim's declared evidence dependencies still match a supplied current-state snapshot. It is claim-scoped: a change should affect only claims that declare a dependency on the changed object. EVC preserves historical results and reports current applicability separately.

EVC is an optional extension. It MUST NOT change CORD Core PASS semantics.

## 2. Explicit scope boundary

The v0.1 prototype computes dependency freshness only. It does not verify evidence bytes, issuer identity, signatures, trusted timestamps, revocation authority, truth, safety, legal compliance, or completeness of dependency declarations. A \`VALID\` result means only that the declared dependencies match the supplied snapshot and that the claim references at least one evidence record.

The supplied current-state snapshot is an input, not an independently authenticated observation. Production deployments require a separately specified trust and attestation layer.

## 3. Graph document

The top-level JSON object MUST contain exactly:

- \`schema_version\`: \`cord-evc-0.1\`;
- \`graph_id\`: non-empty trimmed string;
- \`subject\`: object with exactly \`id\`, \`version\`, and \`sha256\`;
- \`current_state\`: array of current dependency observations;
- \`claims\`: array of assurance claims;
- \`evidence\`: array of evidence references;
- \`dependencies\`: array linking claims to dependency objects.

All identifiers and descriptive strings MUST be non-empty, trimmed strings. Leading or trailing whitespace is rejected using this explicit set: U+0009–U+000D, U+001C–U+0020, U+0085, U+00A0, U+1680, U+2000–U+200A, U+2028–U+2029, U+202F, U+205F, and U+3000. SHA-256 values MUST be 64 lowercase hexadecimal characters. Duplicate IDs, duplicate state keys, duplicate dependency triples, unknown references, unknown dependency types, and unknown object fields MUST be rejected.

### 3.1 Subject

\`subject\` identifies the assessed system. Its digest is a declared subject digest; v0.1 does not independently derive it from a deployed system.

### 3.2 Evidence

Each evidence record has exactly \`id\`, \`kind\`, and \`sha256\`. The digest identifies the expected evidence bytes but those bytes are not included in the EVC graph and are not verified by the freshness evaluator.

Each claim MUST reference one or more known evidence IDs to be eligible for \`VALID\`.

### 3.3 Claims

Each claim has exactly \`id\`, \`statement\`, \`scope\`, and \`evidence_ids\`. A claim is a bounded proposition, not a general declaration that an AI system is safe or compliant.

### 3.4 Current state

Each current-state record has exactly \`type\`, \`object_id\`, and \`sha256\`. The pair \`(type, object_id)\` MUST be unique.

### 3.5 Dependencies

Each dependency has exactly \`claim_id\`, \`type\`, \`object_id\`, and \`expected_sha256\`. A claim may have multiple dependencies. The triple \`(claim_id, type, object_id)\` MUST be unique.

Supported dependency types:

\`SUBJECT_VERSION\`, \`MODEL_VERSION\`, \`CONFIGURATION\`, \`TOOL_PERMISSION\`, \`DATASET\`, \`TEST_PROFILE\`, \`VERIFIER_BUILD\`, \`TRUST_ANCHOR\`, \`SIGNING_KEY\`, \`TIMESTAMP_POLICY\`, \`EVIDENCE_ARTIFACT\`, \`REGULATORY_PROFILE\`.

Unknown types MUST fail closed. Each dependency must resolve to a current-state record for the same type and object ID.

## 4. Evaluation algorithm

For each claim:

1. Resolve its evidence references. Unknown evidence IDs make the graph invalid; an empty evidence list yields \`INDETERMINATE\`.
2. Resolve its declared dependencies.
3. If it declares no dependencies, return \`INDETERMINATE\`.
4. For each dependency, compare \`expected_sha256\` with the matching current-state \`sha256\`.
5. If any known dependency differs, return \`STALE\`.
6. If no dependency differs but at least one current-state record is missing, return \`INDETERMINATE\`.
7. Otherwise return \`VALID\`.

\`STALE\` takes precedence over \`INDETERMINATE\` when both a known change and a missing dependency exist. This communicates that at least one declared assumption is already known to have changed.

Overall graph status is \`STALE\` if any claim is stale; otherwise \`INDETERMINATE\` if there are no claims or any claim is indeterminate; otherwise \`VALID\`.

## 5. Deterministic graph digest

The graph digest is SHA-256 over UTF-8 JSON with object keys sorted in Unicode code-point order, no insignificant whitespace, non-ASCII characters emitted directly, and no trailing newline. The arrays \`claims\`, \`evidence\`, \`current_state\`, and \`dependencies\` are normalized by their stable identifiers before hashing. Array order therefore does not change the graph digest. The digest is an integrity identifier, not a signature or proof of origin.

## 6. Strict input parsing

The reference loader MUST reject invalid UTF-8, UTF-8 BOM, duplicate JSON object keys, NaN, Infinity, non-object top-level JSON, and inputs larger than 2 MiB. Unknown fields and unsupported versions MUST be rejected. Implementations MUST NOT silently repair input.

## 7. Result semantics

- \`VALID\`: all declared dependencies resolve and match; at least one evidence reference exists.
- \`STALE\`: at least one declared dependency differs from the supplied current-state snapshot.
- \`INDETERMINATE\`: evidence or dependency information is missing or insufficient.

The prototype does not emit \`REVOKED\`. Revocation requires an authenticated authority, signed revocation records, policy scope, and trusted evaluation-time semantics. It MUST NOT be inferred from an ordinary change event.

These statuses describe freshness, not test outcomes. A historical test can have outcome \`PASS\` while its claim is now \`STALE\`.

## 8. Historical preservation

An implementation MUST treat prior graph snapshots and receipts as immutable records. A later graph is a new snapshot with a new digest. It MUST NOT rewrite a historical result to make it appear that a later system version was tested earlier.

## 9. Security and production requirements

Before production use, a future revision must specify authenticated change events, issuer authorization, key rotation and revocation, trusted time, evidence-byte verification, provenance, dependency completeness, anti-replay controls, external checkpoints, and independent implementations. The prototype MUST NOT be marketed as an AI safety certification or proof of regulatory compliance.

## 10. Conformance

The repository contains independent Python and TypeScript evaluators plus shared cross-runtime vectors in `test-vectors/evc-conformance-0.1.json`. CI compiles the TypeScript implementation and compares complete result objects and graph digests against Python for each vector. It also tests array-order invariance and malformed JSON rejection in TypeScript. The suite currently runs 63 repository tests in total; this is implementation-level conformance evidence, not an independent security audit or proof of protocol completeness. Passing these tests is necessary but not sufficient for production conformance or security assurance.
