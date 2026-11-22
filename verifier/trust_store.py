"""Pinned offline trust-store parsing and Ed25519 receipt verification.

The trust-store digest must be supplied from trusted local configuration.
This module does not authenticate identities or provide trusted time.
"""
from __future__ import annotations

import base64
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from verifier.signatures import verify_signed_receipt
from verifier.verify import (
    CordValidationError,
    _load_json,
    _read_bounded,
    _validate_timestamp,
)

STORE_FIELDS = {"trust_store_version", "store_id", "keys"}
KEY_FIELDS = {
    "key_id", "algorithm", "public_key", "roles", "status",
    "not_before", "not_after", "retired_at", "revoked_at",
    "revocation_reason",
}
REQUIRED_KEY_FIELDS = {"key_id", "algorithm", "public_key", "roles", "status"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _parse_time(value: str, field: str) -> datetime:
    if not isinstance(value, str):
        raise CordValidationError(f"{field} must be a timestamp string")
    _validate_timestamp(value, field)
    return datetime.fromisoformat(value[:-1] + "+00:00")


def _non_empty_trimmed(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise CordValidationError(f"{field} must be a non-empty trimmed string")


def load_trust_store(
    path: str | Path,
    expected_sha256: str,
) -> dict[str, Any]:
    """Load a trust store only when its exact raw bytes match a trusted pin."""
    if not isinstance(expected_sha256, str) or not SHA256_RE.fullmatch(expected_sha256):
        raise CordValidationError("expected_sha256 must be a lowercase SHA-256 digest")

    raw = _read_bounded(path, "trust store")
    actual_digest = hashlib.sha256(raw).hexdigest()
    if actual_digest != expected_sha256:
        raise CordValidationError("trust store digest does not match configured pin")

    store = _load_json(raw, "trust store")
    if set(store) != STORE_FIELDS:
        raise CordValidationError("trust store must contain exactly trust_store_version, store_id, and keys")
    if store["trust_store_version"] != "0.1":
        raise CordValidationError("unsupported trust_store_version")
    _non_empty_trimmed(store["store_id"], "trust_store.store_id")
    if not isinstance(store["keys"], list):
        raise CordValidationError("trust_store.keys must be an array")

    records: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(store["keys"]):
        label = f"trust_store.keys[{index}]"
        if not isinstance(record, dict):
            raise CordValidationError(f"{label} must be an object")
        fields = set(record)
        if not REQUIRED_KEY_FIELDS.issubset(fields) or fields - KEY_FIELDS:
            raise CordValidationError(f"{label} has missing or unexpected fields")

        key_id = record["key_id"]
        _non_empty_trimmed(key_id, f"{label}.key_id")
        if key_id in records:
            raise CordValidationError(f"duplicate trust-store key_id: {key_id}")

        if record["algorithm"] != "Ed25519":
            raise CordValidationError(f"{label}.algorithm is unsupported")
        encoded = record["public_key"]
        _non_empty_trimmed(encoded, f"{label}.public_key")
        try:
            raw_key = base64.b64decode(encoded, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise CordValidationError(f"{label}.public_key must be valid Base64") from exc
        if len(raw_key) != 32 or base64.b64encode(raw_key).decode("ascii") != encoded:
            raise CordValidationError(f"{label}.public_key must be canonical Base64 for 32 raw Ed25519 bytes")

        roles = record["roles"]
        if not isinstance(roles, list) or not roles:
            raise CordValidationError(f"{label}.roles must be a non-empty array")
        for role in roles:
            _non_empty_trimmed(role, f"{label}.roles[]")
        if len(set(roles)) != len(roles):
            raise CordValidationError(f"{label}.roles must not contain duplicates")

        status = record["status"]
        if not isinstance(status, str) or status not in {"active", "retired", "revoked"}:
            raise CordValidationError(f"{label}.status is unsupported")

        for field in ("not_before", "not_after", "retired_at", "revoked_at"):
            if field in record:
                if not isinstance(record[field], str):
                    raise CordValidationError(f"{label}.{field} must be a string")
                _parse_time(record[field], f"{label}.{field}")

        if "not_before" in record and "not_after" in record:
            if _parse_time(record["not_before"], f"{label}.not_before") >= _parse_time(record["not_after"], f"{label}.not_after"):
                raise CordValidationError(f"{label} validity interval must satisfy not_before < not_after")

        if status == "retired":
            if "retired_at" not in record or "revoked_at" in record:
                raise CordValidationError(f"{label} retired status requires retired_at and forbids revoked_at")
        elif "retired_at" in record:
            raise CordValidationError(f"{label}.retired_at is only valid for retired keys")

        if status == "revoked":
            if "revoked_at" not in record or "retired_at" in record:
                raise CordValidationError(f"{label} revoked status requires revoked_at and forbids retired_at")
        elif "revoked_at" in record:
            raise CordValidationError(f"{label}.revoked_at is only valid for revoked keys")

        if "revocation_reason" in record and (
            not isinstance(record["revocation_reason"], str)
            or len(record["revocation_reason"]) > 512
        ):
            raise CordValidationError(f"{label}.revocation_reason must be a string of at most 512 characters")

        normalized = dict(record)
        normalized["public_key_object"] = Ed25519PublicKey.from_public_bytes(raw_key)
        records[key_id] = normalized

    return {
        "trust_store_version": "0.1",
        "store_id": store["store_id"],
        "keys": records,
        "sha256": actual_digest,
    }


def verify_signed_receipt_with_store(
    receipt: dict[str, Any],
    envelope: dict[str, Any],
    trust_store: dict[str, Any],
    required_role: str | None = None,
    trusted_signature_time: str | None = None,
) -> dict[str, Any]:
    """Verify a receipt signature using a key from an already pinned trust store.

    The caller is responsible for independently validating trusted_signature_time
    (for example, from a supported timestamp authority). This function validates
    its syntax and applies policy; it does not validate a TSA token or time source.
    If no trusted time is supplied, receipt.created_at is never used as a substitute.
    """
    key_id = envelope.get("key_id") if isinstance(envelope, dict) else None
    _non_empty_trimmed(key_id, "signature envelope.key_id")
    record = trust_store.get("keys", {}).get(key_id)
    if record is None:
        raise CordValidationError("signing key_id is not present in the pinned trust store")

    if required_role is not None:
        _non_empty_trimmed(required_role, "required_role")
        if required_role not in record["roles"]:
            raise CordValidationError("signing key is not authorized for the required role")

    signature_result = verify_signed_receipt(
        receipt,
        envelope,
        record["public_key_object"],
        key_id,
    )

    temporal_status = "INDETERMINATE"
    temporal_reason = "No independently trusted signature time was supplied."
    if trusted_signature_time is not None:
        signed_at = _parse_time(trusted_signature_time, "trusted_signature_time")
        if "not_before" in record and signed_at < _parse_time(record["not_before"], "key.not_before"):
            temporal_status = "FAIL"
            temporal_reason = "Trusted signature time precedes key not_before."
        elif "not_after" in record and signed_at >= _parse_time(record["not_after"], "key.not_after"):
            temporal_status = "FAIL"
            temporal_reason = "Trusted signature time is at or after key not_after."
        elif record["status"] == "retired" and signed_at >= _parse_time(record["retired_at"], "key.retired_at"):
            temporal_status = "FAIL"
            temporal_reason = "Trusted signature time is at or after key retirement."
        elif record["status"] == "revoked" and signed_at >= _parse_time(record["revoked_at"], "key.revoked_at"):
            temporal_status = "FAIL"
            temporal_reason = "Trusted signature time is at or after key revocation."
        else:
            temporal_status = "PASS"
            temporal_reason = "Trusted signature time is within the configured key validity and lifecycle bounds."
    elif record["status"] == "active" and not any(
        field in record for field in ("not_before", "not_after")
    ):
        temporal_reason = "Key is currently active with no configured time bounds; historical signing time is not established."

    # Never emit an overall PASS while historical key validity is unknown.
    status = temporal_status

    return {
        "status": status,
        "signature_validity": "PASS",
        "key_resolution": "PASS",
        "key_id": key_id,
        "key_status": record["status"],
        "role_authorization": "NOT_REQUIRED" if required_role is None else "PASS",
        "historical_key_validity": temporal_status,
        "historical_key_validity_reason": temporal_reason,
        "trust_store_id": trust_store["store_id"],
        "trust_store_sha256": trust_store["sha256"],
        "signature": signature_result,
        "limitations": [
            "A producer-declared receipt timestamp is not trusted signature time.",
            "A trusted key and role assignment do not independently prove civil identity or real-world authority.",
        ],
    }
