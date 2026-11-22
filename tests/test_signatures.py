import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from verifier.signatures import sign_receipt, verify_signed_receipt
from verifier.verify import CordValidationError

RECEIPT = {
    "spec_version": "0.1",
    "bundle_hash": "a" * 64,
    "bundle_file_hash": "b" * 64,
    "created_at": "2026-03-06T12:00:05Z",
}


class CordSignatureTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        self.public = self.private.public_key()
        self.envelope = sign_receipt(RECEIPT, self.private, "test-key-1")

    def test_valid_signature_passes_with_pinned_key(self):
        result = verify_signed_receipt(RECEIPT, self.envelope, self.public, "test-key-1")
        self.assertEqual(result["status"], "PASS")

    def test_modified_receipt_fails(self):
        changed = dict(RECEIPT, created_at="2026-03-06T12:00:06Z")
        with self.assertRaises(CordValidationError):
            verify_signed_receipt(changed, self.envelope, self.public, "test-key-1")

    def test_wrong_key_id_fails(self):
        with self.assertRaises(CordValidationError):
            verify_signed_receipt(RECEIPT, self.envelope, self.public, "other-key")

    def test_wrong_public_key_fails(self):
        other = Ed25519PrivateKey.generate().public_key()
        with self.assertRaises(CordValidationError):
            verify_signed_receipt(RECEIPT, self.envelope, other, "test-key-1")

    def test_non_string_key_id_fails_cleanly(self):
        with self.assertRaises(CordValidationError):
            sign_receipt(RECEIPT, self.private, 123)

    def test_non_ed25519_private_key_fails_cleanly(self):
        from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
        with self.assertRaises(CordValidationError):
            sign_receipt(RECEIPT, generate_private_key(public_exponent=65537, key_size=2048), "key")

    def test_invalid_pem_fails_cleanly(self):
        from verifier.signatures import load_private_key, load_public_key
        with self.assertRaises(CordValidationError):
            load_private_key(b"not a PEM")
        with self.assertRaises(CordValidationError):
            load_public_key(b"not a PEM")

    def test_non_object_envelope_fails_cleanly(self):
        with self.assertRaises(CordValidationError):
            verify_signed_receipt(RECEIPT, [], self.public, "test-key-1")

    def test_non_ed25519_public_key_fails_cleanly(self):
        from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
        other = generate_private_key(public_exponent=65537, key_size=2048).public_key()
        with self.assertRaises(CordValidationError):
            verify_signed_receipt(RECEIPT, self.envelope, other, "test-key-1")


if __name__ == "__main__":
    unittest.main()
