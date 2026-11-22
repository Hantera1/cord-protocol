"""Cord append-only event-chain format (experimental).

A hash chain detects internal edits/reordering when compared with a trusted
checkpoint. It does not stop an attacker from rewriting the entire chain.
Anchor checkpoints externally and sign them for tamper evidence.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable

from verifier.verify import CordValidationError, SPEC_VERSION, _validate_timestamp

ZERO_HASH = "0" * 64
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
FIELDS = {"spec_version", "sequence", "previous_hash", "receipt_hash", "created_at", "event_hash"}


def _canonical(value: dict[str, str]) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: dict[str, str]) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def create_event(sequence: int, previous_hash: str, receipt_hash: str, created_at: str) -> dict[str, str]:
    # bool is a subclass of int in Python; reject it explicitly.
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
        raise CordValidationError("sequence must be a non-negative integer")
    if not isinstance(previous_hash, str) or not HASH_RE.fullmatch(previous_hash):
        raise CordValidationError("previous_hash must be a lowercase SHA-256 digest")
    if not isinstance(receipt_hash, str) or not HASH_RE.fullmatch(receipt_hash):
        raise CordValidationError("receipt_hash must be a lowercase SHA-256 digest")
    _validate_timestamp(created_at, "created_at")
    body = {
        "spec_version": SPEC_VERSION,
        "sequence": str(sequence),
        "previous_hash": previous_hash,
        "receipt_hash": receipt_hash,
        "created_at": created_at,
    }
    return {**body, "event_hash": _digest(body)}


def verify_chain(events: Iterable[dict[str, Any]], expected_head: str | None = None) -> dict[str, Any]:
    if expected_head is not None and (
        not isinstance(expected_head, str) or not HASH_RE.fullmatch(expected_head)
    ):
        raise CordValidationError("expected_head must be a lowercase SHA-256 digest")
    previous = ZERO_HASH
    count = 0
    for index, event in enumerate(events):
        if not isinstance(event, dict) or set(event) != FIELDS:
            raise CordValidationError(f"event {index} has invalid fields")
        if any(not isinstance(v, str) for v in event.values()):
            raise CordValidationError(f"event {index} fields must be strings")
        if event["spec_version"] != SPEC_VERSION:
            raise CordValidationError(f"event {index} has unsupported spec_version")
        if event["sequence"] != str(index):
            raise CordValidationError(f"event {index} has invalid sequence")
        if event["previous_hash"] != previous:
            raise CordValidationError(f"event {index} previous_hash mismatch")
        if not HASH_RE.fullmatch(event["receipt_hash"]):
            raise CordValidationError(f"event {index} receipt_hash is invalid")
        _validate_timestamp(event["created_at"], f"event {index}.created_at")
        body = {k: event[k] for k in ("spec_version", "sequence", "previous_hash", "receipt_hash", "created_at")}
        calculated = _digest(body)
        if not HASH_RE.fullmatch(event["event_hash"]) or calculated != event["event_hash"]:
            raise CordValidationError(f"event {index} hash mismatch")
        previous = calculated
        count += 1
    if expected_head is not None and previous != expected_head:
        raise CordValidationError("chain head does not match trusted checkpoint")
    return {
        "status": "PASS",
        "events": count,
        "head_hash": previous,
        "checkpoint_checked": expected_head is not None,
        "meaning": "Chain links are internally consistent. Trust against full-chain replacement requires an externally retained checkpoint.",
    }
