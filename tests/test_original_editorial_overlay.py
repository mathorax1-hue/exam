"""Synthetic tests: originals must never impersonate owner PDF questions."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import process_raw_exam as P


class OverlayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.raw = self.root / "raw"
        (self.raw / "authoring").mkdir(parents=True)
        self.res = self.root / "proof"
        self.res.mkdir()
        self.out = self.root / "work" / "out" / "AB-900" / "extracted"
        self.out.mkdir(parents=True)
        self.pdfsha = "e" * 64
        self.write(self.raw / "manifest.json",
                   {"pdf_files": [{"sha256": self.pdfsha}]})
        self.write(self.out / "split.json", {
            "q001": {"question_key": "q001", "source_number": 1,
                     "marker": "QUESTION 1", "pages": [1], "stem": "Owner original text",
                     "options": {"a": "old", "b": "source"},
                     "answer_raw": "A", "question_images": [], "answer_images": []},
            "q002": {"question_key": "q002", "source_number": 2,
                     "marker": "QUESTION 2", "pages": [2], "stem": "Owner original hotspot",
                     "options": {}, "answer_raw": "",
                     "question_images": ["question.png"], "answer_images": ["marked.png"]},
        })
        self.write(self.out / "visual_draft.json", {"q002": {"key": ["no", "no"]}})
        self.write(self.raw / "visual_transcription.json", {
            "q002": {"rows": ["A true statement", "A false statement"], "key": ["yes", "no"]}})
        self.rows = [
            {"original_owner_question_id": "q001",
             "new_question_key": "cp-ab900-q001-r1", "author": "CertPassly Team",
             "not_in_owner_pdf": True, "approved_for_publication": False,
             "official_sources": ["https://learn.microsoft.com/en-us/demo"],
             "type": "single_choice",
             "stem": "Which option correctly describes a supported official Microsoft feature?",
             "options": [{"id": "a", "text": "The supported option"},
                         {"id": "b", "text": "An unsupported option"}],
             "correct_option_id": "a"},
            {"original_owner_question_id": "q002",
             "new_question_key": "cp-ab900-q002-r1", "author": "CertPassly Team",
             "not_in_owner_pdf": True, "approved_for_publication": False,
             "official_sources": ["https://learn.microsoft.com/en-us/demo2"],
             "type": "yes_no_matrix",
             "stem": "For each statement, select Yes if it is correct. Otherwise, select No.",
             "rows": ["A true statement", "A false statement"],
             "correct_responses": ["yes", "no"]},
        ]
        self.save_replacements()

    def write(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def save_replacements(self):
        self.write(self.raw / "authoring" / "original_editorial_replacements.json", {
            "exam_code": "AB-900", "author": "CertPassly Team",
            "owner_pdf_sha256": self.pdfsha,
            "publication_state": "EDITORIAL_REPLACEMENT_DRAFT_NOT_RELEASED",
            "replacement_questions": self.rows, "replacement_count": len(self.rows)})

    def test_overlay_requires_source_coverage_and_preserves_provenance(self):
        p = P.apply_original_editorial_overlay(self.root / "work", self.raw,
                                                "AB-900", self.res)
        self.assertEqual(2, p["count"])
        self.assertEqual(2, len(P.load_json(self.out / "split.json")))
        question1 = P.load_json(self.out / "split.json")["q001"]
        question2 = P.load_json(self.out / "split.json")["q002"]
        self.assertEqual("A", question1["answer_raw"])
        self.assertEqual([], question1["question_images"])
        self.assertEqual([], question2["answer_images"])
        self.assertIn("select Yes if the statement is true", question2["stem"])
        self.assertEqual({}, P.load_json(self.out / "visual_draft.json"))
        self.assertTrue((self.res / "editorial-overlay-evidence.json").is_file())
        self.assertEqual({"q002"}, set(P.load_json(self.out / "visual_transcription.json")))
        self.assertFalse(p["ready_for_publication"])

    def test_unsourced_original_is_rejected(self):
        self.rows[0]["official_sources"] = ["https://example.com/claims"]
        self.save_replacements()
        with self.assertRaisesRegex(ValueError, "official source URLs"):
            P.apply_original_editorial_overlay(self.root / "work", self.raw,
                                                "AB-900", self.res)

    def test_missing_visual_transcription_is_rejected(self):
        self.rows[1]["rows"].append("Third row")
        self.rows[1]["correct_responses"].append("no")
        self.save_replacements()
        with self.assertRaisesRegex(ValueError, "rows differ"):
            P.apply_original_editorial_overlay(self.root / "work", self.raw,
                                                "AB-900", self.res)

    def test_corrects_final_bank_provenance_without_approving_it(self):
        overlay = P.apply_original_editorial_overlay(self.root / "work", self.raw,
                                                       "AB-900", self.res)
        out = self.root / "work" / "out" / "AB-900"
        self.write(out / "questions.json",
                   {"questions": [{"question_key": "q001"}, {"question_key": "q002"}]})
        csv_path = out / "import" / "questions.csv"
        csv_path.parent.mkdir()
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=["question_key", "author_key",
                                                     "created_source", "review_gate",
                                                     "publication_state", "blocking_reason"])
            writer.writeheader()
            for k in ("q001", "q002"):
                writer.writerow({"question_key": k, "created_source": "owner_file"})
        P.identify_originals_after_bank(self.root / "work", "AB-900", overlay)
        result = P.load_json(out / "questions.json")["questions"]
        self.assertTrue(all(x["human_review_required"] for x in result))
        self.assertTrue(all(x["key_source"] == "certpassly_team_original_unverified"
                            for x in result))
        with csv_path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertTrue(all(x["author_key"] == "CertPassly Team" for x in rows))
        self.assertTrue(all(x["publication_state"] == "draft" for x in rows))


if __name__ == "__main__":
    unittest.main()
