"""Synthetic tests prove editorial originals keep owner slots and provenance."""
import json
from pathlib import Path
import tempfile
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
from validate_editorial_overrides import validate

class EditorialOverrideTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)
        self.owner=self.p/"split.json"
        self.stage=self.p/"questions.json"
        self.ledger=self.p/"ledger.json"
        self.items=[{"question_key":"q001","publication_state":"draft","source_pdf_pages":[1]},
                    {"question_key":"cp-ab900-q002-r1","replaces_owner_item_key":"q002",
                     "publication_state":"draft","source_pdf_pages":[]}]
        self.entries=[{"original_owner_question_id":"q002","new_question_key":"cp-ab900-q002-r1",
                       "author":"CertPassly Team", "approved_for_publication":False,
                       "not_in_owner_pdf":True, "stem":"Original practice question",
                       "core_explanation":"Source-backed original explanation",
                       "official_sources":["https://learn.microsoft.com/example"]}]
    def write(self):
        self.owner.write_text(json.dumps({"q001":{"stem":"one"},"q002":{"stem":"two"}}))
        self.stage.write_text(json.dumps({"question_count":2,"questions":self.items}))
        self.ledger.write_text(json.dumps({"replacement_count":len(self.entries),
                                           "replacement_questions":self.entries}))
    def test_good_source_preserving_replacement(self):
        self.write();r=validate(self.owner,self.stage,self.ledger)
        self.assertEqual(2,r["active_count"])
        self.assertEqual(1,r["original_replacement_count"])
        self.assertFalse(r["ready_for_publication"])
    def test_untracked_rewrite_rejected(self):
        self.items[0]["question_key"]="new-untracked"
        self.write()
        with self.assertRaises(ValueError):validate(self.owner,self.stage,self.ledger)
    def test_unapproved_origin_rejected(self):
        self.entries[0]["approved_for_publication"]=True
        self.write()
        with self.assertRaises(ValueError):validate(self.owner,self.stage,self.ledger)
    def test_duplicate_owner_source_rejected(self):
        self.entries.append(dict(self.entries[0],new_question_key="cp-ab900-q002-r2"))
        self.write()
        with self.assertRaises(ValueError):validate(self.owner,self.stage,self.ledger)
    def test_reviewer_origin_missing_rejected(self):
        self.items[1].pop("replaces_owner_item_key")
        self.write()
        with self.assertRaises(ValueError):validate(self.owner,self.stage,self.ledger)

if __name__=="__main__":
    unittest.main()
