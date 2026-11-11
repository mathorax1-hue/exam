#!/usr/bin/env python3
"""Create a safe GitHub Actions matrix for private raw-exam inputs.

Only exam identifiers mapped to verified official URLs in the pinned skill
(or specifically supplied through a reviewed manifest) enter preparation.
All other source folders remain visible as blocked, not silently omitted.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import sys

CODE_RX = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{1,79}\Z")
URL_RX = re.compile(r"https://[^\s]+\Z")


def load(path: Path):
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-root", type=Path, required=True)
    ap.add_argument("--lookup", type=Path, required=True)
    ap.add_argument("--target", choices=["all", "one"], default="all")
    ap.add_argument("--exam", default="")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    root = args.raw_root.resolve()
    upstream = load(args.lookup)
    lookups = upstream.get("exams") or {}
    paths = sorted((root / "exams").glob("*/manifest.json"))
    if args.target == "one":
        if not CODE_RX.fullmatch(args.exam):
            raise SystemExit("Invalid requested exam code")
        paths = [p for p in paths if p.parent.name == args.exam]
        if not paths:
            raise SystemExit("Exam is not present in the raw source repo")

    plan = []
    matrix = []
    for path in paths:
        exam = path.parent.name
        item = {"exam": exam, "status": "blocked", "reasons": []}
        try:
            m = load(path)
        except (ValueError, OSError) as e:
            item["reasons"].append("Unreadable manifest")
            plan.append(item)
            continue
        if not CODE_RX.fullmatch(exam):
            item["reasons"].append("unsafe_exam_code")
        if m.get("exam_code") != exam:
            item["reasons"].append("exam_manifest_mismatch")
        if not str(m.get("owner_rights_statement") or "").strip():
            item["reasons"].append("owner_rights_not_recorded")

        pdfs = m.get("pdf_files") or []
        if not isinstance(pdfs, list) or len(pdfs) != 1:
            item["reasons"].append("choose_exactly_one_source_pdf")
        else:
            p = pdfs[0]
            name = p.get("name")
            if not isinstance(name, str) or Path(name).name != name or not name.lower().endswith(".pdf"):
                item["reasons"].append("invalid_pdf_filename")
            elif not (path.parent / "source" / name).is_file():
                item["reasons"].append("pdf_missing_from_git")
            if not re.fullmatch(r"[0-9a-f]{64}", str(p.get("sha256") or "")):
                item["reasons"].append("pdf_sha256_missing")

        official = (m.get("official_exam_url") or "").strip()
        known = lookups.get(exam) or {}
        if not official:
            official = next(iter(known.get("urls") or []), "")
        vendor = str(m.get("vendor_slug") or "").strip()
        if known and vendor and known.get("vendor") != vendor:
            item["reasons"].append("vendor_slug_disagrees_with_pinned_lookup")
        if not known and not m.get("official_exam_url"):
            item["reasons"].append("official_exam_mapping_needed")
        if not URL_RX.fullmatch(official):
            item["reasons"].append("official_exam_url_missing")
        if not re.fullmatch("[a-z][a-z0-9-]*", vendor):
            item["reasons"].append("vendor_slug_invalid")

        # Source aliases are never official exam codes.
        if "-ALT-" in exam or exam.startswith("SF-SALESFORCE-"):
            item["reasons"].append("source_alias_requires_official_code")

        item["official_url_present"] = bool(official)
        item["vendor"] = vendor
        item["has_authoring"] = any((path.parent / "authoring").glob("*.json"))
        if not item["reasons"]:
            item["status"] = "queued"
            matrix.append({"exam": exam})
        plan.append(item)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    report = {"target": args.target, "requested_exam": args.exam, "total": len(plan),
              "queued": len(matrix), "blocked": sum(x["status"] == "blocked" for x in plan),
              "entries": plan}
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    matrix_txt = json.dumps({"include": matrix}, separators=(",", ":"))
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as fh:
            fh.write("matrix=" + matrix_txt + "\n")
            fh.write("queued=" + str(len(matrix)) + "\n")
            fh.write("blocked=" + str(report["blocked"]) + "\n")
    print(f'Exam plan: {len(plan)} sources; {len(matrix)} queued; {report["blocked"]} blocked for source/mapping review')
    return 0


if __name__ == "__main__":
    sys.exit(main())
