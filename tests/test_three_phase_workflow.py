"""Guards the public workflow pin and the public-run refusal."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PIN = "c8d4400598c225c6a32f029f28ca24429649edd6"


class ThreePhaseWorkflowTests(unittest.TestCase):
    def test_synthetic_qa_pin_is_not_pre_v130(self):
        text = (ROOT / ".github/workflows/certpassly.yml").read_text(encoding="utf-8")
        self.assertNotIn("13dea6bab662ab1c4bbf87017e912e519907c8bc", text)
        self.assertRegex(text, r"ref:\s+[0-9a-f]{40}")

    def test_reusable_workflow_refuses_public_dispatch(self):
        text = (ROOT / ".github/workflows/three-phase-exam.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_call", text)
        self.assertIn("Refuse a non-owner or forked run", text)
        self.assertIn(PIN, text)
        self.assertIn('[A-Za-z0-9][A-Za-z0-9._-]{1,39}', text)
        self.assertIn("github.repository == 'mathorax1-hue/exam'", text)
        self.assertIn("github.event.repository.fork == false", text)
        self.assertIn("Apply skill patches to pinned upstream", text)
        self.assertIn("skill/patches/upstream/v1.3.1-", text)


if __name__ == "__main__":
    unittest.main()
