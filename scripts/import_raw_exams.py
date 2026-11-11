#!/usr/bin/env python3
"""Import owner-approved PDF inputs from the private catalog to private raw-exam.

Uses the pinned upstream Drive downloader's public folder parser. Does not
extract questions or call an AI. Run only in the private raw-exam Actions job.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

SAFE_CODE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,79}$")
PDF_MAGIC = b"%PDF"
MAX_BYTES = 125 * 1024 * 1024


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_catalog(path: Path):
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw-root", required=True, type=Path)
    p.add_argument("--catalog", required=True, type=Path)
    p.add_argument("--skill-root", required=True, type=Path)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=12)
    p.add_argument("--max-mb", type=int, default=125)
    args = p.parse_args()
    if args.offset < 0 or args.limit < 1:
        raise SystemExit("offset must be nonnegative and limit positive")
    cap = min(max(args.max_mb, 1), 125) * 1024 * 1024

    sys.path.insert(0, str(args.skill_root.resolve() / "scripts"))
    from drive_fetch import list_folder, folder_ids, get, dl, safe_name

    root = args.raw_root.resolve()
    rows = read_catalog(args.catalog)
    cache_dir = root / ".import-cache" / "drive"
    report = []
    errors = 0
    for idx in range(args.offset, min(len(rows), args.offset + args.limit)):
        record = rows[idx]
        code = (record.get("exam_code") or "").strip()
        mode = (record.get("import_mode") or "import").lower()
        vendor = (record.get("vendor_slug") or "").strip()
        url = (record.get("source_url") or "").strip()
        result = {"row": idx + 2, "code": code, "status": None, "files": [], "reason": ""}
        try:
            if mode != "import":
                result.update(status="review", reason="Catalog entry requires exam-code or source-folder review")
                report.append(result)
                continue
            if not SAFE_CODE.fullmatch(code):
                raise ValueError("Invalid normalized exam code")
            if not vendor or not re.fullmatch(r"[a-z][a-z0-9-]*", vendor):
                raise ValueError("Invalid vendor slug")
            ids = folder_ids(url)
            if len(ids) != 1:
                raise ValueError("Input must be exactly one Google Drive folder")
            folder_id = ids[0]
            # The upstream source is the authority for official exam URLs.
            dest = root / "exams" / code
            src_dir = dest / "source"
            if dest.is_symlink() or (src_dir.exists() and src_dir.is_symlink()):
                raise ValueError("Symlink source path refused")
            src_dir.mkdir(parents=True, exist_ok=True)
            queue = [folder_id]
            visited = set()
            pdf_count = 0
            while queue:
                fid = queue.pop(0)
                if fid in visited:
                    continue
                visited.add(fid)
                for item in list_folder(fid, str(cache_dir)):
                    if item["folder"]:
                        queue.append(item["id"])
                        continue
                    name = safe_name(item.get("name") or "")
                    if not name.lower().endswith(".pdf"):
                        continue  # VCE and other binaries are not useful inputs.
                    fname = safe_name(name)
                    target = src_dir / fname
                    if target.exists() and target.stat().st_size > 20:
                        with target.open("rb") as chk:
                            if chk.read(4) == PDF_MAGIC:
                                pdf_count += 1
                                result["files"].append({"name": fname, "bytes": target.stat().st_size, "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "status": "cached"})
                                continue
                    status, content_type, payload = get(f'{dl()}/download?id={item["id"]}&export=download&confirm=t', timeout=300)
                    if status != 200:
                        raise ValueError(f"PDF download returned HTTP {status}")
                    if not payload.startswith(PDF_MAGIC) or "text/html" in content_type:
                        raise ValueError("Downloaded PDF did not have PDF file signature")
                    if len(payload) > cap:
                        raise ValueError("PDF exceeds configured size limit")
                    temp = target.with_suffix(".pdf.part")
                    temp.write_bytes(payload)
                    os.replace(temp, target)
                    pdf_count += 1
                    result["files"].append({"name": fname, "bytes": len(payload), "sha256": digest(payload), "status": "downloaded"})
            if not pdf_count:
                raise ValueError("No readable PDF found under source folder")
            manifest = {
                "exam_code": code,
                "vendor_slug": vendor,
                "owner_rights_statement": "The owner affirmed permission to use the supplied PDFs for exam preparation in ChatGPT on 2026-11-11.",
                "source_kind": "owner_provided_google_drive_folder",
                "source_sheet_row": record.get("sheet_row", ""),
                "sheet_status": record.get("sheet_status", ""),
                "pdf_files": [{"name": o["name"], "sha256": o["sha256"], "bytes": o["bytes"]} for o in result["files"]],
            }
            (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            result["status"] = "imported"
        except Exception as exc:
            errors += 1
            result["status"] = "failed"
            result["reason"] = str(exc)[:300]
        report.append(result)
        print(f'{code or "UNKNOWN"}: {result["status"]} ({len(result["files"])} PDF file(s)); {result["reason"]}')
    summary = {
        "catalog_entries": len(rows),
        "offset": args.offset,
        "batch_count": len(report),
        "imported": sum(x["status"] == "imported" for x in report),
        "review": sum(x["status"] == "review" for x in report),
        "failed": errors,
        "records": report,
    }
    report_dir = root / "reports" / "batches"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / f'import-{args.offset:03d}.json').write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f'Batch summary: {summary["imported"]} imported, {summary["review"]} review, {summary["failed"]} failed')
    # Each row is independent. Write the report and allow later batches to continue.
    return 0


if __name__ == "__main__":
    sys.exit(main())
