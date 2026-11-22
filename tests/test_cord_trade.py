import unittest

from sdk.python.cord_trade import (
    CordTradeValidationError,
    trade_manifest_hash,
    validate_trade_manifest,
)


class CordTradeTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {
            "extension": "cord.trade.evidence",
            "extension_version": "0.1",
            "event_id": "evt-demo-0001",
            "event_type": "asset.registered",
            "created_at": "2026-11-22T12:00:00Z",
            "core_receipt_hash": "a" * 64,
            "trust_class": "DECLARED",
            "claims": [
                {"claim": "serial_number", "value": "DEMO-12345", "trust_class": "DECLARED"}
            ],
            "asset": {
                "category": "watch",
                "brand": "Example",
                "model": "Demo",
                "serial_number": "DEMO-12345"
            },
            "disclosure": {"contains_personal_data": False, "visibility": "counterparties"}
        }

    def test_valid_trade_manifest(self):
        self.assertEqual(validate_trade_manifest(self.manifest), self.manifest)
        self.assertEqual(len(trade_manifest_hash(self.manifest)), 64)

    def test_watch_and_silver_examples_match_schema(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1]
        for filename in ("trade_watch_sale.json", "trade_silver_lot.json"):
            data = json.loads((root / "examples" / filename).read_text(encoding="utf-8"))
            self.assertEqual(validate_trade_manifest(data), data)

    def test_rejects_unknown_fields(self):
        invalid = {**self.manifest, "secret_private_key": "never"}
        with self.assertRaises(CordTradeValidationError):
            validate_trade_manifest(invalid)

    def test_rejects_bad_core_receipt_hash(self):
        invalid = {**self.manifest, "core_receipt_hash": "not-a-hash"}
        with self.assertRaises(CordTradeValidationError):
            validate_trade_manifest(invalid)

    def test_rejects_untrusted_class(self):
        invalid = {**self.manifest, "trust_class": "VERIFIED"}
        with self.assertRaises(CordTradeValidationError):
            validate_trade_manifest(invalid)


if __name__ == "__main__":
    unittest.main()
