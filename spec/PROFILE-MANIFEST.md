# CORD Application Profile Manifest and Verification Model

**Specification ID:** CORD-PROFILE-MANIFEST  
**Version:** 0.1  
**Status:** Proposed technical specification — draft  
**Normative scope:** Profile identification, version declaration, package layout, and common-verifier behavior.

This specification defines a common, machine-readable way to identify CORD application profiles and declare the evidence and verification rules they require. It is designed to let one CORD verifier discover and validate supported profiles without changing the semantics of CORD Core.

This is a draft specification. The reference verifier does not yet implement profile-manifest or profile-evidence verification.

## 1. Design goals

A conforming implementation of this specification is intended to:
- identify an application profile unambiguously;
- identify the exact profile version and specification;
- declare compatible CORD Core versions;
- declare required evidence schemas and extension dependencies;
- distinguish unsupported profiles from invalid evidence;
- run common package and integrity checks before profile-specific validation;
- report Core, package-integrity, extension, and profile results separately.

A manifest is descriptive and machine-readable. It is not, by itself, proof that an issuer is trusted, a claim is true, or a profile has been certified.

## 2. Separation from CORD Core

Application profile manifests and profile evidence MUST NOT be inserted as extra fields in the Core v0.1 bundle or receipt.

The Core v0.1 verifier MUST continue to accept only the exact fields defined in CORD Core Formats v0.1. Profile-aware verification is an additional layer that invokes Core verification and then performs profile-package and profile-specific checks.

A profile-aware PASS MUST NOT change or broaden the meaning of Core PASS.

## 3. Manifest file

The manifest file MUST be named `profile-manifest.json` in a CORD profile package.

The manifest MUST be a UTF-8 JSON object and MUST conform to the accompanying JSON Schema. Duplicate keys, invalid UTF-8, invalid JSON constants, and unsupported manifest versions MUST be rejected. Implementations SHOULD impose a documented size limit.

### 3.1 Required fields

| Field | Type | Meaning |
|---|---|---|
| `manifest_version` | string | Manifest format version; currently `0.1` |
| `profile_id` | string | Stable reverse-DNS identifier controlled by the profile publisher |
| `profile_version` | string | Exact profile version using SemVer 2.0.0 |
| `profile_name` | string | Human-readable profile name |
| `profile_status` | string | `draft`, `candidate`, or `stable` |
| `core_compatibility` | object | Supported Core version range |
| `specification_uri` | string | URI identifying the normative profile specification |
| `evidence_schema_uri` | string | URI identifying the JSON Schema for profile evidence |
| `evidence_media_type` | string | Media type of the profile evidence document |
| `verification` | object | Required common and profile-specific verification behavior |

### 3.2 Optional fields

- `publisher`: organization or project name; a declaration, not verified identity.
- `description`: short profile description.
- `required_extensions`: list of extension identifiers and exact supported versions.
- `supersedes`: previous profile version identifiers.
- `documentation_uri`: additional human-readable documentation.
- `security_considerations_uri`: profile threat model and security notes.

Unknown fields MUST be rejected in manifest version 0.1. A future manifest version may define extension points.

### 3.3 Identifier and version rules

- `profile_id` MUST be stable across compatible releases and MUST be controlled by the profile publisher.
- A profile version MUST be an exact SemVer 2.0.0 value. Ranges, wildcards, and floating tags MUST NOT be used as the package's selected profile version.
- The manifest version, profile version, Core version, and extension versions are independent version namespaces.
- A package MUST pin one exact profile version.
- A verifier MUST NOT silently substitute a newer profile version.
- A verifier MUST report an unknown profile or unsupported profile version as `UNSUPPORTED`, not as `PASS`.

## 4. Package layout

A profile-aware package using this specification MUST contain:

```text
package/
  bundle.json
  receipt.json
  profile-manifest.json
  profile-evidence.json
  profile-receipt.json
```

The Core files retain their existing Core v0.1 meanings. The three profile files are additional files and are not Core v0.1 fields.

