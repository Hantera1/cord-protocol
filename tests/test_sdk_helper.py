import tempfile
import unittest
from pathlib import Path

from sdk.python.cord_sdk import create_evidence, verify_evidence


class CordSdkTests(unittest.TestCase):
    def test_create_evidence_writes_real_newline_and_verifies(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle.json"
            receipt = Path(directory) / "receipt.json"
            create_evidence(
                input_bytes=b"hello",
                output_bytes=b"world",
                model_id="test-model",
                policy_id="test-policy",
                event_timestamp="2026-11-22T12:00:00Z",
                bundle_path=bundle,
                receipt_path=receipt,
                receipt_created_at="2026-11-22T12:00:01Z",
            )
            raw = bundle.read_bytes()
            self.assertTrue(raw.endswith(b"\n"))
            self.assertFalse(raw.endswith(b"\\n"))
            self.assertEqual(verify_evidence(bundle, receipt)["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
