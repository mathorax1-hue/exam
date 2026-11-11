# Supplemental Salesforce raw exam collection

Date: 2026-11-11

Owner-supplied supplemental Google Drive folder was inspected through the connected Google Drive account. It contains **102 direct subfolders** for Salesforce-related exams and credentials. Exact source URLs and raw PDF content are stored only in the private `mathorax1-hue/raw-exam` repository's `catalog/salesforce-collection.csv` and source folders, not in this public processor repository.

- Source collection catalog: `mathorax1-hue/raw-exam:catalog/salesforce-collection.csv` (private).
- Raw importer: `mathorax1-hue/exam:scripts/import_raw_exams.py`.
- Import workflow: `mathorax1-hue/raw-exam:.github/workflows/import-salesforce-collection.yml` (private, Git LFS PDFs).
- Import run: https://github.com/mathorax1-hue/raw-exam/actions/runs/43021246836 (requires access to the private repository).

The private collection catalog uses a source-specific alias when the folder title is not a confirmed official exam code, or when the canonical code already exists in the original catalog. These aliases are **not** official vendor exam codes and must not be used as final catalog codes or site URLs until confirmed against official vendor information.

The importer deliberately excludes VCE and other non-PDF inputs. It writes per-file SHA-256 metadata and PDF files into the private source repository, with Git LFS enabled. It does not publish an exam or complete the AI author, writing, validation, or packaging stages.

**Completed result (verified):** GitHub Actions run [43021246836](https://github.com/mathorax1-hue/raw-exam/actions/runs/43021246836) concluded `success`. All 102 entries were imported as 102 PDF files (49,838,610 bytes) with zero failed or review records across 13 batches. The private summary is `reports/collections/salesforce-2026-11-11-summary.json`. Files are raw owner inputs only, not validated ready exams.
