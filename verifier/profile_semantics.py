"""Profile-specific semantic checks for CORD draft application profiles.

These checks validate internal consistency only. They do not authenticate issuers,
verify RFC 3161 tokens, establish physical authenticity, or determine legal title.
"""
from __future__ import annotations

from typing import Any


class ProfileSemanticError(ValueError):
    """Evidence is structurally valid but semantically inconsistent."""


def _unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ProfileSemanticError(f"duplicate {label}")


def validate_profile_semantics(profile_id: str, evidence: dict[str, Any]) -> None:
    if profile_id == "org.cordprotocol.profile.luxury-asset":
        _validate_luxury_asset(evidence)
    elif profile_id == "org.cordprotocol.profile.clock":
        _validate_clock(evidence)


def _validate_luxury_asset(evidence: dict[str, Any]) -> None:
    asset = evidence["asset"]
    records = evidence["evidence"]
    _unique([record["evidence_id"] for record in records], "evidence_id")

    if asset.get("serial_number") and asset.get("serial_number_visibility") is None:
        raise ProfileSemanticError(
            "serial_number_visibility is required when serial_number is present"
        )

    for record in records:
        kind = record["evidence_type"]
        issuer_role = record["issuer"]["issuer_role"]
        if kind == "AuthenticityEvidence":
            assessment = record["assessment"]
            if assessment in {"authentic", "not_authentic", "inconclusive"} and issuer_role not in {
                "manufacturer", "authorized_service", "independent_examiner"
            }:
                raise ProfileSemanticError(
                    "a substantive authenticity assessment requires a manufacturer, "
                    "authorized_service, or independent_examiner issuer role"
                )
        elif kind == "TransferEvidence":
            if record["from_party_ref"] == record["to_party_ref"]:
                raise ProfileSemanticError("transfer from_party_ref and to_party_ref must differ")
        elif kind == "CustodyEvidence":
            if "party_ref" in record:
                raise ProfileSemanticError(
                    "custody evidence must use custodian_ref, not ownership party_ref"
                )


def _validate_clock(evidence: dict[str, Any]) -> None:
    claims = evidence["time_claims"]
    observations = evidence["observations"]
    tokens = evidence["timestamp_tokens"]
    orders = evidence["event_orders"]

    _unique([item["claim_id"] for item in claims], "time claim id")
    _unique([item["observation_id"] for item in observations], "clock observation id")
    _unique([item["token_id"] for item in tokens], "timestamp token id")
    _unique(
        [f'{item["source_ref"]}:{item["sequence"]}' for item in orders],
        "source sequence pair",
    )

    token_ids = {item["token_id"] for item in tokens}
    for claim in claims:
        if claim["assurance"] == "external_timestamp_reference":
            if claim.get("timestamp_token_ref") not in token_ids:
                raise ProfileSemanticError(
                    "external timestamp reference must resolve to a token in this evidence package"
                )

    expected_lengths = {"sha256": 64, "sha384": 96, "sha512": 128}
    for token in tokens:
        expected = expected_lengths[token["message_imprint_algorithm"]]
        if len(token["message_imprint_digest"]) != expected:
            raise ProfileSemanticError(
                "message_imprint_digest length does not match message_imprint_algorithm"
            )

    for order in orders:
        if order["ordering_basis"] == "external_checkpoint" and not order.get("checkpoint_digest"):
            raise ProfileSemanticError("external checkpoint ordering requires checkpoint_digest")
        if order["ordering_basis"] == "monotonic_clock" and not order.get("clock_domain_ref"):
            raise ProfileSemanticError("monotonic clock ordering requires clock_domain_ref")
