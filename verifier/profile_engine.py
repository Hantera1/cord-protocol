"""CORD profile-aware verifier, draft implementation of CORD-PROFILE-MANIFEST 0.1.

The engine layers profile checks on top of the unchanged Core v0.1 verifier.
It uses a local, pinned profile registry; it never fetches schemas or executes
code from manifest-provided URIs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from verifier.verify import (
    CordValidationError,
    MAX_FILE_BYTES,
    verify_files,
)
from verifier.profile_semantics import ProfileSemanticError, validate_profile_semantics

MANIFEST_VERSION = "0.1"
PROFILE_RECEIPT_VERSION = "0.1"
PROFILE_RECEIPT_FIELDS = {
    "receipt_version", "profile_id", "profile_version",
    "manifest_file_hash", "evidence_file_hash", "created_at",
}
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
UTC_TIMESTAMP = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?Z$")


class ProfileVerificationError(ValueError):
    """Malformed or invalid profile package."""


class UnsupportedProfileError(ProfileVerificationError):
    """The local verifier does not support the requested profile/version."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProfileVerificationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ProfileVerificationError(f"cannot read {label}: {exc}") from exc
    if len(raw) > MAX_FILE_BYTES:
        raise ProfileVerificationError(f"{label} exceeds {MAX_FILE_BYTES} bytes")
    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=_unique_object,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ProfileVerificationError(f"invalid JSON constant: {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProfileVerificationError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ProfileVerificationError(f"{label} must be a JSON object")
    return value, raw


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _version_tuple(value: str) -> tuple[int, ...]:
    if not isinstance(value, str) or not re.fullmatch(r"(0|[1-9][0-9]*)([.](0|[1-9][0-9]*)){0,2}", value):
        raise ProfileVerificationError(f"invalid numeric version: {value!r}")
    parts = tuple(int(part) for part in value.split("."))
    return parts + (0,) * (3 - len(parts))


def _validate_utc_timestamp(value: str, field: str) -> None:
    if not isinstance(value, str) or not UTC_TIMESTAMP.fullmatch(value):
        raise ProfileVerificationError(f"{field} must be an RFC 3339 UTC timestamp ending in Z")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ProfileVerificationError(f"{field} is not a valid timestamp") from exc


def _safe_registry_file(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    base = root.resolve()
    if candidate != base and base not in candidate.parents:
        raise ProfileVerificationError("registry file path escapes registry directory")
    if not candidate.is_file():
        raise ProfileVerificationError(f"registry file does not exist: {relative}")
    return candidate


def _validate_schema(instance: Any, schema: dict[str, Any], label: str) -> None:
    try:
        Draft202012Validator.check_schema(schema)
        errors = sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
            key=lambda error: list(error.absolute_path),
        )
    except Exception as exc:
        raise ProfileVerificationError(f"{label} schema is invalid: {exc}") from exc
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path) or "$"
        raise ProfileVerificationError(f"{label} schema validation failed at {location}: {first.message}")


def create_profile_receipt(
    manifest_path: str | Path,
    evidence_path: str | Path,
    receipt_path: str | Path,
    *,
    created_at: str,
) -> dict[str, str]:
    """Create the unsigned profile integrity receipt defined by manifest v0.1."""
    manifest, manifest_raw = _load_json(Path(manifest_path), "profile-manifest.json")
    _, evidence_raw = _load_json(Path(evidence_path), "profile-evidence.json")
    if manifest.get("manifest_version") != MANIFEST_VERSION:
        raise UnsupportedProfileError("unsupported manifest_version")
    if not isinstance(manifest.get("profile_id"), str) or not isinstance(manifest.get("profile_version"), str):
        raise ProfileVerificationError("manifest profile_id and profile_version are required")
    _validate_utc_timestamp(created_at, "created_at")
    receipt = {
        "receipt_version": PROFILE_RECEIPT_VERSION,
        "profile_id": manifest["profile_id"],
        "profile_version": manifest["profile_version"],
        "manifest_file_hash": _sha256(manifest_raw),
        "evidence_file_hash": _sha256(evidence_raw),
        "created_at": created_at,
    }
    Path(receipt_path).write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + chr(10),
        encoding="utf-8",
    )
    return receipt


