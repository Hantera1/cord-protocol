import unittest

from verifier.chain import ZERO_HASH, create_event, verify_chain
from verifier.verify import CordValidationError


class CordChainTests(unittest.TestCase):
    def test_valid_chain_and_checkpoint(self):
        first = create_event(0, ZERO_HASH, "a" * 64, "2026-03-06T12:00:00Z")
        second = create_event(1, first["event_hash"], "b" * 64, "2026-03-06T12:01:00Z")
        result = verify_chain([first, second], expected_head=second["event_hash"])
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["events"], 2)

    def test_tampered_event_fails(self):
        first = create_event(0, ZERO_HASH, "a" * 64, "2026-03-06T12:00:00Z")
        first["receipt_hash"] = "c" * 64
        with self.assertRaises(CordValidationError):
            verify_chain([first])

    def test_wrong_checkpoint_fails(self):
        first = create_event(0, ZERO_HASH, "a" * 64, "2026-03-06T12:00:00Z")
        with self.assertRaises(CordValidationError):
            verify_chain([first], expected_head="f" * 64)

    def test_reordering_or_missing_predecessor_fails(self):
        first = create_event(0, ZERO_HASH, "a" * 64, "2026-03-06T12:00:00Z")
        second = create_event(1, first["event_hash"], "b" * 64, "2026-03-06T12:01:00Z")
        with self.assertRaises(CordValidationError):
            verify_chain([second])

    def test_boolean_sequence_rejected(self):
        with self.assertRaises(CordValidationError):
            create_event(True, ZERO_HASH, "a" * 64, "2026-03-06T12:00:00Z")

    def test_non_integer_sequence_rejected(self):
        with self.assertRaises(CordValidationError):
            create_event("0", ZERO_HASH, "a" * 64, "2026-03-06T12:00:00Z")

    def test_invalid_expected_head_rejected(self):
        with self.assertRaises(CordValidationError):
            verify_chain([], expected_head="not-a-hash")


if __name__ == "__main__":
    unittest.main()
