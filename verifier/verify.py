#!/usr/bin/env python3
"""Cord Core v0.1 reference verifier.

Checks bundle/receipt consistency and integrity only. It does not authenticate
the creator, prove trusted time, or prove that an AI model produced the event.
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

SPEC_VERSION = "0.1"
MAX_FILE_BYTES = 1_048_576
BUNDLE_FIELDS = {
    "spec_version", "model_id", "timestamp", "policy_id",
    "input_hash", "output_hash",
}
RECEIPT_FIELDS = {
    "spec_version", "bundle_hash", "bundle_file_hash", "created_at",
}
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class CordValidationError(ValueError):
    """Raised when a Cord evidence file is malformed or invalid."""


def _read_bounded(path: str | Path, label: str) -> bytes:
    """Read at most MAX_FILE_BYTES + 1, so oversized files are never fully loaded."""
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise CordValidationError(f"{label} exceeds {MAX_FILE_BYTES} bytes")
    return data


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CordValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise CordValidationError(f"invalid JSON constant: {value}")


def _load_json(data: bytes, label: str) -> dict[str, Any]:
    if len(data) > MAX_FILE_BYTES:
        raise CordValidationError(f"{label} exceeds {MAX_FILE_BYTES} bytes")
    if data.startswith(b"\xef\xbb\xbf"):
        raise CordValidationError(f"{label} MUST NOT contain a UTF-8 BOM")
    try:
        text = data.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise CordValidationError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CordValidationError(f"{label} must be a JSON object")
    return value


def _reject_surrogates(value: str, field: str) -> None:
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise CordValidationError(f"{field} must contain only Unicode scalar values")


def canonical_json(bundle: dict[str, Any]) -> bytes:
    """CORD-CJSON-1: code-point key order, compact UTF-8 JSON, no ASCII escaping."""
    try:
        return json.dumps(
            bundle,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        ).encode("utf-8")
    except (UnicodeEncodeError, ValueError) as exc:
        raise CordValidationError(f"bundle cannot be canonicalized as CORD-CJSON-1: {exc}") from exc


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_fields(obj: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(obj)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if extra:
            details.append("unexpected: " + ", ".join(extra))
        raise CordValidationError(f"{label} fields invalid ({'; '.join(details)})")
    for key, value in obj.items():
        if not isinstance(value, str):
            raise CordValidationError(f"{label}.{key} must be a string")
        _reject_surrogates(value, f"{label}.{key}")


def _validate_timestamp(value: str, field: str) -> None:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value):
        raise CordValidationError(f"{field} must be an RFC 3339 UTC timestamp ending in Z")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise CordValidationError(f"{field} is not a valid timestamp") from exc


def validate_bundle(bundle: dict[str, Any]) -> None:
    _validate_fields(bundle, BUNDLE_FIELDS, "bundle")
    if bundle["spec_version"] != SPEC_VERSION:
        raise CordValidationError("unsupported bundle spec_version")
    for field in ("model_id", "policy_id"):
        if not bundle[field] or bundle[field].strip() != bundle[field]:
            raise CordValidationError(f"bundle.{field} must be a non-empty trimmed string")
    _validate_timestamp(bundle["timestamp"], "bundle.timestamp")
    for field in ("input_hash", "output_hash"):
        if not HASH_RE.fullmatch(bundle[field]):
            raise CordValidationError(f"bundle.{field} must be a lowercase SHA-256 hex digest")


def validate_receipt(receipt: dict[str, Any]) -> None:
    _validate_fields(receipt, RECEIPT_FIELDS, "receipt")
    if receipt["spec_version"] != SPEC_VERSION:
        raise CordValidationError("unsupported receipt spec_version")
    for field in ("bundle_hash", "bundle_file_hash"):
        if not HASH_RE.fullmatch(receipt[field]):
            raise CordValidationError(f"receipt.{field} must be a lowercase SHA-256 hex digest")
    _validate_timestamp(receipt["created_at"], "receipt.created_at")


def create_receipt(bundle_path: str | Path, receipt_path: str | Path, created_at: str) -> dict[str, str]:
    bundle_bytes = _read_bounded(bundle_path, "bundle")
    bundle = _load_json(bundle_bytes, "bundle")
    validate_bundle(bundle)
    _validate_timestamp(created_at, "created_at")
    receipt = {
        "spec_version": SPEC_VERSION,
        "bundle_hash": sha256(canonical_json(bundle)),
        "bundle_file_hash": sha256(bundle_bytes),
        "created_at": created_at,
    }
    Path(receipt_path).write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return receipt


def verify_files(bundle_path: str | Path, receipt_path: str | Path) -> dict[str, Any]:
    bundle_bytes = _read_bounded(bundle_path, "bundle")
    receipt_bytes = _read_bounded(receipt_path, "receipt")
    bundle = _load_json(bundle_bytes, "bundle")
    receipt = _load_json(receipt_bytes, "receipt")
    validate_bundle(bundle)
    validate_receipt(receipt)

    actual_bundle_hash = sha256(canonical_json(bundle))
    actual_file_hash = sha256(bundle_bytes)
    checks = {
        "bundle_hash": actual_bundle_hash == receipt["bundle_hash"],
        "bundle_file_hash": actual_file_hash == receipt["bundle_file_hash"],
    }
    if not all(checks.values()):
        raise CordValidationError("hash mismatch: " + ", ".join(k for k, ok in checks.items() if not ok))
    return {
        "status": "PASS",
        "spec_version": SPEC_VERSION,
        "checks": checks,
        "meaning": "Bundle and receipt hashes match. This is an integrity check, not proof of identity or trusted time.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or verify Cord Core v0.1 evidence.")
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create", help="create a receipt for a valid bundle")
    create.add_argument("bundle")
    create.add_argument("receipt")
    create.add_argument("--created-at", required=True, help="UTC RFC 3339 timestamp, e.g. 2026-03-06T12:00:05Z")
    verify = sub.add_parser("verify", help="verify bundle and receipt")
    verify.add_argument("bundle")
    verify.add_argument("receipt")
    args = parser.parse_args()

    try:
        if args.command == "create":
            result = create_receipt(args.bundle, args.receipt, args.created_at)
            print(json.dumps({"status": "CREATED", "receipt": result}, indent=2))
        else:
            print(json.dumps(verify_files(args.bundle, args.receipt), indent=2))
        return 0
    except (OSError, CordValidationError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
