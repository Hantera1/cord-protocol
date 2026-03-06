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
}