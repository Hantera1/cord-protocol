# CORD Trust Store Format

**Specification ID:** CORD-TRUST-STORE  
**Version:** 0.1  
**Status:** Draft specification  
**Normative scope:** Offline distribution and resolution of trusted public keys for CORD signature verification.

This specification defines a small, local trust-store document for resolving a CORD signature envelope's `key_id` to an explicitly trusted public key and deployment-assigned roles. It is designed to work offline. It does not define a global CORD identity authority, a public key directory, certificate validation, or automatic trust discovery.

## 1. Security model

A trust store is a trust input, not self-authenticating evidence. A verifier MUST receive it through an independently authenticated administrative channel or pin its exact SHA-256 digest through trusted configuration. A trust store MUST NOT become trusted merely because it is included beside an evidence package, downloaded from a URI in that package, or signed by a key that is not already trusted.

A key's presence in a trust store means that the verifier's operator has chosen to trust that public key for the listed purposes under the operator's policy. It does not independently prove the civil identity, legal status, competence, or authority of the key holder.

CORD Core and the existing Ed25519 Signed Receipt Extension remain unchanged. The trust store supplies the externally trusted key material and policy metadata needed by a verifier; it does not change what bytes the signature covers.

## 2. File format

A trust store MUST be a UTF-8 JSON object conforming to `schemas/trust-store-0.1.schema.json`.

The top-level object MUST contain exactly:

- `trust_store_version`: MUST be the string `0.1`.
- `store_id`: non-empty, trimmed, locally unique identifier for this trust-store configuration.
- `keys`: array of trusted key records.

Unknown fields MUST be rejected. Duplicate JSON keys, invalid UTF-8, a UTF-8 BOM, invalid JSON constants, and unpaired Unicode surrogates MUST be rejected. Implementations MUST impose a documented size and nesting limit.

The trust store is configuration. Its JSON serialization is not a signature format and MUST NOT be reserialized to infer trust. Pin the exact raw file bytes or distribute it through an authenticated administrative channel.

## 3. Key record

Each key record MUST contain exactly:

| Field | Type | Rule |
|---|---|---|
| `key_id` | string | Non-empty, trimmed, unique within this store |
| `algorithm` | string | MUST be `Ed25519` in version 0.1 |
| `public_key` | string | Base64 encoding of exactly 32 raw Ed25519 public-key bytes |
| `roles` | array of strings | One or more deployment-defined role identifiers; unique, non-empty, trimmed |
| `status` | string | `active`, `retired`, or `revoked` |
| `not_before` | string | Optional RFC 3339 UTC timestamp ending in `Z` |
| `not_after` | string | Optional RFC 3339 UTC timestamp ending in `Z` |
| `revoked_at` | string | Required when status is `revoked`; otherwise MUST be absent |
| `revocation_reason` | string | Optional operator-supplied reason; descriptive, not cryptographic evidence |

The interval, when both bounds exist, MUST satisfy `not_before < not_after`. A key record MUST NOT contain both `not_before` or `not_after` values that make the validity interval empty.

The public key MUST be decoded strictly. Invalid Base64, non-canonical Base64, or a decoded length other than 32 bytes MUST be rejected. The algorithm MUST NOT be inferred from key length or file extension.

Role names are deployment-defined identifiers, not a universal CORD role vocabulary. Examples include `manufacturer`, `authorized_service`, `independent_examiner`, and `carrier`. A verifier MUST compare roles against the exact role requirements of the selected application profile or local policy. A role string in a trust store does not by itself prove that a real-world organization has that role.

## 4. Resolution and verification

For an Ed25519 signed-receipt envelope, a trust-aware verifier MUST:

1. Validate the Core receipt and signature envelope using the applicable extension version.
2. Resolve `key_id` only within the explicitly configured trust store selected by the verifier's operator.
3. Require the envelope algorithm to match the trusted key record's algorithm.
4. Verify the signature using the public key from the trusted record, never a key supplied only by the evidence package.
5. Apply the deployment's key status, validity, role, and revocation policy.
6. Report cryptographic signature validity separately from key trust, role authorization, and time validity.

