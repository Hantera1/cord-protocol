"""CORD Evidence Validity Calculus (EVC) v0.1 prototype.

Evaluates claim-scoped dependency freshness only. It does not authenticate
claims/evidence, verify signatures, establish trusted time, or prove truth.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any, Mapping

SCHEMA_VERSION = "cord-evc-0.1"
MAX_GRAPH_BYTES = 2 * 1024 * 1024
DEPENDENCY_TYPES = frozenset({
    "SUBJECT_VERSION", "MODEL_VERSION", "CONFIGURATION", "TOOL_PERMISSION",
    "DATASET", "TEST_PROFILE", "VERIFIER_BUILD", "TRUST_ANCHOR",
    "SIGNING_KEY", "TIMESTAMP_POLICY", "EVIDENCE_ARTIFACT", "REGULATORY_PROFILE",
})
ROOT_FIELDS = frozenset({"schema_version", "graph_id", "subject", "current_state", "claims", "evidence", "dependencies"})
SUBJECT_FIELDS = frozenset({"id", "version", "sha256"})
STATE_FIELDS = frozenset({"type", "object_id", "sha256"})
CLAIM_FIELDS = frozenset({"id", "statement", "scope", "evidence_ids"})
EVIDENCE_FIELDS = frozenset({"id", "kind", "sha256"})
DEPENDENCY_FIELDS = frozenset({"claim_id", "type", "object_id", "expected_sha256"})


class EVCValidationError(ValueError):
    """Raised when an EVC graph is malformed or ambiguous."""


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


def _fields(value: Any, expected: frozenset[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise EVCValidationError(f"{label} must contain exactly: {', '.join(sorted(expected))}")


def _id(value: Any, label: str) -> None:
    if not _nonempty(value):
        raise EVCValidationError(f"{label} must be a non-empty trimmed string")


def _digest(value: Any, label: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise EVCValidationError(f"{label} must be a lowercase SHA-256 hex digest")


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8", errors="strict")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise EVCValidationError("Graph cannot be represented as canonical UTF-8 JSON") from exc


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EVCValidationError(f"Duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_graph(raw: bytes) -> dict[str, Any]:
    """Parse bounded strict UTF-8 JSON, rejecting duplicate keys and constants."""
    if not isinstance(raw, bytes):
        raise EVCValidationError("Graph input must be bytes")
    if len(raw) > MAX_GRAPH_BYTES:
        raise EVCValidationError("Graph exceeds the 2 MiB input limit")
    if raw.startswith(b"\xef\xbb\xbf"):
        raise EVCValidationError("UTF-8 BOM is not permitted")
    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=_unique_object,
            parse_constant=lambda token: (_ for _ in ()).throw(EVCValidationError(f"Invalid JSON constant: {token}")),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EVCValidationError("Graph must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise EVCValidationError("Graph top level must be an object")
    return value


def _validate(graph: Mapping[str, Any]):
    _fields(graph, ROOT_FIELDS, "graph")
    if graph["schema_version"] != SCHEMA_VERSION:
        raise EVCValidationError("Unsupported EVC schema_version")
    _id(graph["graph_id"], "graph_id")
    _fields(graph["subject"], SUBJECT_FIELDS, "subject")
    for field in ("id", "version"):
        _id(graph["subject"][field], "subject." + field)
    _digest(graph["subject"]["sha256"], "subject.sha256")

    evidence: dict[str, dict[str, Any]] = {}
    if not isinstance(graph["evidence"], list):
        raise EVCValidationError("evidence must be an array")
    for i, item in enumerate(graph["evidence"]):
        _fields(item, EVIDENCE_FIELDS, f"evidence[{i}]")
        _id(item["id"], f"evidence[{i}].id")
        _id(item["kind"], f"evidence[{i}].kind")
        _digest(item["sha256"], f"evidence[{i}].sha256")
        if item["id"] in evidence:
            raise EVCValidationError(f"Duplicate evidence id: {item['id']}")
        evidence[item["id"]] = item

    claims: dict[str, dict[str, Any]] = {}
    if not isinstance(graph["claims"], list):
        raise EVCValidationError("claims must be an array")
    for i, item in enumerate(graph["claims"]):
        _fields(item, CLAIM_FIELDS, f"claims[{i}]")
        for field in ("id", "statement", "scope"):
            _id(item[field], f"claims[{i}].{field}")
        if item["id"] in claims:
            raise EVCValidationError(f"Duplicate claim id: {item['id']}")
        refs = item["evidence_ids"]
        if not isinstance(refs, list) or any(not _nonempty(x) for x in refs):
            raise EVCValidationError(f"claims[{i}].evidence_ids must be an array of non-empty strings")
        if len(refs) != len(set(refs)):
            raise EVCValidationError(f"claims[{i}].evidence_ids contains duplicates")
        missing = sorted(set(refs) - set(evidence))
        if missing:
            raise EVCValidationError(f"claims[{i}] references unknown evidence: {', '.join(missing)}")
        claims[item["id"]] = item

    current: dict[tuple[str, str], str] = {}
    if not isinstance(graph["current_state"], list):
        raise EVCValidationError("current_state must be an array")
    for i, item in enumerate(graph["current_state"]):
        _fields(item, STATE_FIELDS, f"current_state[{i}]")
        if item["type"] not in DEPENDENCY_TYPES:
            raise EVCValidationError(f"current_state[{i}].type is unsupported")
        _id(item["object_id"], f"current_state[{i}].object_id")
        _digest(item["sha256"], f"current_state[{i}].sha256")
        key = (item["type"], item["object_id"])
        if key in current:
            raise EVCValidationError(f"Duplicate current_state entry: {key[0]}:{key[1]}")
        current[key] = item["sha256"]

    by_claim: dict[str, list[dict[str, Any]]] = {key: [] for key in claims}
    seen: set[tuple[str, str, str]] = set()
    if not isinstance(graph["dependencies"], list):
        raise EVCValidationError("dependencies must be an array")
    for i, item in enumerate(graph["dependencies"]):
        _fields(item, DEPENDENCY_FIELDS, f"dependencies[{i}]")
        if item["claim_id"] not in claims:
            raise EVCValidationError(f"dependencies[{i}] references unknown claim")
        if item["type"] not in DEPENDENCY_TYPES:
            raise EVCValidationError(f"dependencies[{i}].type is unsupported")
        _id(item["object_id"], f"dependencies[{i}].object_id")
        _digest(item["expected_sha256"], f"dependencies[{i}].expected_sha256")
        key = (item["claim_id"], item["type"], item["object_id"])
        if key in seen:
            raise EVCValidationError(f"Duplicate dependency: {key[0]}:{key[1]}:{key[2]}")
        seen.add(key)
        by_claim[item["claim_id"]].append(item)
    return claims, current, by_claim


def _normalized(graph: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(graph)
    result["claims"] = sorted(graph["claims"], key=lambda x: x["id"])
    result["evidence"] = sorted(graph["evidence"], key=lambda x: x["id"])
    result["current_state"] = sorted(graph["current_state"], key=lambda x: (x["type"], x["object_id"]))
    result["dependencies"] = sorted(graph["dependencies"], key=lambda x: (x["claim_id"], x["type"], x["object_id"]))
    return result


def evaluate_graph(graph: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate dependency freshness. VALID is not an authenticity or truth claim."""
    claims, current, by_claim = _validate(graph)
    results = []
    for claim_id in sorted(claims):
        claim = claims[claim_id]
        reasons: list[str] = []
        stale = False
        indeterminate = not bool(claim["evidence_ids"])
        if indeterminate:
            reasons.append("NO_EVIDENCE_REFERENCED")
        deps = sorted(by_claim[claim_id], key=lambda x: (x["type"], x["object_id"]))
        if not deps:
            indeterminate = True
            reasons.append("NO_DEPENDENCIES_DECLARED")
        for dep in deps:
            key = (dep["type"], dep["object_id"])
            observed = current.get(key)
            if observed is None:
                indeterminate = True
                reasons.append("CURRENT_STATE_MISSING:" + key[0] + ":" + key[1])
            elif observed != dep["expected_sha256"]:
                stale = True
                reasons.append("DEPENDENCY_CHANGED:" + key[0] + ":" + key[1])
        status = "STALE" if stale else "INDETERMINATE" if indeterminate else "VALID"
        if status == "VALID":
            reasons.append("ALL_DECLARED_DEPENDENCIES_MATCH")
        results.append({
            "claim_id": claim_id, "status": status, "statement": claim["statement"],
            "scope": claim["scope"], "evidence_ids": sorted(claim["evidence_ids"]),
            "dependency_count": len(deps), "reasons": sorted(reasons),
        })
    statuses = {x["status"] for x in results}
    overall = "STALE" if "STALE" in statuses else "INDETERMINATE" if not results or "INDETERMINATE" in statuses else "VALID"
    graph_digest = hashlib.sha256(_canonical_bytes(_normalized(graph))).hexdigest()
    return {
        "evc_version": SCHEMA_VERSION, "graph_id": graph["graph_id"],
        "graph_sha256": graph_digest, "status": overall, "claim_count": len(results),
        "claims": results,
        "limitations": [
            "This result evaluates declared dependency freshness only.",
            "Evidence digests are identifiers; evidence bytes are not supplied or verified here.",
            "This prototype does not authenticate issuers, signatures, timestamps, or change events.",
            "A VALID result does not establish factual truth, safety, legal compliance, or completeness.",
        ],
    }
