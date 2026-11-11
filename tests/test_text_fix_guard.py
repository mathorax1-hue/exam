"""Synthetic regression tests for safe automatic text-fix subsets."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from process_raw_exam import guarded_text_fix_config

ORIGINAL = """brand: CertPassly
text_fixes:
  enabled: true
  auto:
    - lost_ligature
    - repeated_word
    - space_before_punct
    - double_space
owner_rights_statement: "Authorized"
"""


class TextFixGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)

    def put(self, kinds, exam="AB-900"):
        (self.dir / "processing_overrides.json").write_text(
            json.dumps({"exam": exam, "text_fixes_auto": kinds}), encoding="utf-8")

    def test_default_is_unchanged(self):
        self.assertEqual(ORIGINAL, guarded_text_fix_config(ORIGINAL, self.dir, "AB-900"))

    def test_disable_repeated_word_for_product_name(self):
        self.put(["lost_ligature", "space_before_punct", "double_space"])
        updated = guarded_text_fix_config(ORIGINAL, self.dir, "AB-900")
        self.assertIn("    - space_before_punct", updated)
        self.assertNotIn("    - repeated_word", updated)
        self.assertIn('owner_rights_statement: "Authorized"', updated)

    def test_mismatched_code_rejected(self):
        self.put(["double_space"], exam="AZ-900")
        with self.assertRaises(ValueError):
            guarded_text_fix_config(ORIGINAL, self.dir, "AB-900")

    def test_unsafe_fix_type_rejected(self):
        self.put(["replace_answer_key"])
        with self.assertRaises(ValueError):
            guarded_text_fix_config(ORIGINAL, self.dir, "AB-900")


if __name__ == "__main__":
    unittest.main()
