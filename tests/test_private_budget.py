"""Check private Actions job budget caps without using owner PDF content."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "plan_exam_processing.py"


class BudgetPlannerTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)
        self.lookup = self.root / "lookup.json"
        codes = ["AB-900", "AI-103", "AZ-900", "SC-200", "AZ-305"]
        self.lookup.write_text(json.dumps({"exams": {
            code: {"vendor": "microsoft", "urls": ["https://learn.microsoft.com/example/" + code]}
            for code in codes}}), encoding="utf-8")
        for code in codes:
            folder = self.root / "exams" / code
            (folder / "source").mkdir(parents=True)
            (folder / "source" / "owner.pdf").write_bytes(b"%PDF dummy synthetic")
            (folder / "manifest.json").write_text(json.dumps({
                "exam_code": code, "vendor_slug": "microsoft",
                "owner_rights_statement": "Authorized synthetic input",
                "pdf_files": [{"name": "owner.pdf", "sha256": "a" * 64}],
            }), encoding="utf-8")

    def plan(self, limit=2, target="all", exam=""):
        out = self.root / "plan.json"
        p = subprocess.run([sys.executable, str(SCRIPT),
                            "--raw-root", str(self.root), "--lookup", str(self.lookup),
                            "--target", target, "--exam", exam, "--max-exams", str(limit),
                            "--out", str(out)], capture_output=True, text=True)
        return p, json.loads(out.read_text()) if out.exists() else None

    def test_all_mode_limits_private_jobs(self):
        p, report = self.plan(2)
        self.assertEqual(0, p.returncode, p.stderr)
        self.assertEqual(5, report["eligible_total"])
        self.assertEqual(2, report["queued"])
        self.assertEqual(3, report["deferred_budget"])
        self.assertEqual(0, report["blocked"])

    def test_one_mode_selects_only_requested_exam(self):
        p, report = self.plan(1, "one", "AB-900")
        self.assertEqual(0, p.returncode, p.stderr)
        self.assertEqual(["AB-900"], [x["exam"] for x in report["entries"] if x["status"] == "queued"])

    def test_rejects_unbounded_private_fanout(self):
        p, _ = self.plan(46)
        self.assertNotEqual(0, p.returncode)
        self.assertIn("--max-exams", p.stderr + p.stdout)


if __name__ == "__main__":
    unittest.main()
