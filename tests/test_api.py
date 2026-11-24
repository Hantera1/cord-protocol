import base64
import hashlib
import json
import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.app import app
from verifier.verify import canonical_json, sha256

BUNDLE = {
    "spec_version": "0.1",
    "model_id": "api-test-model",
    "timestamp": "2026-03-06T12:00:00Z",
    "policy_id": "cord-output-v0.1",
    "input_hash": "1" * 64,
    "output_hash": "2" * 64,
}


def evidence_pair():
    bundle_bytes = (json.dumps(BUNDLE, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    receipt = {
        "spec_version": "0.1",
        "bundle_hash": sha256(canonical_json(BUNDLE)),
        "bundle_file_hash": sha256(bundle_bytes),
        "created_at": "2026-03-06T12:00:05Z",
    }
    receipt_bytes = (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return bundle_bytes, receipt_bytes


def request_body(bundle_bytes, receipt_bytes):
    return {
        "spec_version": "0.1",
        "bundle_base64": base64.b64encode(bundle_bytes).decode("ascii"),
        "receipt_base64": base64.b64encode(receipt_bytes).decode("ascii"),
    }


class CordVerifyApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.auth = patch.dict(os.environ, {"CORD_API_AUTH_DISABLED": "true"}, clear=False)
        self.auth.start()

    def tearDown(self):
        self.auth.stop()

    def test_health_is_available(self):
        response = self.client.get("/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_valid_evidence_passes_and_reports_scope(self):
        bundle, receipt = evidence_pair()
        response = self.client.post("/v1/verify/core", json=request_body(bundle, receipt))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"]["status"], "PASS")
        self.assertEqual(response.json()["result"]["profile"], "cord-core")
        self.assertIn("not proof of identity", response.json()["result"]["meaning"])

    def test_hash_mismatch_is_fail_not_http_error(self):
        bundle, receipt = evidence_pair()
        changed = bundle + b" "
        response = self.client.post("/v1/verify/core", json=request_body(changed, receipt))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"]["status"], "FAIL")

    def test_duplicate_outer_json_keys_are_rejected(self):
        response = self.client.post(
            "/v1/verify/core",
            content=b'{"spec_version":"0.1","spec_version":"0.1","bundle_base64":"","receipt_base64":""}',
            headers={"content-type": "application/json"},
        )
        self.assertEqual(response.status_code, 400)

    def test_noncanonical_base64_is_rejected(self):
        response = self.client.post(
            "/v1/verify/core",
            json={"spec_version": "0.1", "bundle_base64": "YQ", "receipt_base64": "YQ"},
        )
        self.assertEqual(response.status_code, 400)

    def test_unsupported_version_is_unprocessable(self):
        response = self.client.post(
            "/v1/verify/core",
            json={"spec_version": "9.9", "bundle_base64": "", "receipt_base64": ""},
        )
        self.assertEqual(response.status_code, 422)

    def test_authentication_required_when_not_disabled(self):
        with patch.dict(os.environ, {"CORD_API_AUTH_DISABLED": "false"}, clear=False):
            os.environ.pop("CORD_API_KEY_SHA256", None)
            response = self.client.post("/v1/verify/core", json={})
        self.assertEqual(response.status_code, 503)

    def test_invalid_api_key_is_rejected(self):
        key = "example-api-key-that-is-long-enough"
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        with patch.dict(os.environ, {"CORD_API_AUTH_DISABLED": "false", "CORD_API_KEY_SHA256": digest}, clear=False):
            response = self.client.post("/v1/verify/core", json={}, headers={"authorization": "Bearer wrong"})
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
