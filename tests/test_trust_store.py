import base64
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from verifier.signatures import sign_receipt
from verifier.trust_store import load_trust_store, verify_signed_receipt_with_store
from verifier.verify import CordValidationError

RECEIPT = {
    "spec_version": "0.1",
    "bundle_hash": "a" * 64,
    "bundle_file_hash": "b" * 64,
    "created_at": "2026-03-06T12:00:05Z",
}


class TrustStoreTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        self.public_bytes = self.private.public_key().public_bytes_raw()
        self.key_id = "manufacturer-key-1"
        self.record = {
            "key_id": self.key_id,
            "algorithm": "Ed25519",
            "public_key": base64.b64encode(self.public_bytes).decode("ascii"),
            "roles": ["manufacturer", "issuer"],
            "status": "active",
        }
        self.envelope = sign_receipt(RECEIPT, self.private, self.key_id)
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "trust-store.json"

    def tearDown(self):
        self.temp.cleanup()

    def write_store(self, record=None):
        data = {
            "trust_store_version": "0.1",
            "store_id": "test-deployment",
            "keys": [self.record if record is None else record],
        }
        raw = (json.dumps(data, separators=(",", ":")) + "\n").encode("utf-8")
        self.path.write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def load(self, record=None):
        digest = self.write_store(record)
        return load_trust_store(self.path, digest)

    def test_valid_pinned_store_verifies_signature_and_role(self):
        store = self.load()
        result = verify_signed_receipt_with_store(
            RECEIPT, self.envelope, store, required_role="manufacturer"
        )
        self.assertEqual(result["status"], "INDETERMINATE")
        self.assertEqual(result["signature_validity"], "PASS")
        self.assertEqual(result["role_authorization"], "PASS")
        self.assertEqual(result["historical_key_validity"], "INDETERMINATE")

    def test_wrong_pin_fails_closed(self):
        digest = self.write_store()
        with self.assertRaisesRegex(CordValidationError, "does not match"):
            load_trust_store(self.path, "0" * 64)

    def test_unknown_key_id_fails(self):
        store = self.load()
        changed = dict(self.envelope, key_id="unknown-key")
        with self.assertRaisesRegex(CordValidationError, "not present"):
            verify_signed_receipt_with_store(RECEIPT, changed, store)

    def test_missing_role_fails(self):
        store = self.load()
        with self.assertRaisesRegex(CordValidationError, "not authorized"):
            verify_signed_receipt_with_store(
                RECEIPT, self.envelope, store, required_role="independent_examiner"
            )

    def test_duplicate_key_ids_fail(self):
        data = {
            "trust_store_version": "0.1",
            "store_id": "test-deployment",
            "keys": [self.record, self.record],
        }
        raw = json.dumps(data).encode("utf-8")
        self.path.write_bytes(raw)
        with self.assertRaisesRegex(CordValidationError, "duplicate"):
            load_trust_store(self.path, hashlib.sha256(raw).hexdigest())

    def test_noncanonical_or_wrong_length_public_key_fails(self):
        bad = dict(self.record, public_key=base64.b64encode(b"short").decode("ascii"))
        with self.assertRaisesRegex(CordValidationError, "32 raw"):
            self.load(bad)

    def test_retired_key_without_trusted_time_is_indeterminate(self):
        retired = dict(self.record, status="retired", retired_at="2026-03-07T00:00:00Z")
        store = self.load(retired)
        result = verify_signed_receipt_with_store(RECEIPT, self.envelope, store)
        self.assertEqual(result["status"], "INDETERMINATE")
        self.assertEqual(result["historical_key_validity"], "INDETERMINATE")

    def test_retired_key_passes_with_trusted_time_before_retirement(self):
        retired = dict(self.record, status="retired", retired_at="2026-03-07T00:00:00Z")
        store = self.load(retired)
        result = verify_signed_receipt_with_store(
            RECEIPT, self.envelope, store,
            trusted_signature_time="2026-03-06T12:00:05Z"
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["historical_key_validity"], "PASS")

    def test_revoked_key_fails_with_trusted_time_after_revocation(self):
        revoked = dict(self.record, status="revoked", revoked_at="2026-03-07T00:00:00Z")
        store = self.load(revoked)
        result = verify_signed_receipt_with_store(
            RECEIPT, self.envelope, store,
            trusted_signature_time="2026-03-08T00:00:00Z"
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["historical_key_validity"], "FAIL")

    def test_receipt_created_at_is_not_used_as_trusted_signature_time(self):
        revoked = dict(self.record, status="revoked", revoked_at="2026-03-07T00:00:00Z")
        store = self.load(revoked)
        result = verify_signed_receipt_with_store(RECEIPT, self.envelope, store)
        self.assertEqual(result["status"], "INDETERMINATE")

    def test_active_key_with_trusted_time_outside_validity_fails(self):
        bounded = dict(
            self.record,
            not_before="2026-03-07T00:00:00Z",
            not_after="2026-04-01T00:00:00Z",
        )
        store = self.load(bounded)
        result = verify_signed_receipt_with_store(
            RECEIPT, self.envelope, store,
            trusted_signature_time="2026-03-06T12:00:05Z"
        )
        self.assertEqual(result["status"], "FAIL")

    def test_duplicate_json_keys_fail(self):
        raw = b'{"trust_store_version":"0.1","trust_store_version":"0.1","store_id":"x","keys":[]}'
        self.path.write_bytes(raw)
        with self.assertRaises(CordValidationError):
            load_trust_store(self.path, hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    unittest.main()
