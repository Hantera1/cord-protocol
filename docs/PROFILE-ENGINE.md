# CORD Profile Engine — draft implementation

**Implementation:** `verifier/profile_engine.py`  
**Specification:** [CORD Application Profile Manifest 0.1](../spec/PROFILE-MANIFEST.md)  
**Status:** experimental reference implementation; not production-ready.

## What it does

The Profile Engine layers application-profile checks on top of the existing Core v0.1 verifier. It currently:

1. verifies `bundle.json` and `receipt.json` with the existing Core verifier;
2. validates `profile-manifest.json` against the repository's manifest JSON Schema;
3. resolves an exact profile ID and version from a local registry;
4. compares the package manifest byte-for-byte with the locally pinned manifest;
5. checks Core version compatibility;
6. validates the profile receipt's exact fields and SHA-256 commitments;
7. validates `profile-evidence.json` against the locally pinned JSON Schema;
8. applies profile-specific semantic consistency checks for the initial Clock and Luxury Asset profiles;
9. returns structured `PASS`, `FAIL`, or `UNSUPPORTED` results.

The implementation does not fetch remote schemas, trust publisher names, or execute code referenced by a manifest.

## Package layout

A package directory contains:

```text
package/
  bundle.json
  receipt.json
  profile-manifest.json
  profile-evidence.json
  profile-receipt.json
```

## Local registry

The verifier uses a locally managed `registry.json`:

```json
{
  "registry_version": "0.1",
  "profiles": {
    "org.example.profile.demo": {
      "0.1.0": {
        "manifest_path": "profiles/demo/manifest.json",
        "evidence_schema_path": "profiles/demo/evidence.schema.json"
      }
    }
  }
}
```

All paths are relative to the registry directory. Path traversal outside that directory is rejected. The registry, pinned manifests, and schemas are trust inputs and must be provisioned and protected by the operator. The package manifest must match the pinned manifest bytes exactly.

## Create a profile receipt

The helper creates an unsigned integrity receipt over the exact manifest and evidence bytes:

```python
from verifier.profile_engine import create_profile_receipt

create_profile_receipt(
    "package/profile-manifest.json",
    "package/profile-evidence.json",
    "package/profile-receipt.json",
    created_at="2026-11-22T12:00:00Z",
)
```

The timestamp is producer-declared, not trusted time. The profile receipt is not a digital signature.

## Verify a package

Install dependencies and run:

```bash
python -m pip install -r requirements.txt
python verifier/profile_engine.py ./package --registry ./trusted-profile-registry
```

Exit code `0` means the selected checks passed. Any non-PASS result returns exit code `1`.

## Initial profile implementations

The local registry in `profiles/registry.json` pins two draft profile versions:

- `org.cordprotocol.profile.luxury-asset@0.1.0`: asset identity metadata and typed evidence records for registration, authenticity assessment, condition, components, service, ownership assertions, transfers, valuation, custody, clock references, and disputes.
- `org.cordprotocol.profile.clock@0.1.0`: producer time claims, clock observations, timestamp-token references, and event-order records.

The engine also applies semantic consistency checks. Examples include unique evidence identifiers, examiner-role requirements for substantive authenticity assessments, distinct transfer parties, resolvable external timestamp references, digest-length consistency, and per-source sequence uniqueness.

These are data-consistency rules, not external trust checks. In particular, the Clock profile schema does not permit a token to be marked as successfully validated by this implementation. RFC 3161 signature/path/revocation validation is not implemented. The Luxury Asset profile does not establish that an object is genuine or that an ownership assertion is legally correct.

Build complete examples with `python examples/build_profile_packages.py` and verify them with the CLI. See [profile package examples](../examples/profile-packages/README.md).

## Current limitations

- The engine is an experimental draft implementation.
- The local registry is a trust input; registry authenticity and distribution are deployment responsibilities.
- Profile-specific semantic consistency checks are implemented for the two initial draft profiles; broader trust semantics remain outside this engine.
- Signature verification, issuer identity, authorization, trusted timestamps, revocation, and external checkpoints are not performed by this engine.
- The engine does not prove domain truth, physical authenticity, ownership, or regulatory compliance.
- Independent interoperability and security review have not been completed.

A Core-only verifier remains available and unchanged. Do not treat this engine as a production certification service.
