"""Validation helpers for detached Cord Trade Evidence manifests.

Trade manifests are optional extensions linked to an unchanged Cord Core receipt.
They are evidence records, not proof that a physical-world claim is true.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "spec" / "TRADE-EVIDENCE-0.1.schema.json"


class CordTradeValidationError(ValueError):
    """Raised when a Cord Trade extension is invalid."""


def canonical_trade_json(manifest: dict[str, Any]) -> bytes:
    """Canonical JSON for hashing a detached Trade manifest.

    This helper sorts keys and emits compact UTF-8 JSON. It is not CORD-CJSON-1
    and must never be used to compute Core bundle or receipt hashes.
    """
    return json.dumps(
        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def validate_trade_manifest(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise CordTradeValidationError("Trade manifest must be a JSON object")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        raise CordTradeValidationError(f"{location}: {error.message}")
    return manifest


def trade_manifest_hash(manifest: dict[str, Any]) -> str:
    validate_trade_manifest(manifest)
    return hashlib.sha256(canonical_trade_json(manifest)).hexdigest()
