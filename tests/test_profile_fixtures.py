"""End-to-end tests for the initial CORD application profile fixtures."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from verifier.profile_engine import create_profile_receipt, verify_profile_package
from verifier.verify import create_receipt

ROOT = Path(__file__).resolve().parents[1]
PROFILE_ROOT = ROOT / "profiles"
EXAMPLES = ROOT / "examples" / "profile-packages"
NOW = "2026-11-22T10:00:05Z"


class InitialProfileFixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def build_package(self, profile_name):
        package = self.root / profile_name
        package.mkdir()
        profile_dir = PROFILE_ROOT / profile_name
        (package / "profile-manifest.json").write_bytes(
            (profile_dir / "manifest.json").read_bytes()
        )
        (package / "profile-evidence.json").write_bytes(
            (EXAMPLES / profile_name / "profile-evidence.json").read_bytes()
        )
        bundle = {
            "spec_version": "0.1",
            "model_id": "cord-profile-fixture",
            "timestamp": "2026-11-22T10:00:00Z",
            "policy_id": "cord-profile-fixture-v0.1",
            "input_hash": "1" * 64,
            "output_hash": "2" * 64,
        }
        (package / "bundle.json").write_text(
            json.dumps(bundle, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        create_receipt(package / "bundle.json", package / "receipt.json", NOW)
        create_profile_receipt(
            package / "profile-manifest.json",
            package / "profile-evidence.json",
            package / "profile-receipt.json",
            created_at="2026-11-22T10:00:06Z",
        )
        return package

    def reseal(self, package):
        create_profile_receipt(
            package / "profile-manifest.json",
            package / "profile-evidence.json",
            package / "profile-receipt.json",
            created_at="2026-11-22T10:00:06Z",
        )

    def test_example_builder_creates_both_verifiable_packages(self):
        output = self.root / "built-packages"
        subprocess.run(
            [sys.executable, str(ROOT / "examples" / "build_profile_packages.py"),
             "--output-dir", str(output)],
            check=True,
            capture_output=True,
            text=True,
        )
        for profile_name in ("luxury-asset", "clock"):
            result = verify_profile_package(output / profile_name, PROFILE_ROOT)
            self.assertEqual(result["status"], "PASS", result)

    def test_luxury_asset_fixture_passes(self):
        result = verify_profile_package(self.build_package("luxury-asset"), PROFILE_ROOT)
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["checks"]["profile_validation"]["profile_id"],
                         "org.cordprotocol.profile.luxury-asset")

    def test_clock_fixture_passes(self):
        result = verify_profile_package(self.build_package("clock"), PROFILE_ROOT)
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["checks"]["profile_validation"]["profile_id"],
                         "org.cordprotocol.profile.clock")

    def test_luxury_asset_duplicate_evidence_id_fails(self):
        package = self.build_package("luxury-asset")
        path = package / "profile-evidence.json"
        evidence = json.loads(path.read_text(encoding="utf-8"))
        evidence["evidence"][1]["evidence_id"] = evidence["evidence"][0]["evidence_id"]
        path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        self.reseal(package)
        result = verify_profile_package(package, PROFILE_ROOT)
        self.assertEqual(result["status"], "FAIL", result)
        self.assertIn("duplicate evidence_id", result["error"])

    def test_substantive_authenticity_claim_requires_examiner_role(self):
        package = self.build_package("luxury-asset")
        path = package / "profile-evidence.json"
        evidence = json.loads(path.read_text(encoding="utf-8"))
        evidence["evidence"][1]["assessment"] = "authentic"
        evidence["evidence"][1]["issuer"]["issuer_role"] = "seller"
        path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        self.reseal(package)
        result = verify_profile_package(package, PROFILE_ROOT)
        self.assertEqual(result["status"], "FAIL", result)
        self.assertIn("substantive authenticity assessment", result["error"])

    def test_clock_external_timestamp_reference_must_resolve(self):
        package = self.build_package("clock")
        path = package / "profile-evidence.json"
        evidence = json.loads(path.read_text(encoding="utf-8"))
        evidence["time_claims"][0]["assurance"] = "external_timestamp_reference"
        evidence["time_claims"][0]["timestamp_token_ref"] = "missing-token"
        path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        self.reseal(package)
        result = verify_profile_package(package, PROFILE_ROOT)
        self.assertEqual(result["status"], "FAIL", result)
        self.assertIn("must resolve to a token", result["error"])

    def test_clock_digest_length_must_match_algorithm(self):
        package = self.build_package("clock")
        path = package / "profile-evidence.json"
        evidence = json.loads(path.read_text(encoding="utf-8"))
        evidence["timestamp_tokens"] = [{
            "token_id": "tsa-token-1", "format": "RFC3161",
            "token_digest": "a" * 64,
            "message_imprint_algorithm": "sha256",
            "message_imprint_digest": "b" * 32,
            "validation_status": "not_validated",
        }]
        path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        self.reseal(package)
        result = verify_profile_package(package, PROFILE_ROOT)
        self.assertEqual(result["status"], "FAIL", result)
        self.assertIn("length does not match", result["error"])


if __name__ == "__main__":
    unittest.main()