### 4.1 Profile evidence

`profile-evidence.json` MUST conform to the exact evidence schema declared by the manifest. Its domain claims MUST identify their source, issuer role, and evidence type as required by the relevant profile.

A profile MUST NOT treat an unverified self-assertion as an independently established fact.

### 4.2 Profile receipt

`profile-receipt.json` commits to the exact profile manifest and profile evidence files. Version 0.1 uses this exact object:

| Field | Type | Meaning |
|---|---|---|
| `receipt_version` | string | MUST equal `0.1` |
| `profile_id` | string | Exact profile identifier from the manifest |
| `profile_version` | string | Exact profile version from the manifest |
| `manifest_file_hash` | string | SHA-256 of the exact raw manifest file bytes |
| `evidence_file_hash` | string | SHA-256 of the exact raw profile evidence file bytes |
| `created_at` | string | Producer-declared RFC 3339 UTC time ending in `Z` |

All hashes MUST be lowercase 64-character hexadecimal SHA-256 digests. `created_at` is a declaration and is not trusted time.

The profile receipt in version 0.1 is an integrity commitment, not a digital signature. Signatures and trusted timestamps require separately specified extensions.

### 4.3 Profile canonicalization

Version 0.1 uses exact raw-file SHA-256 commitments for the manifest and evidence files. Implementations MUST NOT rewrite, normalize, reserialize, or otherwise alter the bytes before checking these file hashes.

Profile-specific semantic validation MUST parse the original bytes as strict UTF-8 JSON, reject duplicate keys, and validate against the exact schema version identified by the manifest.

A future specification may add a canonical semantic digest, but MUST identify its canonicalization algorithm explicitly. Core CJSON-1 MUST NOT be reused for arbitrary nested profile evidence.

## 5. Common verifier processing model

A profile-aware verifier MUST perform the following stages in order:

1. **Package presence:** require all files mandated by the selected package format.
2. **Strict parsing:** parse Core and profile JSON with duplicate-key rejection and documented size limits.
3. **Core verification:** run the supported Core verifier without changing its rules.
4. **Manifest validation:** validate manifest version, exact schema, identifiers, status, and required fields.
5. **Profile selection:** resolve the exact `profile_id` and `profile_version` from locally supported profile definitions or an explicitly trusted profile catalog.
6. **Compatibility:** verify that the manifest's declared Core compatibility includes the package's Core version and that the verifier supports that combination.
7. **Package integrity:** compare exact raw manifest and evidence file hashes with the profile receipt; verify that receipt identifiers match the manifest.
8. **Extension checks:** run only explicitly supported and configured extensions; do not assume that a declared dependency has been verified.
9. **Profile validation:** validate evidence against the exact profile schema and apply the profile's normative rules.
10. **Result reporting:** report each layer independently, including unsupported or indeterminate checks.

A verifier MUST fail closed on malformed required data, hash mismatch, contradictory identifiers, unsupported required versions, or failed mandatory checks.

## 6. Result model

A profile-aware verifier MUST NOT collapse all checks into a single ambiguous boolean.

The overall package result MUST be one of:
- `PASS`: all mandatory checks for the requested verification scope passed;
- `FAIL`: one or more mandatory checks failed;
- `UNSUPPORTED`: the verifier does not support the required manifest, profile, Core, schema, or mandatory extension version;
- `INDETERMINATE`: a required trust or evidence decision cannot be reached from available evidence or configuration.

The result MUST include separate sections for:
- `core_integrity`;
- `profile_package_integrity`;
- `manifest_validation`;
- `extension_results`;
- `profile_validation`;
- `limitations`.

A top-level `PASS` means only that the checks required by the selected verification scope passed. It MUST NOT be displayed as proof of truth, physical authenticity, legal ownership, authorization, regulatory compliance, or trusted time unless the relevant independent evidence and trust checks were explicitly performed and separately reported.

## 7. Trust and profile distribution

