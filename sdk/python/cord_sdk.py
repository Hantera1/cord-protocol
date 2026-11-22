"""Small Python integration helpers for Cord Core v0.1."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from verifier.verify import create_receipt, verify_files


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def create_evidence(
    *,
    input_bytes: bytes,
    output_bytes: bytes,
    model_id: str,
    policy_id: str,
    event_timestamp: str,
    bundle_path: str | Path,
    receipt_path: str | Path,
    receipt_created_at: str,
) -> dict[str, str]:
    """Create Core files from application-selected exact input/output bytes.

    The caller is responsible for choosing/documenting byte serialization.
    model_id and timestamps are producer-declared, not independently attested.
    """
    bundle = {
        "spec_version": "0.1",
        "model_id": model_id,
        "timestamp": event_timestamp,
        "policy_id": policy_id,
        "input_hash": sha256_bytes(input_bytes),
        "output_hash": sha256_bytes(output_bytes),
    }
    Path(bundle_path).write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return create_receipt(bundle_path, receipt_path, receipt_created_at)


def verify_evidence(bundle_path: str | Path, receipt_path: str | Path) -> dict:
    """Verify a Core bundle and receipt offline."""
    return verify_files(bundle_path, receipt_path)
