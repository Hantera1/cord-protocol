"""Cord signed-receipt extension (Ed25519).

The trusted public key MUST be supplied by the verifier from an out-of-band
trust store. A key_id inside an envelope is only a lookup hint, not identity
proof by itself.
"""
from __future__ import annotations

import base64
import json
from typing import Any

from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from verifier.verify import CordValidationError, RECEIPT_FIELDS, SPEC_VERSION, _validate_fields, validate_receipt

ENVELOPE_FIELDS = {"spec_version", "alg", "key_id", "signature"}


def canonical_receipt(receipt: dict[str, Any]) -> bytes:
    """Return deterministic bytes for the exact validated Core receipt."""
    validate_receipt(receipt)
    return json.dumps(
        receipt, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def load_private_key(pem: bytes, password: bytes | None = None) -> Ed25519PrivateKey:
    try:
        key = serialization.load_pem_private_key(pem, password=password)
    except (TypeError, ValueError, UnsupportedAlgorithm) as exc:
        raise CordValidationError("invalid private key PEM or password") from exc
    if not isinstance(key, Ed25519PrivateKey):
        raise CordValidationError("private key must be Ed25519")
    return key


def load_public_key(pem: bytes) -> Ed25519PublicKey:
    try:
        key = serialization.load_pem_public_key(pem)
    except (TypeError, ValueError, UnsupportedAlgorithm) as exc:
        raise CordValidationError("invalid public key PEM") from exc
    if not isinstance(key, Ed25519PublicKey):
        raise CordValidationError("trusted public key must be Ed25519")
    return key


def sign_receipt(
    receipt: dict[str, Any], private_key: Ed25519PrivateKey, key_id: str
) -> dict[str, str]:
    if not isinstance(key_id, str) or not key_id or key_id.strip() != key_id:
        raise CordValidationError("key_id must be a non-empty trimmed string")
    if not isinstance(private_key, Ed25519PrivateKey):
        raise CordValidationError("private_key must be an Ed25519 private key")
    signature = private_key.sign(canonical_receipt(receipt))
    return {
        "spec_version": SPEC_VERSION,
        "alg": "Ed25519",
        "key_id": key_id,
        "signature": base64.b64encode(signature).decode("ascii"),
    }


def verify_signed_receipt(
    receipt: dict[str, Any],
    envelope: dict[str, Any],
    trusted_public_key: Ed25519PublicKey,
    expected_key_id: str,
) -> dict[str, Any]:
    if not isinstance(envelope, dict):
        raise CordValidationError("signature envelope must be an object")
    if not isinstance(trusted_public_key, Ed25519PublicKey):
        raise CordValidationError("trusted_public_key must be an Ed25519 public key")
    if not isinstance(expected_key_id, str) or not expected_key_id or expected_key_id.strip() != expected_key_id:
        raise CordValidationError("expected_key_id must be a non-empty trimmed string")
    validate_receipt(receipt)
    _validate_fields(envelope, ENVELOPE_FIELDS, "signature envelope")
    if envelope["spec_version"] != SPEC_VERSION:
        raise CordValidationError("unsupported signature envelope spec_version")
    if envelope["alg"] != "Ed25519":
        raise CordValidationError("unsupported signature algorithm")
    if not expected_key_id or envelope["key_id"] != expected_key_id:
        raise CordValidationError("untrusted or unexpected signing key_id")
    try:
        signature = base64.b64decode(envelope["signature"], validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise CordValidationError("signature must be valid base64") from exc
    if len(signature) != 64:
        raise CordValidationError("Ed25519 signature must be 64 bytes")
    try:
        trusted_public_key.verify(signature, canonical_receipt(receipt))
    except InvalidSignature as exc:
        raise CordValidationError("receipt signature verification failed") from exc
    return {
        "status": "PASS",
        "algorithm": "Ed25519",
        "key_id": expected_key_id,
        "meaning": "Receipt signature matches the externally trusted public key.",
    }