A manifest's `publisher`, `profile_id`, and specification URI are declarations. They do not authenticate the publisher.

A deployment that relies on approved profiles MUST configure a trusted profile catalog or pin approved profile identifiers and versions through an authenticated mechanism. A downloaded manifest MUST NOT be trusted solely because it is reachable at the URI it declares.

Profile catalogs SHOULD support:
- publisher identity and authenticated publication;
- immutable versioned manifest and schema references;
- profile status and deprecation notices;
- integrity digests for published artifacts;
- revocation or withdrawal notices;
- offline export for independent verification.

The Core verifier MUST remain usable without a CORD-hosted catalog. Local profile definitions and explicitly configured trust stores MUST be supported.

## 8. Versioning and lifecycle

- Manifest format versioning is independent of profile versioning.
- Each profile version MUST have immutable normative specification and schema artifacts.
- A published profile version MUST NOT be silently edited in place.
- Corrections that alter validation outcomes require a new profile version.
- A profile may move through `draft`, `candidate`, and `stable` statuses, but status alone does not prove maturity.
- A profile marked `stable` MUST have normative schemas, test vectors, reference verifier support, documented security limitations, and interoperability evidence.
- Deprecated or withdrawn profiles MUST remain identifiable for historical verification; verifiers MUST report their status and applicable policy.

## 9. Security requirements

Implementations MUST consider:
- manifest substitution and profile downgrade;
- schema substitution and remote schema retrieval risks;
- maliciously large or deeply nested JSON;
- duplicate keys and parser differentials;
- unsupported or ambiguous versions;
- profile ID spoofing and untrusted publisher claims;
- package file replacement;
- malicious evidence content and parser vulnerabilities;
- privacy leakage through evidence and identifiers.

A verifier SHOULD use locally pinned schemas or an authenticated profile catalog. It MUST NOT fetch and execute arbitrary code referenced by a manifest. Schema and specification URIs are identifiers/references, not instructions to execute.

## 10. Conformance levels

Implementations SHOULD identify which level they support:

- **Core-only verifier:** verifies Core v0.1 only; ignores no Core rules and makes no profile claim.
- **Manifest-aware verifier:** validates the manifest and package commitments but does not claim domain-profile conformance unless it also performs profile validation.
- **Profile-aware verifier:** validates Core, profile package, manifest, schema, and supported profile rules.
- **Trust-aware profile verifier:** additionally validates configured signatures, issuer trust, timestamps, revocation, and other required trust extensions.

A verifier MUST clearly identify its conformance level and supported profile/version matrix.

## 11. Initial profile registration

The following identifiers are proposed for CORD-maintained profiles. They are reserved identifiers, not evidence of implementation or external registration.

| Profile | Proposed profile ID | Initial version | Status |
|---|---|---:|---|
| Luxury Asset Verification | `org.cordprotocol.profile.luxury-asset` | `0.1.0` | draft |
| Clock Verification | `org.cordprotocol.profile.clock` | `0.1.0` | draft |

A profile's own manifest MUST use the identifier and version selected by its normative profile specification. Changes to these identifiers require an explicit migration decision.

## 12. Implementation plan

Before this specification is marked implemented, the project MUST:
1. publish and validate the JSON Schema accompanying this document;
2. define immutable profile manifest and evidence fixtures for each initial profile;
3. implement strict manifest and profile-receipt parsing;
4. implement profile registry loading from local, pinned definitions;
5. implement the staged verifier pipeline and structured result model;
6. add positive, negative, downgrade, substitution, unsupported-version, and boundary tests;
7. publish conformance test vectors;
8. demonstrate that Core-only verification remains unchanged;
9. obtain independent implementation and security review.

**Current status:** the manifest specification and JSON Schema remain draft artifacts. The experimental Profile Engine and the initial Clock/Luxury Asset profile fixtures and validators are implemented on PR #13. Independent interoperability and security review, trust extensions, and release conformance evidence remain outstanding; the existing Core verifier remains unchanged.