An unknown key ID, duplicate key ID, unsupported algorithm, malformed public key, or failed signature MUST NOT produce a trusted-signature PASS.

## 5. Time and historical verification

The `created_at` value in a Core receipt is producer-declared time. It is not proof of when the receipt was signed. A signature over a receipt does not add trusted time.

A verifier MUST NOT use an untrusted receipt timestamp as proof that a signature was created before `not_after` or `revoked_at`.

Without independently validated trusted timestamp evidence, a verifier MAY report that the signature is cryptographically valid under a key currently present in the configured trust store, but MUST report historical key validity as `INDETERMINATE` when the result depends on when the signature was created.

A deployment MAY adopt a stricter policy, including rejecting all signatures made with a currently revoked key. Such policy MUST be explicit and MUST be reported. A deployment MUST NOT silently reinterpret a revoked key as historically trusted or historically untrusted without adequate time evidence and a documented revocation policy.

Trusted timestamp evidence, certificate path validation, revocation-status protocols, and historical validation policy are outside the scope of Trust Store v0.1.

## 6. Key lifecycle

The trust store records an operator's current view of key status. It is not an append-only key history and does not itself prove when a change was made.

- **active:** the key is currently configured for verification, subject to validity bounds and local policy.
- **retired:** the key is no longer intended for new signing. Historical verification requires adequate trusted time evidence and an explicit policy.
- **revoked:** the operator has withdrawn trust in the key. The reason and effective handling are determined by local policy; the field `revoked_at` is an operator assertion, not trusted time evidence.

Key rotation SHOULD use a new `key_id` and a new key pair. A key ID MUST NOT be reassigned to different key material within the same trust-store history. Private keys SHOULD be generated and held using an appropriately protected key-management system. Private keys MUST NOT be included in a trust store or evidence package.

Updates to trust stores SHOULD be version-controlled or otherwise auditable by the operator. Deployments SHOULD retain prior trust-store snapshots and their exact digests to support reproducible historical investigations.

## 7. Result model

A trust-aware verifier MUST report at least these checks independently:

- `signature_validity`: whether the signature mathematically verifies over the specified receipt bytes;
- `key_resolution`: whether the key ID resolved to the configured trusted key record;
- `key_status`: active, retired, revoked, or unknown;
- `role_authorization`: whether the key has the role required by the selected policy;
- `historical_key_validity`: `PASS`, `FAIL`, `UNSUPPORTED`, or `INDETERMINATE`;
- `trust_store_id` and the pinned trust-store digest used.

A successful signature check MUST NOT be collapsed into a global PASS when required role authorization or historical validity is indeterminate or failed.

## 8. Privacy and operational requirements

Trust stores SHOULD contain only public keys and the minimum metadata required for verification. They SHOULD NOT contain private keys, personal contact details, unnecessary identity documents, or sensitive employee data.

Deployments MUST protect trust-store updates as security-sensitive administrative changes. They SHOULD require review, preserve audit history, and distribute pinned versions to verifiers through authenticated channels.

## 9. Versioning and compatibility

Trust Store versioning is independent of Core, Signed Receipt Extension, Profile Manifest, and application-profile versions. Version 0.1 supports Ed25519 only. Unsupported versions and algorithms MUST be reported as `UNSUPPORTED`; implementations MUST NOT guess.

Future versions may add additional key types, signed trust-list publication, delegation, or certificate references. Such features MUST define their own trust model, downgrade behavior, and conformance vectors.

## 10. Limitations and non-goals

Trust Store v0.1 does NOT provide:

- a public or global identity registry;
- proof of legal identity or organizational authority;
- automatic trust in a key supplied with an evidence package;
- key generation, secure storage, hardware security module integration, or private-key custody;
- signed trust-list publication or transparency logging;
- certificate path validation or online revocation checks;
- trusted timestamping or historical proof of signing time;
- proof that signed claims are true.

**Status:** draft specification. A schema is provided, but no production trust-store resolver, lifecycle manager, or conformance suite is claimed by this document.
