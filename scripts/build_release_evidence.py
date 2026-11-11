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
REVIEW_FLAGS = re.compile(r"wrong|outdated|arguable|could_not|unverified|needs_review|dispute|inaccurate|flagged|not_checked|pending|missing", re.I)


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



def audit_active_visual_roles(split: dict, role_manifest: dict) -> dict:
    """Compare active post-replacement image slots to the original PDF role inventory.

    Removed originals must not be counted as live screenshot assets, but their
    provenance is retained. Matching is by original source question key and by
    separate question/answer counts, not by a total that can hide swapped roles.
    """
    records = role_manifest.get("image_roles")
    if not isinstance(records, list):
        raise ValueError("Visual role inventory must be a list")
    grouped = collections.defaultdict(list)
    for rec in records:
        if not isinstance(rec, dict):
            raise ValueError("Malformed original PDF visual role record")
        if rec.get("role") in (
            "question_prompt_candidate", "answer_reference_never_show_before_submission"
        ):
            grouped[rec.get("question_key")].append(rec)
    active, superseded, issues = [], [], []
    if not isinstance(split, dict) or not split:
        raise ValueError("No extracted question mapping to audit")
    expected_total = 0
    for qid, question in split.items():
        if not isinstance(question, dict):
            issues.append(f"{qid}:invalid_question")
            continue
        expected = {
            "question_prompt_candidate": len(question.get("question_images") or []),
            "answer_reference_never_show_before_submission": len(question.get("answer_images") or [])
        }
        expected_total += sum(expected.values())
        current = grouped.pop(qid, [])
        if sum(expected.values()) == 0:
            superseded.extend(current)
            continue
        for role, count in expected.items():
            rows = [x for x in current if x["role"] == role]
            if count != len(rows):
                issues.append(f"{qid}:{role}:expected_{count}:mapped_{len(rows)}")
            active.extend(rows)
    # Original PDF roles for a question no longer in the active bank cannot
    # be silently promoted as active. They remain traceable as superseded.
    for qid, leftovers in grouped.items():
        superseded.extend(leftovers)
        if qid in split:
            issues.append(f"{qid}:unexpected_unmapped_source_role")
    identities = [(a.get("question_key"), a.get("page"), a.get("xref")) for a in active]
    if len(identities) != len(set(identities)):
        issues.append("duplicate_active_pdf_image_xref")
    return {
        "active_image_reference_count": expected_total,
        "active_role_coverage_count": len(active),
        "active_question_image_count": sum(x["role"] == "question_prompt_candidate" for x in active),
        "active_answer_reference_count": sum(x["role"] == "answer_reference_never_show_before_submission" for x in active),
        "superseded_owner_image_reference_count": len(superseded),
        "original_owner_image_reference_count": len(active) + len(superseded),
        "unapproved_active_image_count": sum(x.get("approved_for_release") is not True for x in active),
        "unverified_active_answer_reference_count": sum(
            x.get("answer_verified") is not True for x in active
            if x["role"] == "answer_reference_never_show_before_submission"
        ),
        "pre_submission_answer_leak_count": sum(
            x.get("may_display_before_submission") is True for x in active
            if x["role"] == "answer_reference_never_show_before_submission"
        ),
        "role_mapping_issues": issues,
    }


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
    # Image-based exams can contain an unmarked question screenshot AND a
    # screenshot with the correct answer outlined. Explicit role review is
    # essential: shipping the latter in the unanswered simulator leaks the key.
    split_file = out / "extracted" / "split.json"
    if not split_file.is_file():
        problems.append("owner_question_split_missing_for_visual_proof")
    raw_split = load(split_file) if split_file.is_file() else {}
    if not isinstance(raw_split, dict):
        problems.append("owner_question_split_not_mapping")
        raw_split = {}
    image_refs = sum(len(q.get("question_images") or []) +
                     len(q.get("answer_images") or [])
                     for q in raw_split.values() if isinstance(q, dict))
    visual_role_path = source / "visual-role-audit.json"
    visual_unreviewed = image_refs
    visual_wrong_role = 0
    visual_covered = 0
    image_audit = {}
    if image_refs:
        if not visual_role_path.is_file():
            problems.append("visual_source_role_manifest_missing")
        else:
            roles = load(visual_role_path)
            if roles.get("exam") != code or roles.get("source_pdf_sha256") != manifest["pdf_files"][0].get("sha256"):
                problems.append("visual_role_manifest_pdf_hash_mismatch")
            image_audit = audit_active_visual_roles(raw_split, roles)
            visual_covered = image_audit["active_role_coverage_count"]
            visual_unreviewed = image_audit["unapproved_active_image_count"]
            visual_wrong_role = image_audit["pre_submission_answer_leak_count"]
            if image_audit["role_mapping_issues"] or visual_covered != image_refs:
                problems.append("visual_role_coverage_mismatch:" +
                                ",".join(image_audit["role_mapping_issues"][:8]))
            if visual_unreviewed:
                problems.append(f"visual_assets_not_approved:{visual_unreviewed}")
            if image_audit["unverified_active_answer_reference_count"]:
                problems.append("visual_answer_keys_not_verified:" +
                                str(image_audit["unverified_active_answer_reference_count"]))
            if visual_wrong_role:
                problems.append(f"pre_submission_answer_image_exposed:{visual_wrong_role}")
    audit.update({
        "visual_image_count": image_refs,
        "visual_role_coverage_count": visual_covered,
        "unreviewed_visual_asset_count": visual_unreviewed,
        "pre_submission_answer_leak_count": visual_wrong_role,
        "unverified_visual_answer_reference_count": image_audit.get(
            "unverified_active_answer_reference_count", 0),
        "active_question_image_count": image_audit.get("active_question_image_count", 0),
        "active_answer_reference_count": image_audit.get("active_answer_reference_count", 0),
        "superseded_owner_image_reference_count": image_audit.get(
            "superseded_owner_image_reference_count", 0),
        "visual_role_mapping_issues": image_audit.get("role_mapping_issues", []),
        "visual_role_manifest_sha256": sha(visual_role_path) if visual_role_path.is_file() else None,
    })
    write_json(proofdir / "question-audit.json", audit)
    for k in ("held_count", "answer_not_found_count", "unverified_key_count",
              "flagged_accuracy_count", "human_review_required_count",
              "scoring_excluded_count"):
        if audit[k]:
            problems.append(f"unresolved_question_review:{k}={audit[k]}")
    research_file = ws / "research" / manifest["vendor_slug"] / f"{code}.json"
    research = load(research_file)
    sources = research.get("sources") or []
    # Independently hash the actual saved official HTML pages, rather
    # than trusting the declared source hashes in the research file.
    saved_sources = {}
    vendor_sources = ws / "sources" / manifest["vendor_slug"]
    if vendor_sources.is_dir():
        for sidecar in vendor_sources.rglob("*.html.json"):
            try:
                meta = load(sidecar)
                html_snapshot = sidecar.with_suffix("")
                if not html_snapshot.is_file():
                    continue
                digest = sha(html_snapshot)
                saved_sources[(str(meta.get("url") or ""), digest)] = html_snapshot.stat().st_size
            except (OSError, ValueError, TypeError):
                continue
    official_sources = []
    for source_info in sources:
        url = str(source_info.get("url") or "")
        expected = str(source_info.get("expected_sha256") or "")
        verified_size = saved_sources.get((url, expected))
        official_sources.append({
            "id": str(source_info.get("id") or ""),
            "url": url,
            "expected_sha256": expected,
            "retrieved_date": str(source_info.get("as_of_date") or ""),
            "content_sha256_verified": verified_size is not None,
            "snapshot_size_bytes": verified_size,
        })
    facts = factual_quotes({"exam_name": research.get("exam_name"), "facts": research.get("facts"),
                            "objectives": research.get("objectives")})
    info = {"exam": code, "sources": official_sources,
            "verified_source_count": sum(s["content_sha256_verified"] for s in official_sources),
            "quoted_fact_count": len(facts), "quoted_facts": facts}
    write_json(proofdir / "official-sources.json", info)
    hashes = {x["expected_sha256"] for x in official_sources}
    if not official_sources or not facts:
        problems.append("official_fact_evidence_missing")
    if info["verified_source_count"] != len(official_sources):
        problems.append("official_page_snapshot_hash_mismatch_or_missing")
    if any(not re.fullmatch(r"[0-9a-f]{64}", x["expected_sha256"]) for x in official_sources):
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
        "author": "CertPassly Team",
        "editorial_credit": "CertPassly Team",
        "editorial_process": "AI-assisted draft; independent human subject review pending",
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
