"""Public synthetic tests: original PDF screenshot roles after editorial replacements."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_release_evidence import audit_active_visual_roles


def role(qid, typ, page, xref, **flags):
    return {"question_key": qid, "role": typ, "page": page, "xref": xref,
            "approved_for_release": False, "answer_verified": False,
            "may_display_before_submission": False, **flags}


Q = "question_prompt_candidate"
A = "answer_reference_never_show_before_submission"


class VisualRoleTests(unittest.TestCase):
    def setUp(self):
        self.split = {
            "q001": {"question_images": ["p-3_1.jpg"], "answer_images": ["p-4_1.jpg"]},
            # This owner question was replaced with an original text-only item.
            "q002": {"question_images": [], "answer_images": []},
            "q003": {"question_images": ["p-5_1.png"], "answer_images": []},
        }
        self.roles = {"image_roles": [
            role("q001", Q, 3, 6),
            role("q001", A, 4, 10),
            role("q002", Q, 4, 11),
            role("q002", A, 5, 15),
            role("q003", Q, 5, 16),
            {"role": "cover_decoration", "question_key": None, "page": 1, "xref": 509},
        ]}

    def test_superseded_images_do_not_count_as_active(self):
        result = audit_active_visual_roles(self.split, self.roles)
        self.assertEqual(3, result["active_image_reference_count"])
        self.assertEqual(3, result["active_role_coverage_count"])
        self.assertEqual(2, result["superseded_owner_image_reference_count"])
        self.assertEqual(2, result["active_question_image_count"])
        self.assertEqual(1, result["active_answer_reference_count"])
        self.assertEqual(1, result["unverified_active_answer_reference_count"])
        self.assertEqual(0, result["pre_submission_answer_leak_count"])
        self.assertEqual([], result["role_mapping_issues"])

    def test_correct_count_wrong_role_does_not_pass(self):
        self.roles["image_roles"][0]["role"] = A
        result = audit_active_visual_roles(self.split, self.roles)
        self.assertEqual(3, result["active_image_reference_count"])
        self.assertEqual(3, result["active_role_coverage_count"])
        self.assertTrue(result["role_mapping_issues"], "Must reject prompt/answer role swap")

    def test_unreviewed_key_is_not_mislabeled_as_answer_leak(self):
        result = audit_active_visual_roles(self.split, self.roles)
        self.assertEqual(1, result["unverified_active_answer_reference_count"])
        self.assertEqual(0, result["pre_submission_answer_leak_count"])

    def test_explicit_answer_exposure_is_blocked(self):
        self.roles["image_roles"][1]["may_display_before_submission"] = True
        result = audit_active_visual_roles(self.split, self.roles)
        self.assertEqual(1, result["pre_submission_answer_leak_count"])

    def test_duplicate_pdf_images_fail(self):
        self.roles["image_roles"].append(self.roles["image_roles"][0].copy())
        result = audit_active_visual_roles(self.split, self.roles)
        self.assertTrue(result["role_mapping_issues"])

    def test_changed_active_question_count_fails(self):
        self.split["q003"]["answer_images"].append("not-from-owner.jpg")
        result = audit_active_visual_roles(self.split, self.roles)
        self.assertTrue(result["role_mapping_issues"])


if __name__ == "__main__":
    unittest.main()
