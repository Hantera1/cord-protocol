# Cord Core Formats (v0.1)

**Status: experimental draft.** This document defines the current interoperable Core profile. Implementations MUST follow the rules below exactly.

Cord Core uses two UTF-8 JSON files:

- `bundle.json`: a minimal description of an AI event.
- `receipt.json`: cryptographic commitments to the parsed bundle and the exact bundle file bytes.

Core verification is an integrity-consistency check. It does not authenticate the creator, establish trusted time, or prove that a declared model generated the output.

## 1. JSON and canonicalization

### 1.1 Input encoding

Both files MUST be UTF-8 JSON objects. UTF-8 BOMs, invalid UTF-8, duplicate object keys, non-object top-level values, NaN, and Infinity MUST be rejected. Implementations SHOULD impose a file-size limit; the reference verifier limits each file to 1 MiB.

### 1.2 CORD-CJSON-1

For v0.1, canonicalization is defined only for the fixed Core objects below. Every field value is a string; numbers, booleans, arrays, and nested objects are not permitted.

To produce CORD-CJSON-1 bytes:

1. Parse the JSON object while rejecting duplicate keys.
2. Validate its exact field set and value types.
3. Serialize the object with keys sorted in ascending Unicode code-point order.
4. Encode as UTF-8 without a BOM.
5. Use no insignificant whitespace: no spaces after commas or colons.
6. Use JSON string escaping; do not escape non-ASCII characters solely for ASCII compatibility. Escape quotation marks, reverse solidus, and control characters as required by JSON.
7. Do not append a newline to the canonical bytes.

Implementations MUST NOT canonicalize arbitrary extension objects as part of Core v0.1. Future versions may adopt a separately specified general canonicalization standard.

## 2. Core Bundle

A valid bundle MUST contain exactly these six fields and no others:

| Field | Type | Requirement |
|---|---|---|
| `spec_version` | string | MUST equal `0.1` |
| `model_id` | string | Non-empty, trimmed identifier declared by the producer |
| `timestamp` | string | RFC 3339 UTC timestamp ending in `Z` |
| `policy_id` | string | Non-empty, trimmed policy/configuration identifier |
| `input_hash` | string | 64-character lowercase hexadecimal SHA-256 digest |
| `output_hash` | string | 64-character lowercase hexadecimal SHA-256 digest |

The timestamp is a producer-declared time, not a trusted timestamp.

### 2.1 Input and output hash scope

`input_hash` and `output_hash` are SHA-256 digests of the exact byte sequences selected by the integrating application for the input and output, respectively. The application MUST document its serialization and encoding choices. Cord Core does not prescribe or retain the raw input/output bytes.

If the input or output is JSON, an integration SHOULD define a deterministic serialization profile and identify that profile in its policy documentation. Different byte encodings produce different hashes.

## 3. Receipt

A valid receipt MUST contain exactly these four fields and no others:

| Field | Type | Requirement |
|---|---|---|
| `spec_version` | string | MUST equal `0.1` |
| `bundle_hash` | string | SHA-256 of CORD-CJSON-1 bytes for the parsed bundle |
| `bundle_file_hash` | string | SHA-256 of the exact raw bytes in `bundle.json` |
| `created_at` | string | RFC 3339 UTC timestamp ending in `Z` |

Both hash fields MUST be 64-character lowercase hexadecimal strings.

`created_at` is self-declared by the receipt creator. It is not independently trusted or proof that the receipt existed at that time.

## 4. Hash algorithms

The only Core v0.1 hash algorithm is SHA-256.

- `bundle_hash = SHA256(CORD-CJSON-1(bundle))`
- `bundle_file_hash = SHA256(exact_bundle_file_bytes)`
- `input_hash = SHA256(application_defined_input_bytes)`
- `output_hash = SHA256(application_defined_output_bytes)`

All digests are lowercase hexadecimal strings.

## 5. Receipt creation

A producer MUST:

1. Create a bundle containing exactly the six required fields.
2. Validate the bundle.
3. Serialize the bundle as a UTF-8 JSON file.
4. Compute `bundle_hash` from CORD-CJSON-1 bytes.
5. Compute `bundle_file_hash` from the exact bytes written to disk.
6. Create a receipt with the required fields and a UTC `created_at` value.

A receipt is a set of hash commitments, not a digital signature.

## 6. Verification

Given `bundle.json` and `receipt.json`, a verifier MUST:

1. Read both files as raw bytes and reject files above its documented size limit.
2. Decode strict UTF-8 and parse JSON, rejecting duplicate keys and invalid constants.
3. Require JSON objects with exactly the defined fields.
4. Validate all field types, supported versions, timestamp syntax, and hash encodings.
5. Compute the bundle hash from CORD-CJSON-1 bytes.
6. Compute the bundle file hash from the exact raw bundle bytes.
7. Compare both computed digests with the receipt.
8. Return PASS only if every required check succeeds; otherwise return FAIL.

A verifier MUST NOT silently repair malformed input or ignore unknown Core fields. Unsupported versions MUST fail closed.

## 7. Security properties and limitations

A PASS means only that the supplied bundle parses as a valid v0.1 Core bundle and that its two computed hashes match the supplied receipt.

Core v0.1 alone does NOT prove:
- who created the bundle or receipt;
- that the receipt is the original receipt;
- that a declared model actually generated the output;
- that the declared timestamp is accurate or trusted;
- that input/output content is true, safe, lawful, complete, or policy-compliant;
- that no events were omitted.

An attacker able to replace both bundle and receipt can create a new internally consistent pair. To establish signer identity or protect a receipt against replacement, use a separately specified signature/attestation extension with trusted key distribution and revocation. To establish trusted time, use a separately specified timestamping mechanism. These are not Core v0.1 features.

## 8. Compatibility

Core v0.1 is intentionally small. Optional metadata MUST NOT be added to the Core bundle or receipt. Extensions require their own versioned specification and MUST NOT change Core hash semantics.

A verifier that does not support a version MUST reject it rather than guess.

## 9. Example bundle

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
