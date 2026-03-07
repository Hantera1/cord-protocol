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
- Object keys sorted lexicographically
- No insignificant whitespace
- No trailing commas
- Numbers encoded using standard JSON number encoding
- Strings encoded using standard JSON escaping rules

The canonicalization procedure MUST be identical across implementations.

This ensures that the same object always produces the same hash.

---

# 2. Cord Bundle

## 2.1 Purpose

The Cord bundle is the canonical object describing an AI event.

It contains metadata needed to verify:

- which model produced the output
- when the event occurred
- which policy governed the output
- hashes of the input and output

Cord does **not require storing raw input or output**, only their hashes.

---

## 2.2 Required Fields

| Field | Type | Description |
|------|------|-------------|
| spec_version | string | Version of the Cord specification |
| model_id | string | Identifier of the AI model |
| timestamp | string | ISO-8601 timestamp |
| policy_id | string | Identifier of the policy used |
| input_hash | string | SHA-256 hash of the input |
| output_hash | string | SHA-256 hash of the output |

---

## 2.3 Optional Fields

| Field | Type | Description |
|------|------|-------------|
| meta | object | Non-security metadata |
| notes | string | Human readable notes |

Verifiers MUST ignore unknown fields.

---

## 2.4 Example Bundle

```json
{
  "spec_version": "0.1",
  "model_id": "demo-model",
  "timestamp": "2026-03-06T12:00:00Z",
  "policy_id": "cord-output-v0.1",
  "input_hash": "1111111111111111111111111111111111111111111111111111111111111111",
  "output_hash": "2222222222222222222222222222222222222222222222222222222222222222"
}## Cord Core Bundle

The Cord Core Bundle is the canonical representation of an AI event within the Cord protocol.

Implementations MUST produce a bundle object containing exactly the following fields:

- spec_version
- model_id
- timestamp
- policy_id
- input_hash
- output_hash

No additional fields are permitted in the core bundle.

---

## Canonical Structure

A valid Cord Core Bundle MUST follow this structure:

{
  "spec_version": "0.1",
  "model_id": "...",
  "timestamp": "...",
  "policy_id": "...",
  "input_hash": "...",
  "output_hash": "..."
}

Field names are case-sensitive and MUST appear exactly as defined above.

---

## Field Definitions

spec_version  
Version of the Cord Core specification used to generate the bundle.

model_id  
Identifier of the AI model that produced the output.

timestamp  
Timestamp representing when the AI event occurred.  
This value SHOULD be encoded using ISO-8601 in UTC.

policy_id  
Identifier of the policy, configuration, or execution context under which the model operated.

input_hash  
SHA-256 hash of the canonicalized model input.

output_hash  
SHA-256 hash of the generated model output.

---

## Determinism Requirements

The Cord Core Bundle MUST be treated as a canonical object.

Implementations:

- MUST include exactly the defined fields
- MUST NOT include additional fields in the core bundle
- MUST ensure deterministic serialization before hashing

Any additional metadata MUST be stored outside the Cord Core Bundle and MUST NOT influence bundle hashing.

---

## Bundle Hash Definition

The bundle hash is defined as:

SHA256(CanonicalJSON(bundle))

Where CanonicalJSON(bundle) represents a deterministic JSON encoding with the following requirements:

- UTF-8 encoding
- lexicographically sorted object keys
- no insignificant whitespace
- deterministic numeric encoding

These requirements ensure identical hashes across independent implementations.

---

## Design Rationale

The Cord Core Bundle is intentionally minimal in order to ensure:

- deterministic verification
- cross-implementation compatibility
- long-term auditability of AI events

The minimal structure reduces ambiguity and enables simple offline verification of AI event integrity.

---

## Signatures (Optional Future Extension)

Future versions of Cord may support cryptographic signatures over the bundle hash.

This would allow verifiers to confirm not only integrity, but also the identity of the signer that produced or attested the AI event.

In such a model, a signature layer may include:

- signer_id
- signature
- signature_algorithm

Signature support is not required in Cord Core v0.1.