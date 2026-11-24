import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from assurance.evc import evaluate_graph, load_graph, EVCValidationError

ROOT = Path(__file__).resolve().parents[1]
VECTOR_FILE = ROOT / "test-vectors" / "evc-conformance-0.1.json"
CLI = ROOT / "build" / "assurance" / "evc_cli.js"
NODE = os.environ.get("NODE", "node")


@unittest.skipUnless(CLI.is_file(), "TypeScript EVC CLI is compiled by CI before cross-runtime tests")
class EVCCrossRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vectors = json.loads(VECTOR_FILE.read_text(encoding="utf-8"))

    def test_shared_vectors_match_byte_for_byte_semantics(self):
        for case in self.vectors["cases"]:
            with self.subTest(vector=case["name"]):
                graph = case["graph"]
                py_result = evaluate_graph(graph)
                self.assertEqual(py_result["status"], case["expected_status"])
                with tempfile.NamedTemporaryFile("wb", suffix=".json") as f:
                    f.write(json.dumps(graph, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
                    f.flush()
                    proc = subprocess.run([NODE, str(CLI), f.name], capture_output=True, check=False)
                self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", "replace"))
                ts_result = json.loads(proc.stdout.decode("utf-8"))
                self.assertEqual(ts_result, py_result)

    def test_array_permutations_keep_digest_and_results(self):
        graph = self.vectors["cases"][0]["graph"]
        expected = evaluate_graph(graph)
        for key in ("claims", "evidence", "current_state", "dependencies"):
            graph[key].reverse()
        with tempfile.NamedTemporaryFile("wb", suffix=".json") as f:
            f.write(json.dumps(graph, ensure_ascii=False).encode("utf-8"))
            f.flush()
            proc = subprocess.run([NODE, str(CLI), f.name], capture_output=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", "replace"))
        self.assertEqual(json.loads(proc.stdout.decode("utf-8")), expected)

    def test_typescript_rejects_malformed_json_inputs(self):
        bad_inputs = [
            b'{"schema_version":"cord-evc-0.1","schema_version":"cord-evc-0.1"}',
            b'\xef\xbb\xbf{}',
            b'\xff',
            b'{"x":NaN}',
        ]
        for raw in bad_inputs:
            with self.subTest(raw=raw[:20]):
                with tempfile.NamedTemporaryFile("wb", suffix=".json") as f:
                    f.write(raw)
                    f.flush()
                    proc = subprocess.run([NODE, str(CLI), f.name], capture_output=True, check=False)
                self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
