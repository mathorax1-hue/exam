"""Synthetic checks for the public processing-to-proof adapter."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_release_evidence as E


class EvidenceBuilderTests(unittest.TestCase):
    def test_collects_only_facts_with_official_evidence(self):
        data = {
            "facts": {
                "passing_score": {
                    "value": 700, "url": "https://example.org/official",
                    "sha256": "a" * 64, "quote": "The passing score is 700."
                },
                "duration": {"value": None, "reason": "not published by the vendor"}
            }
        }
        facts = E.factual_quotes(data)
        self.assertEqual(1, len(facts))
        self.assertIn("passing_score", facts[0]["field"])
        self.assertEqual(700, facts[0]["value"])

    def test_detects_unreviewed_question(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            data = {"questions": [
                {"question_type": "single_choice",
                 "answer_key_status": "as_in_source_file",
                 "accuracy_status": "key_ok",
                 "human_review_required": False},
                {"question_type": "image_based_choice",
                 "answer_key_status": "researched_unverified",
                 "verification_status": "unverified",
                 "accuracy_status": "key_could_not_be_checked",
                 "human_review_required": True}
            ], "held_for_review": [], "scoring_excluded_question_keys": []}
            (out / "questions.json").write_text(json.dumps(data), encoding="utf-8")
            proof = E.question_audit("AB-900", out)
            self.assertEqual(2, proof["total_questions"])
            self.assertEqual(1, proof["unverified_key_count"])
            self.assertEqual(1, proof["flagged_accuracy_count"])
            self.assertEqual(1, proof["human_review_required_count"])
            self.assertEqual(0, proof["scoring_excluded_count"])


if __name__ == "__main__":
    unittest.main()
