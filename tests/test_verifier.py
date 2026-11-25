import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from verifier.verify import MAX_FILE_BYTES, MAX_JSON_DEPTH, CordValidationError, _read_bounded_file, create_receipt, verify_files

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


    def test_reader_requests_only_limit_plus_one_bytes(self):
        class ReadSpy:
            requested_size = None

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self, size):
                self.requested_size = size
                return b"x" * size

        reader = ReadSpy()
        with mock.patch.object(Path, "open", return_value=reader):
            with self.assertRaisesRegex(CordValidationError, "bundle exceeds"):
                _read_bounded_file(self.bundle, "bundle")
        self.assertEqual(reader.requested_size, MAX_FILE_BYTES + 1)

    def test_oversized_bundle_is_rejected_before_full_read(self):
        self.bundle.write_bytes(b" " * (MAX_FILE_BYTES + 1))
        with self.assertRaisesRegex(CordValidationError, "bundle exceeds"):
            verify_files(self.bundle, self.receipt)

    def test_oversized_receipt_is_rejected(self):
        self.receipt.write_bytes(b" " * (MAX_FILE_BYTES + 1))
        with self.assertRaisesRegex(CordValidationError, "receipt exceeds"):
            verify_files(self.bundle, self.receipt)

    def test_excessive_json_nesting_is_rejected(self):
        nested = b'{"x":' + b"[" * (MAX_JSON_DEPTH + 1) + b"0" + b"]" * (MAX_JSON_DEPTH + 1) + b"}"
        self.bundle.write_bytes(nested)
        with self.assertRaisesRegex(CordValidationError, "nesting depth"):
            verify_files(self.bundle, self.receipt)


    def test_unpaired_surrogate_in_field_value_is_rejected(self):
        self.bundle.write_text(
            json.dumps(dict(BUNDLE, model_id="\ud800")),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(CordValidationError, "invalid Unicode"):
            verify_files(self.bundle, self.receipt)

    def test_unpaired_surrogate_in_field_name_is_rejected(self):
        self.bundle.write_text('{"\ud800":"value"}', encoding="utf-8")
        with self.assertRaisesRegex(CordValidationError, "invalid Unicode field name"):
            verify_files(self.bundle, self.receipt)

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
        bundle = dict(BUNDLE, unexpected="not allowed")
        self.bundle.write_text(json.dumps(bundle), encoding="utf-8")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_duplicate_json_key_rejected(self):
        self.bundle.write_text('{"spec_version":"0.1","spec_version":"0.1"}', encoding="utf-8")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_invalid_hash_rejected(self):
        bundle = dict(BUNDLE, input_hash="xyz")
        self.bundle.write_text(json.dumps(bundle), encoding="utf-8")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)

    def test_wrong_version_rejected(self):
        bundle = dict(BUNDLE, spec_version="9.9")
        self.bundle.write_text(json.dumps(bundle), encoding="utf-8")
        with self.assertRaises(CordValidationError):
            verify_files(self.bundle, self.receipt)


if __name__ == "__main__":
    unittest.main()
