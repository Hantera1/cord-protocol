import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from verifier.verify import (
    CordValidationError,
    canonical_json,
    create_receipt,
    verify_files,
)

BUNDLE = {
    "spec_version": "0.1",
    "model_id": "demo-model",
    "timestamp": "2026-03-06T12:00:00Z",
    "policy_id": "cord-output-v0.1",
    "input_hash": "1" * 64,
    "output_hash": "2" * 64,
}
NOW = "2026-03-06T12:00:05Z"


class CordVerifierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bundle = self.root / "bundle.json"
        self.receipt = self.root / "receipt.json"
        self.bundle.write_text(json.dumps(BUNDLE, indent=2) + "\n", encoding="utf-8")
        create_receipt(self.bundle, self.receipt, NOW)

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_package_passes(self):
        self.assertEqual(verify_files(self.bundle, self.receipt)["status"], "PASS")

    def test_published_test_vector_passes(self):
        root = Path(__file__).resolve().parents[1]
        result = verify_files(
            root / "test-vectors" / "bundle_valid.json",
            root / "test-vectors" / "receipt_valid.json",
        )
        self.assertEqual(result["status"], "PASS")

    def test_bundle_byte_change_fails(self):
        self.bundle.write_text(self.bundle.read_text() + " ", encoding="utf-8")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_receipt_hash_change_fails(self):
        receipt = json.loads(self.receipt.read_text())
        receipt["bundle_hash"] = "0" * 64
        self.receipt.write_text(json.dumps(receipt), encoding="utf-8")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_extra_bundle_field_rejected(self):
        self.bundle.write_text(json.dumps(dict(BUNDLE, unexpected="not allowed")), encoding="utf-8")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_duplicate_bundle_key_rejected(self):
        self.bundle.write_text('{"spec_version":"0.1","spec_version":"0.1"}', encoding="utf-8")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_duplicate_receipt_key_rejected(self):
        self.receipt.write_text(
            '{"spec_version":"0.1","spec_version":"0.1","bundle_hash":"' + "0" * 64
            + '","bundle_file_hash":"' + "0" * 64 + '","created_at":"' + NOW + '"}',
            encoding="utf-8",
        )
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_invalid_hash_rejected(self):
        self.bundle.write_text(json.dumps(dict(BUNDLE, input_hash="xyz")), encoding="utf-8")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_wrong_version_rejected(self):
        self.bundle.write_text(json.dumps(dict(BUNDLE, spec_version="9.9")), encoding="utf-8")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_oversized_bundle_rejected(self):
        self.bundle.write_bytes(b"x" * 32)
        with patch("verifier.verify.MAX_FILE_BYTES", 16):
            with self.assertRaisesRegex(CordValidationError, "exceeds 16 bytes"):
                verify_files(self.bundle, self.receipt)

    def test_oversized_receipt_rejected(self):
        self.receipt.write_bytes(b"x" * 32)
        with patch("verifier.verify.MAX_FILE_BYTES", 16):
            with self.assertRaisesRegex(CordValidationError, "exceeds 16 bytes"):
                verify_files(self.bundle, self.receipt)

    def test_oversized_bundle_rejected_during_receipt_creation(self):
        self.bundle.write_bytes(b"x" * 32)
        with patch("verifier.verify.MAX_FILE_BYTES", 16):
            with self.assertRaisesRegex(CordValidationError, "exceeds 16 bytes"):
                create_receipt(self.bundle, self.receipt, NOW)

    def test_deeply_nested_json_fails_closed(self):
        self.bundle.write_text("[" * 2000 + "0" + "]" * 2000, encoding="utf-8")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_utf8_bom_rejected(self):
        self.bundle.write_bytes(bytes.fromhex("efbbbf") + json.dumps(BUNDLE).encode("utf-8"))
        with self.assertRaisesRegex(CordValidationError, "BOM"):
            verify_files(self.bundle, self.receipt)

    def test_invalid_utf8_rejected(self):
        self.bundle.write_bytes(b"\xff")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_invalid_json_constant_rejected(self):
        malformed = json.dumps(BUNDLE)[:-1] + ',"unexpected":NaN}'
        self.bundle.write_text(malformed, encoding="utf-8")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_unpaired_surrogate_rejected(self):
        malformed = json.dumps(dict(BUNDLE, model_id="bad\ud800"))
        self.bundle.write_text(malformed, encoding="utf-8")
        with self.assertRaisesRegex(CordValidationError, "Unicode scalar"):
            verify_files(self.bundle, self.receipt)

    def test_canonical_json_unicode_and_control_escaping(self):
        bundle = dict(BUNDLE, model_id="é", policy_id="line\nfeed")
        encoded = canonical_json(bundle)
        self.assertIn("é".encode("utf-8"), encoded)
        self.assertIn(b'"policy_id":"line\\nfeed"', encoded)
        self.assertNotIn(b"\\u00e9", encoded)
        self.assertFalse(encoded.endswith(b"\n"))


if __name__ == "__main__":
    unittest.main()
