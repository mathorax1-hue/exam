"""Prevent fabricated official names in the private CertPassly exam workflow."""
import csv
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import process_raw_exam as P


class OfficialNameTests(unittest.TestCase):
    URL = "https://learn.microsoft.com/en-us/credentials/certifications/exams/AB-900"
    NAME = "Microsoft 365 Certified: Copilot and Agent Administration Fundamentals"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        research = self.root / "research" / "microsoft"
        research.mkdir(parents=True)
        (research / "AB-900.sources.json").write_text(json.dumps({
            "sources": [{"id": "cp", "url": self.URL}]}), encoding="utf-8")
        sources = self.root / "sources" / "microsoft"
        sources.mkdir(parents=True)
        self.html = sources / "official.html"
        body = ("<!DOCTYPE html><html><body><h1>" + self.NAME +
                "</h1><p>Exam AB-900</p></body></html>")
        self.html.write_text(body, encoding="utf-8")
        self.meta = sources / "official.html.json"
        self.meta.write_text(json.dumps({
            "url": self.URL,
            "sha256": hashlib.sha256(self.html.read_bytes()).hexdigest(),
        }), encoding="utf-8")
        with (self.root / "catalog.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=P.COLUMNS)
            writer.writeheader()
            writer.writerow({"exam_code": "AB-900", "vendor_slug": "microsoft"})

    def test_accepts_sha_verified_microsoft_title(self):
        name, url, digest = P.verified_microsoft_certification_name(self.root, "AB-900")
        self.assertEqual(self.NAME, name)
        self.assertEqual(self.URL, url)
        self.assertEqual(hashlib.sha256(self.html.read_bytes()).hexdigest(), digest)
        result = self.root / "result"
        result.mkdir()
        self.assertTrue(P.add_verified_official_name(self.root, "AB-900", "microsoft", result))
        with (self.root / "catalog.csv").open(newline="", encoding="utf-8") as f:
            self.assertEqual(self.NAME, list(csv.DictReader(f))[0]["exam_name"])

    def test_tampered_source_does_not_qualify(self):
        self.html.write_text("<h1>Microsoft Certified: Fake Test</h1>", encoding="utf-8")
        self.assertIsNone(P.verified_microsoft_certification_name(self.root, "AB-900"))

    def test_nonofficial_url_does_not_qualify(self):
        research = self.root / "research" / "microsoft" / "AB-900.sources.json"
        research.write_text(json.dumps({
            "sources": [{"id": "cp", "url": "https://example.org/exams/AB-900"}]}),
            encoding="utf-8")
        self.assertIsNone(P.verified_microsoft_certification_name(self.root, "AB-900"))

    def test_other_vendor_is_not_assigned_microsoft_title(self):
        self.assertFalse(P.add_verified_official_name(self.root, "AB-900", "salesforce", self.root))


if __name__ == "__main__":
    unittest.main()
