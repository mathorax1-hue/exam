#!/usr/bin/env python3
"""Prove that a mixed owner/original staging bank preserves its source provenance.

This is a safe preflight, NOT an alternative to the pinned CertPassly release
gates. It cannot be used to assert official factual correctness or human review.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

CODE = re.compile(r"[a-z0-9][a-z0-9._-]{1,90}\Z", re.I)
def fail(reason):
    raise ValueError(reason)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def validate(owner: Path, staged: Path, ledger: Path):
    a, b, c = load(owner), load(staged), load(ledger)
    if not isinstance(a, dict) or not isinstance(b, dict):
        fail("Owner split and staged bank must be JSON objects")
    questions = b.get("questions")
    overrides = c.get("replacement_questions")
    if not isinstance(questions, list) or not isinstance(overrides, list):
        fail("Missing staged questions or original replacement list")
    if len(a) != len(questions):
        fail("Source/staged count mismatch; no silent deletions allowed")
    if b.get("question_count", len(questions)) != len(questions):
        fail("Staged question count metadata mismatch")
    owner_keys = list(a)
    active_keys = [q.get("question_key") for q in questions]
    if len(set(active_keys)) != len(active_keys):
        fail("Duplicate active question key")
    seen = set()
    mapped = {}
    for record in overrides:
        old, new = record.get("original_owner_question_id"), record.get("new_question_key")
        if old in seen or not isinstance(old, str) or old not in a:
            fail(f"Unknown or duplicate replacement source ID: {old}")
        seen.add(old)
        if not isinstance(new, str) or not CODE.fullmatch(new) or new == old or new in a:
            fail(f"Original replacement code unsafe or conflicts with owner ID: {new}")
        if record.get("author") != "CertPassly Team":
            fail("Only CertPassly Team can be the original editorial credit")
        if record.get("approved_for_publication") is not False:
            fail("Original replacements cannot arrive auto-approved")
        if not record.get("not_in_owner_pdf"):
            fail("Original replacement origin must be explicitly recorded")
        urls = record.get("official_sources")
        if not isinstance(urls, list) or not urls or any(
            not isinstance(u, str) or not u.startswith("https://learn.microsoft.com/")
            and not u.startswith("https://support.microsoft.com/") for u in urls
        ):
            fail(f"Missing or nonofficial vendor URL for {new}")
        if not record.get("core_explanation"):
            fail("Original replacement has no explanation")
        if not record.get("stem"):
            fail("Original replacement has no stem")
        if new in mapped:
            fail("Duplicate new question ID")
        mapped[new] = old
    if len(active_keys) != len(a):
        fail("Cannot alter source question slots")
    for idx, (old, new) in enumerate(zip(owner_keys, active_keys)):
        q = questions[idx]
        if new in mapped:
            if mapped[new] != old or q.get("replaces_owner_item_key") != old:
                fail(f"Replacement position/provenance mismatch at {old}")
            if q.get("publication_state") != "draft":
                fail("An original replacement is not in draft state")
            if q.get("source_pdf_pages"):
                fail("New original must not claim the owner PDF pages as its origin")
        elif new != old:
            fail(f"Untracked source question substitution at slot {idx+1}")
    if not set(mapped).issubset(set(active_keys)):
        fail("Missing original replacement in staged question list")
    if c.get("replacement_count") != len(overrides):
        fail("Replacement count in editorial ledger mismatch")
    return {
        "status": "source_provenance_preflight_passed_not_release_approval",
        "source_count": len(a),
        "active_count": len(questions),
        "original_replacement_count": len(overrides),
        "owner_split_sha256": sha(owner),
        "staged_questions_sha256": sha(staged),
        "editorial_ledger_sha256": sha(ledger),
        "source_replacement_map": {old:new for new,old in sorted(mapped.items(), key=lambda t:t[1])},
        "publisher": "CertPassly Team",
        "human_review_status": "pending",
        "pinned_pipeline_all_stages_passed": False,
        "ready_for_publication": False,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner-split", required=True, type=Path)
    ap.add_argument("--staged-questions", required=True, type=Path)
    ap.add_argument("--editorial-ledger", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    try:
        result=validate(args.owner_split, args.staged_questions, args.editorial_ledger)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2)+"\n", encoding="utf-8")
        print("PASS 89-slot source-provenance mapping preflight; not a release approval.")
        return 0
    except (OSError, TypeError, ValueError, KeyError) as exc:
        print(f"FAIL editorial source override: {exc}",file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
