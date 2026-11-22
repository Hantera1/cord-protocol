"""Real OpenSSL-generated RFC 3161 integration and negative tests."""
import base64
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from verifier.signatures import sign_receipt
from verifier.trusted_timestamp import verify_receipt_signature_timestamp, verify_signed_receipt_with_timestamp
from verifier.verify import CordValidationError

OPENSSL = shutil.which("openssl")


@unittest.skipUnless(OPENSSL, "OpenSSL is required for RFC 3161 integration tests")
class RFC3161OpenSSLIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="cord-rfc3161-test-")
        cls.root = Path(cls.tmp.name)
        cls.ca = cls.root / "ca.pem"
        cls.ca_key = cls.root / "ca.key"
        cls.tsa_key = cls.root / "tsa.key"
        cls.tsa_csr = cls.root / "tsa.csr"
        cls.tsa_cert = cls.root / "tsa.pem"
        cls.token = cls.root / "token.der"
        cls.data = cls.root / "signature.bin"
        cls.private_key = Ed25519PrivateKey.generate()
        cls.key_id = "integration-test-key"
        cls.receipt = {
            "spec_version": "0.1",
            "bundle_hash": "a" * 64,
            "bundle_file_hash": "b" * 64,
            "created_at": "2026-11-22T12:00:00Z",
        }
        cls.envelope = sign_receipt(cls.receipt, cls.private_key, cls.key_id)
        cls.signature = base64.b64decode(cls.envelope["signature"], validate=True)
        cls.data.write_bytes(cls.signature)
        cls.trust_store = {
            "store_id": "integration-test-store",
            "sha256": "c" * 64,
            "keys": {
                cls.key_id: {
                    "public_key_object": cls.private_key.public_key(),
                    "roles": ["manufacturer"],
                    "status": "active",
                }
            },
        }

        def run(args):
            result = subprocess.run(
                [OPENSSL, *args], cwd=cls.root, check=False,
                capture_output=True, text=True, timeout=30, shell=False,
            )
            if result.returncode:
                raise RuntimeError(f"OpenSSL fixture command failed: {result.stderr}")
            return result

        cls.openssl = staticmethod(run)
        cls.openssl([
            "req", "-x509", "-newkey", "rsa:2048", "-nodes",
            "-keyout", str(cls.ca_key), "-out", str(cls.ca),
            "-subj", "/CN=CORD RFC3161 Test Root", "-days", "2",
            "-addext", "basicConstraints=critical,CA:TRUE",
            "-addext", "keyUsage=critical,keyCertSign,cRLSign",
        ])
        cls.openssl([
            "req", "-newkey", "rsa:2048", "-nodes",
            "-keyout", str(cls.tsa_key), "-out", str(cls.tsa_csr),
            "-subj", "/CN=CORD RFC3161 Test TSA",
        ])
        (cls.root / "tsa.ext").write_text(
            "basicConstraints=critical,CA:FALSE\n"
            "keyUsage=critical,digitalSignature,nonRepudiation\n"
            "extendedKeyUsage=critical,timeStamping\n"
            "subjectKeyIdentifier=hash\n"
            "authorityKeyIdentifier=keyid,issuer\n",
            encoding="ascii",
        )
        cls.openssl([
            "x509", "-req", "-in", str(cls.tsa_csr),
            "-CA", str(cls.ca), "-CAkey", str(cls.ca_key),
            "-CAcreateserial", "-out", str(cls.tsa_cert),
            "-days", "1", "-sha256", "-extfile", str(cls.root / "tsa.ext"),
        ])
        (cls.root / "tsa.cnf").write_text(
            "[ tsa ]\n"
            "default_tsa = tsa_config\n"
            "[ tsa_config ]\n"
            f"dir = {cls.root}\n"
            f"serial = {cls.root / 'tsa.serial'}\n"
            "crypto_device = builtin\n"
            f"signer_cert = {cls.tsa_cert}\n"
            f"certs = {cls.ca}\n"
            f"signer_key = {cls.tsa_key}\n"
            "signer_digest = sha256\n"
            "default_policy = 1.2.3.4.1\n"
            "other_policies = 1.2.3.4.5\n"
            "digests = sha256, sha384, sha512\n"
            "accuracy = secs:1\n"
            "ordering = yes\n"
            "tsa_name = yes\n"
            "ess_cert_id_chain = yes\n"
            "ess_cert_id_alg = sha256\n",
            encoding="ascii",
        )
        (cls.root / "tsa.serial").write_text("01\n", encoding="ascii")
        cls.openssl([
            "ts", "-query", "-data", str(cls.data), "-sha256",
            "-cert", "-out", str(cls.root / "request.tsq"),
        ])
        cls.openssl([
            "ts", "-reply", "-queryfile", str(cls.root / "request.tsq"),
            "-config", str(cls.root / "tsa.cnf"),
            "-token_out", "-out", str(cls.token),
        ])
        # Independent trust anchor used to prove the verifier rejects an
        # otherwise well-formed token from an untrusted TSA hierarchy.
        cls.other_ca = cls.root / "other-ca.pem"
        cls.openssl([
            "req", "-x509", "-newkey", "rsa:2048", "-nodes",
            "-keyout", str(cls.root / "other-ca.key"), "-out", str(cls.other_ca),
            "-subj", "/CN=Untrusted Test Root", "-days", "2",
            "-addext", "basicConstraints=critical,CA:TRUE",
            "-addext", "keyUsage=critical,keyCertSign,cRLSign",
        ])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_real_rfc3161_token_passes(self):
        result = verify_receipt_signature_timestamp(
            self.token.read_bytes(), self.envelope, self.ca
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["message_imprint"], "PASS")
        self.assertEqual(result["cms_signature"], "PASS")
        self.assertEqual(result["tsa_certificate_path"], "PASS")
        self.assertEqual(result["tsa_timestamping_eku"], "PASS")
        self.assertEqual(result["tsa_certificate_validity_at_generation_time"], "PASS")
        self.assertEqual(result["tsa_revocation"], "NOT_CHECKED")
        self.assertTrue(result["generation_time"].endswith("Z"))

    def test_wrong_signature_imprint_fails(self):
        altered = dict(self.envelope, signature=base64.b64encode(b"x" * 64).decode("ascii"))
        with self.assertRaisesRegex(CordValidationError, "validation failed"):
            verify_receipt_signature_timestamp(self.token.read_bytes(), altered, self.ca)

    def test_untrusted_tsa_root_fails(self):
        with self.assertRaisesRegex(CordValidationError, "validation failed"):
            verify_receipt_signature_timestamp(
                self.token.read_bytes(), ENVELOPE, self.other_ca
            )

    def test_crl_is_required_when_policy_demands_it(self):
        with self.assertRaisesRegex(CordValidationError, "CRL checking is required"):
            verify_receipt_signature_timestamp(
                self.token.read_bytes(), self.envelope, self.ca, require_crl=True
            )

    def test_timestamp_flows_into_trust_store_policy(self):
        result = verify_signed_receipt_with_timestamp(
            self.receipt,
            self.envelope,
            self.trust_store,
            self.token.read_bytes(),
            self.ca,
            required_role="manufacturer",
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["timestamp"]["status"], "PASS")
        self.assertEqual(result["trust"]["historical_key_validity"], "PASS")
        self.assertEqual(result["trust"]["role_authorization"], "PASS")


if __name__ == "__main__":
    unittest.main()
