import copy
import unittest
from assurance.evc import EVCValidationError, evaluate_graph, load_graph

H1, H2, H3 = "1" * 64, "2" * 64, "3" * 64

def sample_graph():
    return {
        "schema_version": "cord-evc-0.1", "graph_id": "demo-graph-001",
        "subject": {"id": "assistant-prod", "version": "v1", "sha256": H1},
        "current_state": [
            {"type": "MODEL_VERSION", "object_id": "model-A", "sha256": H1},
            {"type": "TOOL_PERMISSION", "object_id": "browser-readonly", "sha256": H2}],
        "claims": [
            {"id": "claim-model", "statement": "Declared model version is unchanged", "scope": "model identity", "evidence_ids": ["ev-1"]},
            {"id": "claim-tools", "statement": "Tool permission set is unchanged", "scope": "tool permissions", "evidence_ids": ["ev-2"]}],
        "evidence": [
            {"id": "ev-1", "kind": "test-report", "sha256": H1},
            {"id": "ev-2", "kind": "configuration-snapshot", "sha256": H2}],
        "dependencies": [
            {"claim_id": "claim-model", "type": "MODEL_VERSION", "object_id": "model-A", "expected_sha256": H1},
            {"claim_id": "claim-tools", "type": "TOOL_PERMISSION", "object_id": "browser-readonly", "expected_sha256": H2}]}

class EVCTests(unittest.TestCase):
    def test_unchanged_graph_is_valid(self):
        result = evaluate_graph(sample_graph())
        self.assertEqual(result["status"], "VALID")
        self.assertEqual([x["status"] for x in result["claims"]], ["VALID", "VALID"])

    def test_change_invalidates_only_dependent_claim(self):
        graph = sample_graph()
        graph["current_state"][1]["sha256"] = H3
        result = evaluate_graph(graph)
        by_id = {x["claim_id"]: x["status"] for x in result["claims"]}
        self.assertEqual(by_id, {"claim-model": "VALID", "claim-tools": "STALE"})

    def test_missing_current_state_is_indeterminate(self):
        graph = sample_graph()
        graph["current_state"].pop()
        by_id = {x["claim_id"]: x["status"] for x in evaluate_graph(graph)["claims"]}
        self.assertEqual(by_id["claim-tools"], "INDETERMINATE")

    def test_missing_evidence_is_indeterminate(self):
        graph = sample_graph()
        graph["claims"][0]["evidence_ids"] = []
        self.assertEqual(evaluate_graph(graph)["claims"][0]["status"], "INDETERMINATE")

    def test_unknown_evidence_reference_rejected(self):
        graph = sample_graph()
        graph["claims"][0]["evidence_ids"] = ["missing"]
        with self.assertRaises(EVCValidationError): evaluate_graph(graph)

    def test_duplicate_dependency_rejected(self):
        graph = sample_graph()
        graph["dependencies"].append(copy.deepcopy(graph["dependencies"][0]))
        with self.assertRaises(EVCValidationError): evaluate_graph(graph)

    def test_duplicate_current_state_rejected(self):
        graph = sample_graph()
        graph["current_state"].append(copy.deepcopy(graph["current_state"][0]))
        with self.assertRaises(EVCValidationError): evaluate_graph(graph)

    def test_unknown_dependency_type_rejected(self):
        graph = sample_graph()
        graph["dependencies"][0]["type"] = "MAGIC_TRUST"
        with self.assertRaises(EVCValidationError): evaluate_graph(graph)

    def test_exact_fields_required(self):
        graph = sample_graph()
        graph["unexpected"] = True
        with self.assertRaises(EVCValidationError): evaluate_graph(graph)

    def test_digest_and_output_independent_of_unordered_array_order(self):
        graph = sample_graph()
        first = evaluate_graph(graph)
        for key in ("claims", "evidence", "current_state", "dependencies"):
            graph[key].reverse()
        self.assertEqual(first, evaluate_graph(graph))

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(EVCValidationError):
            load_graph(b'{"schema_version":"cord-evc-0.1","schema_version":"cord-evc-0.1"}')

    def test_bom_rejected(self):
        with self.assertRaises(EVCValidationError): load_graph(b'\xef\xbb\xbf{}')

    def test_invalid_utf8_rejected(self):
        with self.assertRaises(EVCValidationError): load_graph(b'\xff')

    def test_nan_rejected(self):
        with self.assertRaises(EVCValidationError): load_graph(b'{"x":NaN}')

    def test_oversize_rejected(self):
        from assurance.evc import MAX_GRAPH_BYTES
        with self.assertRaises(EVCValidationError): load_graph(b" " * (MAX_GRAPH_BYTES + 1))

    def test_digest_changes_when_graph_changes(self):
        graph = sample_graph()
        first = evaluate_graph(graph)["graph_sha256"]
        graph["subject"]["version"] = "v2"
        self.assertNotEqual(first, evaluate_graph(graph)["graph_sha256"])

if __name__ == "__main__":
    unittest.main()
