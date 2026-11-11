#!/usr/bin/env python3
"""Process one private owner PDF using the pinned CertPassly skill.

Runs scripts through pre-author, and completes author->package only if reviewed
authoring inputs exist. No source PDF or raw extract is placed in the public repo.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

STAGE_PRE = ["catalog", "intake", "extract", "sources", "research",
             "textfix", "answer_research", "intent"]

def verified_microsoft_certification_name(workspace: Path, exam: str):
    """Return (name, URL, SHA) only when a saved Microsoft certification page contains the name.

    Never infers a name from an exam code or an unsourced file title.
    """
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{1,79}", exam):
        return None
    sources_path = workspace / "research" / "microsoft" / f"{exam}.sources.json"
    if not sources_path.is_file():
        return None
    try:
        spec = json.loads(sources_path.read_text(encoding="utf-8"))
        cp_urls = [r.get("url") for r in spec.get("sources", [])
                   if r.get("id") == "cp"]
    except (ValueError, OSError, TypeError):
        return None
    for url in cp_urls:
        from urllib.parse import urlparse
        parsed = urlparse(str(url or ""))
        if (parsed.scheme != "https"
            or parsed.hostname != "learn.microsoft.com"
            or not re.search(r"/credentials/certifications/(?:exams/|[^/]+/?$)", parsed.path, re.I)):
            continue
        for sidecar in (workspace / "sources" / "microsoft").glob("*.html.json"):
            try:
                meta = json.loads(sidecar.read_text(encoding="utf-8"))
                if meta.get("url", "").lower().rstrip("/") != url.lower().rstrip("/"):
                    continue
                snapshot = sidecar.with_suffix("")
                if not snapshot.is_file() or sha256(snapshot) != meta.get("sha256"):
                    continue
                body = snapshot.read_text(encoding="utf-8", errors="replace")
                matches = re.findall(r"<h1\b[^>]*>(.*?)</h1\s*>", body, re.I | re.S)
                for section in matches:
                    candidate = html.unescape(re.sub(r"<[^>]+>", " ", section))
                    candidate = re.sub(r"\s+", " ", candidate).strip()
                    if (not 12 <= len(candidate) <= 180
                        or not re.match(r"^Microsoft(?:\s|[-:])", candidate, re.I)
                        or "study guide" in candidate.lower()):
                        continue
                    # Match exactly the official text on this saved page, using
                    # the same plain-tag normalization used by upstream research.
                    norm = lambda x: re.sub(r"\s+", " ", html.unescape(x).replace("\u2019", "'")
                                          .replace("\u2013", "-").replace("\u2014", "-")).strip().lower()
                    if norm(candidate) not in norm(re.sub(r"<[^>]+>", " ", body)):
                        continue
                    return candidate, url, meta["sha256"]
            except (OSError, ValueError, TypeError, KeyError):
                continue
    return None


def add_verified_official_name(workspace: Path, exam: str, vendor: str, result_dir: Path):
    """Write only a sourced Microsoft name into the temporary per-exam catalog."""
    if vendor != "microsoft":
        return False
    verified = verified_microsoft_certification_name(workspace, exam)
    if not verified:
        return False
    name, url, expected_sha = verified
    catalog = workspace / "catalog.csv"
    with catalog.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1 or rows[0].get("exam_code") != exam:
        raise ValueError("Unexpected per-exam catalog while setting sourced title")
    rows[0]["exam_name"] = name
    with catalog.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    write_json(result_dir / "official-name-evidence.json",
               {"exam": exam, "official_exam_name": name,
                "official_page_url": url, "saved_html_sha256": expected_sha})
    print(f"{exam}: recorded a name backed by the saved official Microsoft page")
    return True


STAGE_POST = ["author", "pages", "writing", "import", "bank", "validate", "package"]
COLUMNS = ["vendor", "vendor_slug", "certification", "exam_code", "exam_name",
           "sheet_status", "drive_folder_url", "sheet_cell", "sheet_label",
           "official_exam_url", "url_http", "page_names_exam", "url_sha256",
           "source_path", "empty_reason"]
PIN = "13dea6bab662ab1c4bbf87017e912e519907c8bc"
RX = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{1,79}\Z")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


TEXT_FIX_AUTO_ALLOWED = ("lost_ligature", "repeated_word", "space_before_punct", "double_space")


def guarded_text_fix_config(original: str, raw_exam_dir: Path, code: str) -> str:
    """Restrict automatic text edits, without modifying owner stems or keys.

    The private owner workspace may supply a strict subset of the pinned
    skill's default automatic fix types. This prevents product-name false
    positives such as 'Microsoft Teams teams'. Every excluded proposal
    becomes an explicit author decision; no silent rewrite takes place.
    """
    override = raw_exam_dir / "processing_overrides.json"
    if not override.is_file():
        return original
    data = json.loads(override.read_text(encoding="utf-8"))
    if data.get("exam") != code:
        raise ValueError("Private override does not match exam code")
    kinds = data.get("text_fixes_auto")
    if (not isinstance(kinds, list) or not kinds
            or len(kinds) != len(set(kinds))
            or any(k not in TEXT_FIX_AUTO_ALLOWED for k in kinds)):
        raise ValueError("Invalid automatic text fix subset")
    old = """text_fixes:
  enabled: true
  auto:
    - lost_ligature
    - repeated_word
    - space_before_punct
    - double_space"""
    new = "text_fixes:\\n  enabled: true\\n  auto:\\n" + "".join("    - " + k + "\\n" for k in kinds)
    new = new.replace("\\n", "\n").rstrip("\n")
    if original.count(old) != 1:
        raise ValueError("Pinned text-fixes config anchor changed")
    return original.replace(old, new, 1)



def apply_original_editorial_overlay(workspace: Path, raw_exam: Path, exam: str,
                                     result_dir: Path):
    """Overlay original CertPassly Team questions without replacing the owner PDF.

    The replacement is restricted to exactly the owner's existing question slots.
    The complete original split remains in the private extraction artifact/PDF,
    and hashes plus original/new question identities are recorded for audit.
    """
    path = raw_exam / "authoring" / "original_editorial_replacements.json"
    if not path.is_file():
        return {}
    raw_manifest = load_json(raw_exam / "manifest.json")
    data = load_json(path)
    if (data.get("exam_code") != exam or data.get("author") != "CertPassly Team"
            or data.get("owner_pdf_sha256") != raw_manifest["pdf_files"][0]["sha256"]
            or data.get("publication_state") != "EDITORIAL_REPLACEMENT_DRAFT_NOT_RELEASED"):
        raise ValueError("Original editorial replacements do not match owner provenance")
    records = data.get("replacement_questions")
    if (not isinstance(records, list) or not records
            or len(records) != data.get("replacement_count")):
        raise ValueError("Invalid replacement count")
    split_path = workspace / "out" / exam / "extracted" / "split.json"
    split = load_json(split_path)
    if not isinstance(split, dict):
        raise ValueError("Owner extraction is not a keyed question list")
    original_sha = sha256(split_path)
    original_count = len(split)
    archive = result_dir / "original-owner-extraction.sha256.json"
    write_json(archive, {"exam": exam, "owner_question_split_sha256": original_sha,
                         "question_count": original_count,
                         "source_pdf_sha256": raw_manifest["pdf_files"][0]["sha256"]})
    seen = set()
    rewritten = {}
    for item in records:
        old = item.get("original_owner_question_id")
        new = item.get("new_question_key")
        if (not isinstance(old, str) or not re.fullmatch(r"q[0-9]{3,5}", old)
                or old not in split or old in seen
                or new != "cp-" + exam.lower().replace("-", "") + "-" + old + "-r1"):
            raise ValueError("Replacement does not map uniquely to one extracted owner question")
        seen.add(old)
        if (item.get("author") != "CertPassly Team"
                or item.get("approved_for_publication") is not False
                or item.get("not_in_owner_pdf") is not True):
            raise ValueError("Replacement lacks original and draft attribution")
        urls = item.get("official_sources") or []
        if (not isinstance(urls, list) or not urls
                or any(not isinstance(u, str) or
                       not re.match(r"^https://(learn\.microsoft\.com|support\.microsoft\.com)/", u)
                       for u in urls)):
            raise ValueError("Original replacement lacks official source URLs")
        qtype = item.get("type") or item.get("question_type")
        stem = item.get("stem")
        if not isinstance(stem, str) or len(stem) < 20:
            raise ValueError("Original replacement stem missing")
        original = split[old]
        row = {
            "question_key": old, "source_number": original["source_number"],
            "marker": "CERTPASSLY ORIGINAL, replaces " + old, "pages": [],
            "stem": stem, "options": {}, "answer_raw": "",
            "question_images": [], "answer_images": [],
            "layout_profile": "certpassly_team_original_editorial",
        }
        if qtype == "yes_no_matrix":
            ys = item.get("correct_responses") or []
            rows = item.get("rows") or []
            if (not isinstance(rows, list) or len(rows) < 2
                    or len(rows) != len(ys)
                    or any(v.lower() not in ("yes", "no") for v in ys)):
                raise ValueError("Original matrix rows and key shape mismatch")
            if "select Yes if the statement is true" not in stem:
                row["stem"] = stem.replace("select Yes if it is correct",
                                           "select Yes if the statement is true")
            if "select Yes if the statement is true" not in row["stem"]:
                raise ValueError("Original matrix stem lacks the pinned yes/no marker")
        elif qtype == "single_choice":
            options = item.get("options") or []
            if not isinstance(options, list) or len(options) < 2:
                raise ValueError("Original selection question needs options")
            pairs = [(x.get("id"), x.get("text")) for x in options]
            letters = [x[0] for x in pairs]
            correct = item.get("correct_option_id")
            if (len(set(letters)) != len(letters)
                    or any(not re.fullmatch(r"[a-h]", str(x)) or not isinstance(y, str)
                           or not y.strip() for x, y in pairs)
                    or correct not in letters):
                raise ValueError("Original option IDs or selected answer invalid")
            row["options"] = dict(pairs)
            row["answer_raw"] = correct.upper()
        else:
            raise ValueError("Unsupported new original editorial question type: " + str(qtype))
        split[old] = row
        rewritten[old] = {
            "original_source_question_key": old,
            "editorial_question_id": new,
            "editorial_stem_sha256": hashlib.sha256(row["stem"].encode()).hexdigest(),
            "official_reference_urls": urls,
            "source_kind": "original_certpassly_team_not_owner_pdf",
            "source_accuracy_review": "pending",
            "human_review_status": "pending",
        }
    if len(split) != original_count:
        raise ValueError("Overlay changed the source question count")
    write_json(split_path, split)
    # Remove stale source-image guesses from the discarded original question,
    # never use an old highlighted key to score a newly written replacement.
    vd = split_path.with_name("visual_draft.json")
    if vd.is_file():
        draft = load_json(vd)
        if isinstance(draft, dict):
            for old in seen:
                draft.pop(old, None)
            write_json(vd, draft)
    # Visual transcriptions are required BEFORE answer_research. Without them,
    # the pinned skill may try to invent missing keys for source-image questions.
    trans_path = raw_exam / "visual_transcription.json"
    if not trans_path.is_file():
        raise ValueError("Source visuals lack an authoring transcription file")
    vt = load_json(trans_path)
    if any(k not in split for k in vt):
        raise ValueError("Visual transcript refers to a nonexistent question slot")
    visual_questions = {k for k, x in split.items() if not x["options"]}
    if set(vt) != visual_questions:
        raise ValueError("Incomplete visual transcript coverage")
    for old in rewritten:
        if old in vt and (item := next(r for r in records if r["original_owner_question_id"] == old)):
            if (item.get("type") or item.get("question_type")) != "yes_no_matrix":
                raise ValueError("Unexpected visual replacement type")
            if vt[old].get("rows") != item.get("rows"):
                raise ValueError("Original matrix transcript rows differ from new item")
            if vt[old].get("key") != item.get("correct_responses"):
                raise ValueError("Original matrix transcript key differs from new item")
    shutil.copyfile(trans_path, split_path.with_name("visual_transcription.json"))
    details = {
        "exam": exam, "original_owner_split_sha256": original_sha,
        "overlaid_split_sha256": sha256(split_path),
        "editorial_replacements_sha256": sha256(path),
        "replacements": rewritten, "count": len(rewritten),
        "owner_pdf_untouched": True, "editorial_credit": "CertPassly Team",
        "human_review_status": "pending", "ready_for_publication": False,
    }
    write_json(result_dir / "editorial-overlay-evidence.json", details)
    print(f"{exam}: applied {len(rewritten)} original editorial draft questions; original owner keys retained in private PDF")
    return details


def identify_originals_after_bank(workspace: Path, code: str, overlay: dict):
    """Correct source attribution in generated bank records; do not claim owner authorship."""
    if not overlay:
        return
    root = workspace / "out" / code
    qfile = root / "questions.json"
    if not qfile.is_file():
        raise ValueError("Bank did not generate questions.json")
    result = load_json(qfile)
    questions = result.get("questions") or []
    replaced = overlay["replacements"]
    found = set()
    for row in questions:
        key = row.get("question_key")
        if key not in replaced:
            continue
        found.add(key)
        row["created_source"] = "certpassly-team-original " + replaced[key]["editorial_question_id"]
        row["key_source"] = "certpassly_team_original_unverified"
        row["original_editorial_id"] = replaced[key]["editorial_question_id"]
        row["owner_question_replaced"] = key
        row["editorial_reference_urls"] = replaced[key]["official_reference_urls"]
        row["human_review_required"] = True
        row["review_gate"] = "not_checked"
        row["publication_state"] = "draft"
        row.setdefault("flags", []).append("original editor draft: independent review pending")
    if found != set(replaced):
        raise ValueError("Not every original editorial question was built into bank")
    write_json(qfile, result)
    csv_file = root / "import" / "questions.csv"
    if not csv_file.is_file():
        raise ValueError("Bank did not produce the site-format questions.csv")
    with csv_file.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        headers = list(reader.fieldnames or [])
        rows = list(reader)
    csv_found = set()
    for row in rows:
        key = row.get("question_key")
        if key in replaced:
            csv_found.add(key)
            row["created_source"] = "certpassly-team-original " + replaced[key]["editorial_question_id"]
            row["author_key"] = "CertPassly Team"
            row["review_gate"] = "not_checked"
            row["publication_state"] = "draft"
            row["blocking_reason"] = "AI-assisted original draft, independent review pending"
    if csv_found != found:
        raise ValueError("Question source attribution missing from import CSV")
    with csv_file.open("w", newline="", encoding="utf-8") as dest:
        writer = csv.DictWriter(dest, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)



def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def record_output(key, value):
    if (p := os.environ.get("GITHUB_OUTPUT")):
        with open(p, "a", encoding="utf-8") as handle:
            handle.write(f"{key}={value}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--skill-root", type=Path, required=True)
    parser.add_argument("--exam", required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    raw = args.raw_root.resolve()
    skill = args.skill_root.resolve()
    ws = args.workspace.resolve()
    resdir = args.results.resolve()
    code = args.exam
    resdir.mkdir(parents=True, exist_ok=True)
    result = {
        "exam": code,
        "status": "started",
        "reason": "",
        "pin": PIN,
        "source_commit": args.source_commit,
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "github_run_url": (f"https://github.com/{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/"
                           f"{os.environ.get('GITHUB_RUN_ID')}"),
        "stages": [],
        "pdfs": [],
        "ready_for_promotion": False,
    }
    try:
        if not RX.fullmatch(code):
            raise ValueError("invalid_exam_code")
        manifest_path = raw / "exams" / code / "manifest.json"
        manifest = load_json(manifest_path)
        pdfs = manifest.get("pdf_files") or []
        if manifest.get("exam_code") != code or len(pdfs) != 1:
            raise ValueError("manifest_mismatch_or_multiple_source_pdfs")
        vendor = str(manifest.get("vendor_slug", "")).strip()
        if not re.fullmatch(r"[a-z][a-z0-9-]*", vendor):
            raise ValueError("invalid_vendor_slug")
        rights = str(manifest.get("owner_rights_statement") or "").strip()
        if not rights:
            raise ValueError("owner_rights_not_confirmed")

        lookup = load_json(skill / "config" / "exam_lookup.json")
        known = (lookup.get("exams") or {}).get(code) or {}
        if known and known.get("vendor") != vendor:
            raise ValueError("vendor_conflicts_with_official_lookup")
        official_url = (manifest.get("official_exam_url") or "").strip()
        if not official_url:
            official_url = next(iter(known.get("urls") or []), "")
        if not official_url.startswith("https://"):
            raise ValueError("official_exam_url_not_mapped")
        pdf_name = pdfs[0]["name"]
        if Path(pdf_name).name != pdf_name or not pdf_name.lower().endswith(".pdf"):
            raise ValueError("invalid_pdf_name")
        src = raw / "exams" / code / "source" / pdf_name
        if not src.is_file():
            raise ValueError("pdf_missing_after_lfs_checkout")
        if src.open("rb").read(4) != b"%PDF":
            raise ValueError("not_a_real_pdf_or_lfs_pointer_not_resolved")
        checksha = sha256(src)
        if checksha != pdfs[0].get("sha256"):
            raise ValueError("source_pdf_sha256_mismatch")
        if src.stat().st_size != pdfs[0].get("bytes"):
            raise ValueError("source_pdf_size_mismatch")
        result["pdfs"].append({"sha256": checksha, "bytes": src.stat().st_size})
        ws.mkdir(parents=True, exist_ok=True)
        (ws / "owner-files" / code).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, ws / "owner-files" / code / pdf_name)
        (ws / "config").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(skill / "config" / "pipeline.example.yaml", ws / "config" / "pipeline.yaml")
        shutil.copyfile(skill / "config" / "vendors.example.yaml", ws / "config" / "vendors.yaml")
        cfg_file = ws / "config" / "pipeline.yaml"
        # Upstream uses a restricted YAML parser, so never round-trip its
        # configuration through a general YAML serializer. Preserve its
        # original multiline text and replace only this one scalar.
        original = cfg_file.read_text(encoding="utf-8")
        marker = 'owner_rights_statement: ""'
        if original.count(marker) != 1:
            raise ValueError("upstream_owner_rights_configuration_marker_changed")
        config_text = original.replace(marker, "owner_rights_statement: " + json.dumps(rights), 1)
        config_text = guarded_text_fix_config(config_text, raw / "exams" / code, code)
        cfg_file.write_text(config_text, encoding="utf-8")
        with (ws / "catalog.csv").open("w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerow({"vendor": vendor.title(), "vendor_slug": vendor, "exam_code": code,
                             "sheet_status": "owner_authorized", "sheet_label": code,
                             "official_exam_url": official_url, "url_http": "200"})
        day = datetime.now(timezone.utc).date().isoformat()

        def stage(name):
            cmd = ["certpassly-pipeline", "--exam", code, "--root", str(ws),
                   "--date", day, "--stage", name]
            if name == "intake":
                cmd.append("--offline")
            log_file = resdir / f"stage-{name}.log"
            with log_file.open("w", encoding="utf-8") as out:
                try:
                    ran = subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT,
                                         cwd=str(skill), timeout=3300, check=False)
                    rc = ran.returncode
                except subprocess.TimeoutExpired:
                    rc = 124
            # Official vendor pages may require JavaScript rendering.
            # Install only the skill's documented optional browser extra when
            # a plain source fetch explicitly reports that rendering is absent.
            if name == "sources" and rc and log_file.is_file():
                failure = log_file.read_text(encoding="utf-8", errors="replace")
                if "rendering is not available" in failure:
                    setup = resdir / "source-render-setup.log"
                    with setup.open("w", encoding="utf-8") as setup_out:
                        commands = [
                            [sys.executable, "-m", "pip", "install", "-e", str(skill) + "[render]"],
                            [sys.executable, "-m", "playwright", "install", "chromium"],
                        ]
                        ready = True
                        for install_cmd in commands:
                            try:
                                p = subprocess.run(install_cmd, stdout=setup_out,
                                                   stderr=subprocess.STDOUT, timeout=900)
                            except subprocess.TimeoutExpired:
                                ready = False
                                break
                            if p.returncode:
                                ready = False
                                break
                    if ready:
                        with log_file.open("a", encoding="utf-8") as out:
                            out.write("\nRetrying official source retrieval with headless Chromium.\n")
                            try:
                                retry = subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT,
                                                       cwd=str(skill), timeout=3300)
                                rc = retry.returncode
                            except subprocess.TimeoutExpired:
                                rc = 124
                        result["source_render_retry"] = True
                    else:
                        result["source_render_retry"] = False
            result["stages"].append({"name": name, "exit_code": rc})
            print(f"{code}: stage {name} exit {rc}", flush=True)
            return rc

        overlay = {}
        for name in STAGE_PRE:
            rc = stage(name)
            if name == "sources" and rc == 0:
                add_verified_official_name(ws, code, vendor, resdir)
            if name == "research" and rc == 0:
                overlay = apply_original_editorial_overlay(ws, raw / "exams" / code, code, resdir)
            if rc:
                result["status"] = "needs_official_sources" if name in ("sources", "research") else "blocked_stage"
                result["reason"] = name + "_failed"
                break

        if result["status"] == "started":
            inputs = raw / "exams" / code / "authoring"
            author_needed = ["explanations_text.json", "page_prose.json", "bank_meta.json"]
            missing = [n for n in author_needed if not (inputs / n).is_file()]
            if missing:
                result["status"] = "needs_author"
                result["reason"] = "Missing required batched authoring JSON files"
                result["missing_author_files"] = missing
            else:
                dest = ws / "out" / code / "authoring"
                dest.mkdir(parents=True, exist_ok=True)
                for item in inputs.glob("*.json"):
                    if item.is_file():
                        shutil.copyfile(item, dest / item.name)
                trans = raw / "exams" / code / "visual_transcription.json"
                if trans.is_file():
                    dest2 = ws / "out" / code / "extracted"
                    dest2.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(trans, dest2 / trans.name)
                for name in STAGE_POST:
                    rc = stage(name)
                    if name == "bank" and rc == 0:
                        identify_originals_after_bank(ws, code, overlay)
                    if rc:
                        result["status"] = "blocked_stage"
                        result["reason"] = name + "_failed"
                        break

        if result["status"] == "started":
            conformance = subprocess.run(
                [sys.executable, str(skill / "scripts" / "check_import_conformance.py"),
                 "--root", str(ws), "--exam", code],
                capture_output=True, text=True, timeout=240, check=False)
            (resdir / "conformance.log").write_text(
                conformance.stdout + "\n" + conformance.stderr, encoding="utf-8")
            result["conformance_exit_code"] = conformance.returncode
            validation_path = ws / "out" / code / "validation.json"
            validation = load_json(validation_path)
            if not isinstance(validation, list):
                raise ValueError("validation_report_not_a_list")
            fails = [row for row in validation if not row.get("passed", False)]
            result["validation_checks"] = len(validation)
            result["validation_failed"] = len(fails)
            pkg = ws / (code + "-package.zip")
            report = Path(str(pkg) + ".scan.json")
            scan = load_json(report)
            if conformance.returncode != 0 or fails or scan.get("passed") is not True or scan.get("hit_count") != 0:
                raise ValueError("conformance_validation_or_denylist_scan_failed")
            if not pkg.is_file():
                raise ValueError("validated_package_missing")
            release = {
                "exam": code, "status": "validated_draft", "published": False,
                "owner_pdf_sha256": checksha,
                "source_repo_commit": args.source_commit, "processor_skill_pin": PIN,
                "package_sha256": sha256(pkg), "package_bytes": pkg.stat().st_size,
                "validation_check_count": len(validation),
                "validation_failures": 0, "import_conformance": "passed",
                "writing_stage": "passed", "bank_validation": "passed",
                "package_scan_hits": 0, "github_run_url": result["github_run_url"],
                "validated_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            write_json(resdir / "release.json", release)
            shutil.copyfile(pkg, resdir / pkg.name)
            shutil.copyfile(report, resdir / report.name)
            result["status"] = "validated_draft"
            result["ready_for_promotion"] = True
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        result["status"] = "blocked_input_or_gate"
        result["reason"] = str(exc)[:220]

    record_output("ready", "true" if result["ready_for_promotion"] else "false")
    write_json(resdir / "status.json", result)
    # Store only the owner-authorized pre-author working files in *private*
    # Actions artifacts. Never upload the source PDF again or commit raw extracts.
    if result["status"] in ("needs_author", "needs_official_sources", "blocked_stage"):
        p = ws / "out" / code
        if p.is_dir():
            bundle = resdir / "preauthor"
            bundle.mkdir(exist_ok=True)
            for rel in ("text-fixes-proposals.json", "extracted/split.json",
                        "extracted/visual_draft.json", "extracted/unparsed.json"):
                src = p / rel
                if src.is_file():
                    dst = bundle / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, dst)
            research_root = ws / "research"
            if research_root.is_dir():
                shutil.copytree(research_root, bundle / "research", dirs_exist_ok=True)
    print(f'{code}: status={result["status"]}, reason={result["reason"]}', flush=True)
    print(f'RESULT {json.dumps({"exam": code,"status":result["status"]},separators=(",",":"))}')
    if gh_summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(gh_summary, "a", encoding="utf-8") as stream:
            stream.write(f"### {code}\n\nStatus: **{result['status']}**\n\n")
            stream.write(f"Reason: {result['reason']}\n\n")
            stream.write("Full source PDF remains in private raw-exam, not in the public processor repository.\n\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
