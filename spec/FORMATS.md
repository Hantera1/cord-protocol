# Cord Core Formats (v0.1)

This document defines the minimal evidence package formats used by Cord.

Cord verification uses two files:

- `bundle.json` — the canonical description of an AI event
- `receipt.json` — binds the bundle to cryptographic hashes

Together these files allow **offline deterministic verification**.

---

# 1. Encoding

## 1.1 JSON Encoding

All Cord objects MUST be encoded as JSON.

Files are expected to use:

- UTF-8 encoding
- standard JSON formatting

---

## 1.2 Canonical JSON (CJSON)

When hashing JSON objects, implementations MUST canonicalize JSON.

Canonicalization rules:

- UTF-8 encoding
- object keys sorted lexicographically
- no insignificant whitespace
- no trailing commas
- numbers encoded using standard JSON number encoding
- strings encoded using standard JSON escaping rules

The canonicalization procedure MUST be identical across implementations.

This ensures that the same object always produces the same hash.

---

# 2. Cord Core Bundle

## 2.1 Purpose

The Cord Core Bundle is the canonical representation of an AI event within the Cord protocol.

An AI event represents the generation of model output from a defined input under a specific policy and model configuration.

The Cord Core Bundle defines the minimal set of fields required to describe a verifiable AI event.

Cord does **not** require storing raw input or output, only their hashes.

---

## 2.2 Required Fields

Implementations MUST produce a bundle object containing exactly the following fields:

- `spec_version`
- `model_id`
- `timestamp`
- `policy_id`
- `input_hash`
- `output_hash`

No additional fields are permitted in the Cord Core Bundle.

---

## 2.3 Canonical Structure

A valid Cord Core Bundle MUST follow this structure:

```json
{
  "spec_version": "0.1",
  "model_id": "...",
  "timestamp": "...",
  "policy_id": "...",
  "input_hash": "...",
  "output_hash": "..."
}
```

Field names are case-sensitive and MUST appear exactly as defined above.

---

## 2.4 Field Definitions

**spec_version**  
Version of the Cord Core specification used to generate the bundle.

**model_id**  
Identifier of the AI model that produced the output.

**timestamp**  
Timestamp representing when the AI event occurred.  
This value SHOULD be encoded using ISO-8601 in UTC.

**policy_id**  
Identifier of the policy, configuration, or execution context under which the model operated.

**input_hash**  
SHA-256 hash of the canonicalized model input.

**output_hash**  
SHA-256 hash of the generated model output.

---

## 2.5 Determinism Requirements

The Cord Core Bundle MUST be treated as a canonical object.

Implementations:

- MUST include exactly the defined fields
- MUST NOT include additional fields in the core bundle
- MUST ensure deterministic serialization before hashing

Any additional metadata MUST be stored outside the Cord Core Bundle and MUST NOT influence bundle hashing.

---

## 2.6 Bundle Hash Definition

The bundle hash is defined as:

`SHA256(CanonicalJSON(bundle))`

Where `CanonicalJSON(bundle)` represents a deterministic JSON encoding with the following requirements:

- UTF-8 encoding
- lexicographically sorted object keys
- no insignificant whitespace
- deterministic numeric encoding

These requirements ensure identical hashes across independent implementations.

---

## 2.7 Design Rationale

The Cord Core Bundle is intentionally minimal in order to ensure:

- deterministic verification
- cross-implementation compatibility
- long-term auditability of AI events

The minimal structure reduces ambiguity and enables simple offline verification of AI event integrity.

---

## 2.8 Example Bundle

```json
{
  "spec_version": "0.1",
  "model_id": "demo-model",
  "timestamp": "2026-03-06T12:00:00Z",
  "policy_id": "cord-output-v0.1",
  "input_hash": "1111111111111111111111111111111111111111111111111111111111111111",
  "output_hash": "2222222222222222222222222222222222222222222222222222222222222222"
}
```

---

# 3. Cord Receipt

## 3.1 Purpose

The Cord Receipt binds the bundle to two cryptographic hashes:

1. `bundle_hash` — hash of the canonical bundle object
2. `bundle_file_hash` — hash of the exact bundle file bytes

This prevents both:

- structural tampering
- file formatting ambiguity

---

## 3.2 Required Fields

| Field | Type | Description |
|------|------|-------------|
| spec_version | string | Version of the Cord spec |
| bundle_hash | string | SHA-256 hash of canonical JSON bundle |
| bundle_file_hash | string | SHA-256 hash of the bundle file bytes |
| created_at | string | ISO-8601 timestamp |

---

## 3.3 Example Receipt

```json
{
  "spec_version": "0.1",
  "bundle_hash": "TO_BE_COMPUTED",
  "bundle_file_hash": "TO_BE_COMPUTED",
  "created_at": "2026-03-06T12:00:05Z"
}
```

---

# 4. Hash Definitions (Normative)

## 4.1 Hash Algorithm

All hashes MUST use **SHA-256**.

Hashes MUST be encoded as **lowercase hexadecimal strings**.

---

## 4.2 bundle_hash

`bundle_hash = SHA256(CanonicalJSON(bundle))`

---

## 4.3 bundle_file_hash

`bundle_file_hash = SHA256(bundle_file_bytes)`

Where `bundle_file_bytes` is the exact raw byte content of the bundle file.

---

# 5. Verification Procedure (Normative)

Given:

- `bundle.json`
- `receipt.json`

A verifier MUST:

1. parse `bundle.json`
2. parse `receipt.json`
3. canonicalize the bundle
4. compute `bundle_hash`
5. compute `bundle_file_hash`
6. compare with receipt values
7. ensure supported `spec_version`

If ALL checks pass:

**PASS (MATCH YES)**

Otherwise:

**FAIL (MATCH NO)**

Verification MUST be strictly binary.

---

# 6. Compatibility Notes

Future versions may introduce additional fields outside the Cord Core Bundle.

Verifiers SHOULD reject malformed core bundles that do not comply with the required structure.

Required verification checks MUST NOT be skipped.

---

# 7. Security Notes

`bundle_file_hash` prevents ambiguity caused by formatting differences.

Deterministic canonicalization is required for cross-implementation consistency.

Any change in bundle content or bytes MUST result in verification failure.

---

# 8. Signatures (Optional Future Extension)

Future versions of Cord may support cryptographic signatures over the bundle hash.

This would allow verifiers to confirm not only integrity, but also the identity of the signer that produced or attested the AI event.

In such a model, a signature layer may include:

- `signer_id`
- `signature`
- `signature_algorithm`

Signature support is not required in Cord Core v0.1.