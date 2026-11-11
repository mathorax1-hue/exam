#!/usr/bin/env python3
"""Create traceable proof bundle only after all pinned CertPassly stages pass.

Called by private raw-exam Actions. Never uses real owner source content in
the public processor repository, and never treats a draft as published.
"""
from __future__ import annotations
import argparse
import collections
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

PIN = "13dea6bab662ab1c4bbf87017e912e519907c8bc"
REQUIRED_STAGES = ["catalog", "intake", "extract", "sources", "research",
                   "textfix", "answer_research", "intent",
                   "author", "pages", "writing", "import", "bank", "validate", "package"]
EVIDENCE_NAMES = ["stage-results.json", "source-provenance.json",
                  "official-sources.json", "question-audit.json",
                  "validation.json", "writing-review.json",
                  "bank-check.log", "import-conformance.log"]
REVIEW_FLAGS = re.compile(r"wrong|outdated|arguable|could_not|unverified|needs_review|dispute|inaccurate", re.I)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as s:
        for chunk in iter(lambda: s.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def add_output(value):
    p = os.environ.get("GITHUB_OUTPUT")
    if p:
        with open(p, "a", encoding="utf-8") as f:
            f.write(f"ready={str(value).lower()}\n")


def factual_quotes(obj, path=""):
    """Select only sourced facts from the official research record."""
    facts = []
    if isinstance(obj, dict):
        if all(k in obj for k in ("url", "sha256", "quote", "value")) and obj.get("value") is not None:
            facts.append({
                "field": path,
                "value": obj["value"],
                "url": obj["url"],
                "sha256": obj["sha256"],
                "quote": obj["quote"],
            })
        else:
            for key, value in obj.items():
                if key in ("sources", "source_path", "saved_html", "extra"):
                    continue
                facts.extend(factual_quotes(value, f"{path}.{key}".strip(".")))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            facts.extend(factual_quotes(value, f"{path}[{i}]"))
    return facts


def question_audit(code, out):
    path = out / "questions.json"
    bank = load(path)
    questions = bank.get("questions")
    if not isinstance(questions, list) or not questions:
        raise ValueError("No built questions in the verified question bank")
    types = collections.Counter(str(q.get("question_type") or q.get("type") or "unknown") for q in questions)
    held = bank.get("held_for_review") or []
    excluded = bank.get("scoring_excluded_question_keys") or []
    unverified = sum(bool(REVIEW_FLAGS.search(str(q.get("answer_key_status") or "")))
                     or q.get("verification_status") == "unverified"
                     for q in questions)
    flagged = sum(bool(REVIEW_FLAGS.search(str(q.get("accuracy_status") or "")))
                  for q in questions)
    human = sum(q.get("human_review_required") is True for q in questions)
    not_found = sum(q.get("answer_key_status") == "answer_not_found" for q in questions)
    proof = {
        "exam": code, "built_questions_sha256": sha(path),
        "total_questions": len(questions), "types": dict(types),
        "held_count": len(held),
        "scoring_excluded_count": len(excluded),
        "answer_not_found_count": not_found,
        "unverified_key_count": unverified,
        "flagged_accuracy_count": flagged,
        "human_review_required_count": human,
        "open_owner_review_count": max(len(held), human, unverified, flagged, not_found, len(excluded)),
        "status": "draft",
    }
    return proof


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw-root", required=True, type=Path)
    p.add_argument("--workspace", required=True, type=Path)
    p.add_argument("--exam", required=True)
    p.add_argument("--results", required=True, type=Path)
    p.add_argument("--source-commit", required=True)
    p.add_argument("--processor-commit", required=True)
    args = p.parse_args()
    resdir = args.results.resolve()
    results = resdir / "status.json"
    if not results.is_file():
        raise SystemExit("Cannot locate per-exam processing status")
    status = load(results)
    if status.get("ready_for_promotion") is not True or status.get("status") != "validated_draft":
        print(f"{args.exam}: no full release claim; current status={status.get('status')}")
        add_output(False)
        return 0
    # A strict release audit only runs on exam packages already built by the
    # pinned skill. It can downgrade a draft if any unresolved proof exists.
    code = args.exam
    ws = args.workspace.resolve()
    out = ws / "out" / code
    source = args.raw_root.resolve() / "exams" / code
    manifest = load(source / "manifest.json")
    release_file = resdir / "release.json"
    release = load(release_file)
    proofdir = resdir / "proofs"
    proofdir.mkdir(parents=True, exist_ok=True)
    problems = []
    stage_list = status.get("stages", [])
    if [x.get("name") for x in stage_list] != REQUIRED_STAGES or any(x.get("exit_code") != 0 for x in stage_list):
        problems.append("incomplete_or_failed_stage_sequence")
    stages = {"stages": stage_list, "conformance_exit_code": status.get("conformance_exit_code")}
    write_json(proofdir / "stage-results.json", stages)
    if status.get("conformance_exit_code") != 0:
        problems.append("import_conformance_failed")

    validation = load(out / "validation.json")
    if not isinstance(validation, list) or not validation or any(v.get("passed") is not True for v in validation):
        problems.append("validation_report_failed")
    write_json(proofdir / "validation.json", validation)
    if len(validation) < 60:
        problems.append("validation_report_has_too_few_checks")

    writing = load(out / "writing-review.json")
    write_json(proofdir / "writing-review.json", writing)
    if writing.get("flag_count") != 0 or not re.fullmatch(r"[0-9a-f]{64}", str(writing.get("inputs_sha256", ""))):
        problems.append("writing_review_open_or_stale")

    banklog = resdir / "stage-validate.log"
    if not banklog.is_file():
        problems.append("missing_check_bank_log")
    else:
        log = banklog.read_text(encoding="utf-8", errors="replace")
        m = re.findall(r"Summary:\s*(\d+) passed,\s*(\d+) failed,\s*(\d+) total", log)
        if not m or int(m[-1][0]) <= 0 or int(m[-1][1]) != 0 or int(m[-1][2]) != int(m[-1][0]):
            problems.append("check_bank_not_zero_fail")
        shutil.copyfile(banklog, proofdir / "bank-check.log")
    conformance = resdir / "conformance.log"
    if conformance.is_file():
        shutil.copyfile(conformance, proofdir / "import-conformance.log")
    else:
        problems.append("missing_import_conformance_log")

    audit = question_audit(code, out)
    write_json(proofdir / "question-audit.json", audit)
    for k in ("held_count", "answer_not_found_count", "unverified_key_count",
              "flagged_accuracy_count", "human_review_required_count",
              "scoring_excluded_count"):
        if audit[k]:
            problems.append(f"unresolved_question_review:{k}={audit[k]}")
    research_file = ws / "research" / manifest["vendor_slug"] / f"{code}.json"
    research = load(research_file)
    sources = research.get("sources") or []
    official_sources = [{
        "id": str(s.get("id") or ""),
        "url": str(s.get("url") or ""),
        "expected_sha256": str(s.get("expected_sha256") or ""),
        "retrieved_date": str(s.get("as_of_date") or ""),
    } for s in sources]
    facts = factual_quotes({"exam_name": research.get("exam_name"), "facts": research.get("facts"),
                            "objectives": research.get("objectives")})
    info = {"exam": code, "sources": official_sources,
            "quoted_fact_count": len(facts), "quoted_facts": facts}
    write_json(proofdir / "official-sources.json", info)
    hashes = {s["expected_sha256"] for s in official_sources}
    if not official_sources or not facts:
        problems.append("official_fact_evidence_missing")
    if any(not re.fullmatch(r"[0-9a-f]{64}", s["expected_sha256"]) for s in official_sources):
        problems.append("official_source_hash_missing")
    if any(not f.get("quote") or f.get("sha256") not in hashes for f in facts):
        problems.append("official_fact_quote_not_bound_to_source")

    pdf = manifest["pdf_files"][0]
    owner_file = source / "source" / pdf["name"]
    proof_source = {"exam": code, "source_repo_commit": args.source_commit,
                    "source_manifest_sha256": sha(source / "manifest.json"),
                    "owner_pdf_sha256": pdf["sha256"],
                    "owner_pdf_bytes": pdf["bytes"],
                    "rights_confirmation_recorded": bool(manifest.get("owner_rights_statement")),
                    "processor_code_commit": args.processor_commit,
                    "skill_pin": PIN}
    if sha(owner_file) != pdf["sha256"]:
        problems.append("owner_pdf_hash_mismatch")
    write_json(proofdir / "source-provenance.json", proof_source)
    if release.get("owner_pdf_sha256") != pdf["sha256"]:
        problems.append("release_pdf_hash_mismatch")

    scanfile = resdir / f"{code}-package.zip.scan.json"
    scan = load(scanfile)
    if scan.get("passed") is not True or scan.get("hit_count") != 0:
        problems.append("package_scan_not_clean")
    if problems:
        status["status"] = "needs_human_or_evidence_review"
        status["reason"] = "; ".join(problems)[:1000]
        status["ready_for_promotion"] = False
        status["audit_blockers"] = problems
        write_json(results, status)
        add_output(False)
        print(f"{code}: not promoted; {len(problems)} evidence or review blockers: {'; '.join(problems)}")
        return 0

    files = {}
    for name in EVIDENCE_NAMES:
        file = proofdir / name
        if not file.is_file():
            raise ValueError(f"Required proof absent: {name}")
        files[f"proofs/{name}"] = {"sha256": sha(file), "size_bytes": file.stat().st_size}
    files[scanfile.name] = {"sha256": sha(scanfile), "size_bytes": scanfile.stat().st_size}
    evidence_manifest = {
        "contract_version": 1, "exam": code,
        "files": files,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Audit proof for an evidence-backed validated draft, not production approval",
    }
    manifest_file = resdir / "evidence-manifest.json"
    write_json(manifest_file, evidence_manifest)
    release.update({
        "contract_version": 1, "publication_state": "draft", "published": False,
        "human_review_status": "pending", "ready_for_publication": False,
        "processor_code_commit": args.processor_commit,
        "evidence_manifest_sha256": sha(manifest_file),
        "validation_check_count": len(validation), "validation_failures": 0,
        "verified_question_count": audit["total_questions"],
        "evidence_quality_gate": "passed",
        "package_scan_hits": 0,
    })
    write_json(release_file, release)
    add_output(True)
    print(f"{code}: strict proof gates passed; evidence-backed validated draft can be promoted")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"Release evidence build failed: {e}", file=sys.stderr)
        sys.exit(1)
