#!/usr/bin/env python3
"""Create a private visual-fidelity audit from an owner-authorized PDF.

Keeps original embedded bytes and non-generative, lossless display copies.
NEVER decides an answer key or reveals a solution image by default.
Requires pymupdf and pillow. No source PDF is committed to public Git.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
from pathlib import Path

try:
    import fitz
    from PIL import Image, ImageFilter
except ImportError as e:
    raise SystemExit("Install pymupdf and pillow for private image audits") from e

CODE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{1,79}\Z")


def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def audit_pdf(pdf: Path, out: Path, exam: str, scale: int = 2):
    if not CODE.fullmatch(exam):
        raise ValueError("Unsafe exam code")
    if scale not in (1, 2, 3):
        raise ValueError("Display scale must be 1, 2 or 3")
    out.mkdir(parents=True, exist_ok=True)
    dirs = {k: out / k for k in ("source_embedded", "source_png", "display_png")}
    for directory in dirs.values():
        directory.mkdir(exist_ok=True)
    records = []
    seen = set()
    source_hash = digest(pdf.read_bytes())
    with fitz.open(pdf) as doc:
        page_count = len(doc)
        for page_num, page in enumerate(doc, 1):
            for image in page.get_image_info(xrefs=True):
                xref = image.get("xref")
                if not isinstance(xref, int) or xref <= 0 or xref in seen:
                    continue
                seen.add(xref)
                original = doc.extract_image(xref)
                ext = original["ext"].lower()
                if ext not in ("jpeg", "jpg", "png", "jpx", "tiff"):
                    raise ValueError(f"Unsupported image type: {ext}")
                raw = original["image"]
                stem = f"p{page_num:03d}-x{xref:04d}"
                binary = dirs["source_embedded"] / f"{stem}.{ext}"
                binary.write_bytes(raw)
                with Image.open(io.BytesIO(raw)) as src:
                    src = src.convert("RGB")
                orig_png = dirs["source_png"] / (stem + ".png")
                src.save(orig_png, format="PNG", compress_level=2)
                enlarged = src.resize((src.width * scale, src.height * scale),
                                      Image.Resampling.LANCZOS)
                if scale > 1:
                    enlarged = enlarged.filter(
                        ImageFilter.UnsharpMask(radius=0.9, percent=60, threshold=3))
                if enlarged.width * enlarged.height > 32_000_000:
                    raise ValueError("Image enlargement exceeds safe pixel limit")
                display_png = dirs["display_png"] / (stem + ".png")
                enlarged.save(display_png, format="PNG", compress_level=2)
                # Correct placement dimensions for rotated PDF pages.
                bbox = fitz.Rect(image["bbox"]) * page.rotation_matrix
                xdpi = round(72 * src.width / max(bbox.width, 0.1))
                ydpi = round(72 * src.height / max(bbox.height, 0.1))
                records.append({
                    "page": page_num, "xref": xref,
                    "source_px": [src.width, src.height],
                    "effective_dpi": [xdpi, ydpi],
                    "original_filename": "source_embedded/" + binary.name,
                    "original_sha256": digest(raw),
                    "source_png": "source_png/" + orig_png.name,
                    "source_png_sha256": digest(orig_png.read_bytes()),
                    "display_png": "display_png/" + display_png.name,
                    "display_png_sha256": digest(display_png.read_bytes()),
                    "display_px": [enlarged.width, enlarged.height],
                    "low_source_dpi": min(xdpi, ydpi) < 125,
                    "role": "UNREVIEWED_QUESTION_OR_ANSWER",
                    "may_display_before_submission": False,
                    "human_checked_question_and_answer_roles": False,
                })
    result = {
        "contract_version": 1,
        "exam": exam,
        "source_pdf_sha256": source_hash,
        "page_count": page_count,
        "image_count": len(records),
        "image_pages": len(set(row["page"] for row in records)),
        "low_source_dpi_count": sum(row["low_source_dpi"] for row in records),
        "enhancement_method": "Original bytes kept; lossless 1-3x Lanczos display PNG and mild non-generative sharpening",
        "warning": "Upscaling does not restore missing text or validate visual answer keys",
        "publication_gate": "Review question and answer image roles first. Do not show answer-highlighted screenshots before submission.",
        "images": records,
    }
    (out / "audit.json").write_text(json.dumps(result, indent=2) + "\n",
                                    encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--exam", required=True)
    parser.add_argument("--scale", type=int, default=2)
    args = parser.parse_args()
    report = audit_pdf(args.pdf, args.out, args.exam, args.scale)
    print(json.dumps({k: v for k, v in report.items() if k != "images"}, indent=2))
    print("All images remain blocked for unreviewed question display.")


if __name__ == "__main__":
    main()