def verify_profile_package(
    package_dir: str | Path,
    registry_dir: str | Path,
    *,
    manifest_schema_path: str | Path | None = None,
) -> dict[str, Any]:
    """Verify Core files and a profile package against a locally pinned registry.

    Registry format:
      {
        "registry_version": "0.1",
        "profiles": {
          "<profile_id>": {
            "<profile_version>": {
              "manifest_path": "profiles/example/manifest.json",
              "evidence_schema_path": "profiles/example/evidence.schema.json"
            }
          }
        }
      }

    Paths are relative to registry_dir and cannot escape it. The registry and
    schema files are trusted local configuration and must be managed accordingly.
    """
    package = Path(package_dir)
    registry_root = Path(registry_dir).resolve()
    checks: dict[str, Any] = {
        "core_integrity": {"status": "NOT_RUN"},
        "profile_package_integrity": {"status": "NOT_RUN"},
        "manifest_validation": {"status": "NOT_RUN"},
        "profile_validation": {"status": "NOT_RUN"},
    }

    try:
        core = verify_files(package / "bundle.json", package / "receipt.json")
        checks["core_integrity"] = {"status": "PASS", "result": core}

        manifest, manifest_raw = _load_json(package / "profile-manifest.json", "profile-manifest.json")
        evidence, evidence_raw = _load_json(package / "profile-evidence.json", "profile-evidence.json")
        profile_receipt, _ = _load_json(package / "profile-receipt.json", "profile-receipt.json")

        if manifest_schema_path is None:
            manifest_schema = Path(__file__).resolve().parents[1] / "schemas" / "profile-manifest-0.1.schema.json"
        else:
            manifest_schema = Path(manifest_schema_path)
        schema_obj, _ = _load_json(manifest_schema, "profile manifest JSON Schema")
        _validate_schema(manifest, schema_obj, "profile manifest")
        checks["manifest_validation"] = {"status": "PASS"}

        if manifest.get("manifest_version") != MANIFEST_VERSION:
            raise UnsupportedProfileError("unsupported manifest format version")
        profile_id = manifest.get("profile_id")
        profile_version = manifest.get("profile_version")
        if not isinstance(profile_id, str) or not isinstance(profile_version, str):
            raise ProfileVerificationError("manifest profile_id/profile_version missing")

        registry, _ = _load_json(registry_root / "registry.json", "local profile registry")
        if registry.get("registry_version") != "0.1" or not isinstance(registry.get("profiles"), dict):
            raise ProfileVerificationError("local profile registry must use registry_version 0.1")
        profile_versions = registry["profiles"].get(profile_id)
        if not isinstance(profile_versions, dict) or profile_version not in profile_versions:
            raise UnsupportedProfileError(f"unsupported profile: {profile_id}@{profile_version}")
        entry = profile_versions[profile_version]
        if not isinstance(entry, dict):
            raise ProfileVerificationError("invalid local registry entry")

        manifest_relpath = entry.get("manifest_path")
        schema_relpath = entry.get("evidence_schema_path")
        if not isinstance(manifest_relpath, str) or not isinstance(schema_relpath, str):
            raise ProfileVerificationError("registry entry must contain string manifest_path and evidence_schema_path")
        pinned_manifest_path = _safe_registry_file(registry_root, manifest_relpath)
        pinned_manifest, pinned_manifest_raw = _load_json(pinned_manifest_path, "pinned profile manifest")
        if pinned_manifest_raw != manifest_raw:
            raise ProfileVerificationError("package manifest does not match locally pinned manifest bytes")
        if pinned_manifest.get("profile_id") != profile_id or pinned_manifest.get("profile_version") != profile_version:
            raise ProfileVerificationError("pinned manifest identity does not match registry key")

        core_version = core.get("spec_version")
        compatibility = manifest["core_compatibility"]
        min_core = _version_tuple(compatibility["min_version"])
        max_core = _version_tuple(compatibility["max_version"])
        actual_core = _version_tuple(core_version)
        if min_core > max_core or not (min_core <= actual_core <= max_core):
            raise UnsupportedProfileError(
                f"profile does not declare compatibility with Core {core_version}"
            )

        if manifest["profile_status"] == "draft":
            # Draft profiles can be tested locally, but this is made explicit in results.
            profile_status_note = "DRAFT_PROFILE_NOT_A_STABILITY_OR_CERTIFICATION_CLAIM"
        else:
            profile_status_note = None

        receipt_fields = set(profile_receipt)
        if receipt_fields != PROFILE_RECEIPT_FIELDS:
            raise ProfileVerificationError("profile receipt has missing or unexpected fields")
        for key, value in profile_receipt.items():
            if not isinstance(value, str):
                raise ProfileVerificationError(f"profile receipt {key} must be a string")
        if profile_receipt["receipt_version"] != PROFILE_RECEIPT_VERSION:
            raise UnsupportedProfileError("unsupported profile receipt version")
        if profile_receipt["profile_id"] != profile_id or profile_receipt["profile_version"] != profile_version:
            raise ProfileVerificationError("profile receipt identity does not match manifest")
        if not HEX_SHA256.fullmatch(profile_receipt["manifest_file_hash"]):
            raise ProfileVerificationError("invalid manifest_file_hash")
        if not HEX_SHA256.fullmatch(profile_receipt["evidence_file_hash"]):
            raise ProfileVerificationError("invalid evidence_file_hash")
        _validate_utc_timestamp(profile_receipt["created_at"], "profile receipt created_at")
        if _sha256(manifest_raw) != profile_receipt["manifest_file_hash"]:
            raise ProfileVerificationError("profile manifest file hash mismatch")
        if _sha256(evidence_raw) != profile_receipt["evidence_file_hash"]:
            raise ProfileVerificationError("profile evidence file hash mismatch")
        checks["profile_package_integrity"] = {"status": "PASS"}

        schema_path = _safe_registry_file(registry_root, schema_relpath)
        evidence_schema, _ = _load_json(schema_path, "pinned profile evidence schema")
        _validate_schema(evidence, evidence_schema, "profile evidence")
        validate_profile_semantics(profile_id, evidence)
        checks["profile_validation"] = {
            "status": "PASS",
            "profile_id": profile_id,
            "profile_version": profile_version,
            "profile_status": manifest["profile_status"],
            "note": profile_status_note,
        }
        return {
            "status": "PASS",
            "verifier": "CORD-PROFILE-ENGINE-0.1-draft",
            "checks": checks,
            "limitations": [
                "Profile receipts are unsigned integrity commitments, not signer authentication.",
                "The local registry is a trust input and must be provisioned securely.",
                "No trusted timestamp, issuer identity, authorization, or domain truth is inferred.",
                "Profile-specific semantic rules beyond JSON Schema are not yet implemented.",
                "A PASS does not certify the profile or prove the underlying claims.",
            ],
        }
    except UnsupportedProfileError as exc:
        return {
            "status": "UNSUPPORTED",
            "verifier": "CORD-PROFILE-ENGINE-0.1-draft",
            "checks": checks,
            "error": str(exc),
        }
    except (ProfileVerificationError, ProfileSemanticError, CordValidationError, OSError) as exc:
        return {
            "status": "FAIL",
            "verifier": "CORD-PROFILE-ENGINE-0.1-draft",
            "checks": checks,
            "error": str(exc),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a CORD Core and application-profile package.")
    parser.add_argument("package_dir", help="directory containing Core and profile package files")
    parser.add_argument("--registry", required=True, help="directory containing registry.json and pinned profile files")
    parser.add_argument("--manifest-schema", help="path to a trusted local manifest JSON Schema")
    args = parser.parse_args()
    result = verify_profile_package(
        args.package_dir,
        args.registry,
        manifest_schema_path=args.manifest_schema,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
