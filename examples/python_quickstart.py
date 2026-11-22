"""Minimal end-to-end Cord integration example.

Run from the repository root after: python -m pip install -r requirements.txt
"""
from pathlib import Path

from sdk.python.cord_sdk import create_evidence, verify_evidence

create_evidence(
    input_bytes=b'What is 2 + 2?',
    output_bytes=b'4',
    model_id="example-model",
    policy_id="example-policy-v1",
    event_timestamp="2026-11-22T12:00:00Z",
    bundle_path=Path("bundle.json"),
    receipt_path=Path("receipt.json"),
    receipt_created_at="2026-11-22T12:00:01Z",
)
print(verify_evidence("bundle.json", "receipt.json"))
