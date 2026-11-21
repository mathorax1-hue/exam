"""Guards the public workflow pin and the public-run refusal."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PIN = "d9b6bf67efb870019dd88caeffa90952b7e000d3"


class ThreePhaseWorkflowTests(unittest.TestCase):
    def test_synthetic_qa_uses_v130(self):
        text = (ROOT / ".github/workflows/certpassly.yml").read_text(encoding="utf-8")
        self.assertIn(PIN, text)
        self.assertNotIn("13dea6bab662ab1c4bbf87017e912e519907c8bc", text)

    def test_reusable_workflow_refuses_public_dispatch(self):
        text = (ROOT / ".github/workflows/three-phase-exam.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_call", text)
        self.assertIn("Refuse a real exam on the public repository", text)
        self.assertIn(PIN, text)
        self.assertIn("github.event.repository.private == true", text)


if __name__ == "__main__":
    unittest.main()
