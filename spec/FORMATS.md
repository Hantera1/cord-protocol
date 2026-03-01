# Cord Core Formats (Draft 0.1)

This document defines the minimal evidence package formats used by Cord Core:

- `AuditBundle` (the canonical evidence object)
- `AuditReceipt` (binds the bundle to its exact file bytes)

These formats are designed for offline, deterministic verification.

---

## 1. Encoding

### 1.1 JSON Encoding
All objects are encoded as JSON.

### 1.2 Canonical JSON (CJSON)
When hashing JSON objects, implementations MUST canonicalize JSON:

- UTF-8 encoding
- Object keys sorted lexicographically
- No insignificant whitespace
- No trailing commas
- Numbers encoded in a deterministic manner (use standard JSON number encoding)
- Strings encoded in standard JSON with escapes as required

**Note:** The canonicalization procedure MUST be identical across implementations.

---

## 2. AuditBundle

### 2.1 Purpose
`AuditBundle` is the canonical object that represents a verifiable snapshot of a Cord state.

### 2.2 Required Fields

| Field        | Type    | Description |
|-------------|---------|-------------|
| specVersion | string  | Version of the Cord Core spec used to produce this bundle. Example: `"0.1"` |
| cp_id       | string  | Policy identity hash (hex string). |
| cid         | string  | Current canonical state identifier (hex string). |
| height      | integer | Monotonic height of the state chain. |
| tip_commit  | string  | Current tip commit hash (hex string). |
| createdAt   | string  | ISO-8601 timestamp (UTC recommended). |

### 2.3 Optional Fields

| Field     | Type   | Description |
|----------|--------|-------------|
| meta     | object | Freeform metadata (non-security critical). |
| notes    | string | Human notes. |

### 2.4 Example (Minimal)

```json
{
  "specVersion": "0.1",
  "cp_id": "8f2c...ab",
  "cid": "a19d...5c",
  "height": 12,
  "tip_commit": "c3aa...91",
  "createdAt": "2026-03-01T12:00:00Z"
```

---

## 3. AuditReceipt

### 3.1 Purpose

`AuditReceipt` binds the AuditBundle to:

1) the canonical hash of the bundle object (`bundleHash`)
2) the hash of the exact bundle file bytes (`bundleFileHash`)

This enables strict offline integrity checking.

---

### 3.2 Required Fields

| Field          | Type   | Description |
|---------------|--------|-------------|
| specVersion    | string | Version of the Cord Core spec. Example: "0.1" |
| bundleHash     | string | SHA-256 hash of canonical JSON of the bundle. |
| bundleFileHash | string | SHA-256 hash of the exact bytes of the bundle file. |
| createdAt      | string | ISO-8601 timestamp. |

---

### 3.3 Example (Minimal)

```json
{
  "specVersion": "0.1",
  "bundleHash": "4c5b...e1",
  "bundleFileHash": "a7d1...09",
  "createdAt": "2026-03-01T12:00:05Z"
}
```

---

## 4. Hash Definitions (Normative)

### 4.1 Hash Algorithm

All hashes MUST use SHA-256.  
Output MUST be lowercase hexadecimal.

---

### 4.2 bundleHash

```
bundleHash = SHA256( CJSON(AuditBundle) )
```

Where `CJSON(x)` is the canonical JSON byte sequence of object `x`.

---

### 4.3 bundleFileHash

```
bundleFileHash = SHA256( bundle_file_bytes )
```

Where `bundle_file_bytes` is the exact raw byte content of the bundle file.

---

## 5. Verification Procedure (Normative)

Given:

- bundle.json (AuditBundle)
- receipt.json (AuditReceipt)

A verifier MUST:

1. Parse bundle.json
2. Parse receipt.json
3. Compute bundleHash'
4. Compute bundleFileHash'
5. Compare with receipt values
6. Ensure specVersion is supported

If ALL checks pass → PASS (MATCH YES)  
Otherwise → FAIL (MATCH NO)

Verification MUST be strictly binary.

---

## 6. Compatibility Notes

- Additional fields may be added in future versions.
- Verifiers SHOULD ignore unknown fields.
- Required hash checks MUST NOT be skipped.

---

## 7. Security Notes

- bundleFileHash prevents ambiguity in file formatting.
- Deterministic canonicalization is required.
- Any byte change MUST result in FAIL.