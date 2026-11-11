# Exam catalog intake review

Review date: 2026-11-11
Source: Connected Google Sheet titled `Exams`, tab `Sheet1`.
Status: metadata and folder inventory completed; no real question PDF was downloaded or processed.

This report intentionally excludes Google Drive folder IDs, direct file URLs, owner question text, and other private input material. The source remains in Google Drive.

## Sheet layout

- One tab (`Sheet1`), with populated content reaching row 164.
- 127 non-empty rows; only columns A through E contain values in the inspected range.
- Left group: column A code/vendor label, B sheet-marked completion status, C Drive link.
- Right group: column D additional code/vendor label, E Drive link, without a dedicated completion-status column.
- Vendor section labels appear among exam rows. This is a visual owner sheet, not a normalized `catalog.csv`; conversion must preserve both left and right groups.

## Counts from live sheet

- 89 linked records: 88 Drive folder links plus 1 direct Drive file link.
- 25 left-column status cells are marked `Done` (case-insensitive). This is a *sheet status*, not proof of a completed current-pipeline run.
- 24 of the marked-`Done` records have links; `CLF-C02` is marked `Done` but has no link (row 48).
- 65 linked entries are not marked `Done`. Right-group records have no dedicated status column and must not be called unfinished solely because status is absent.
- Some exam rows are listed without links, and some vendor headings are interspersed with exam rows. Do not count headings as exams.

## Data quality issues to review

1. The same Drive folder ID appears for `Plat-Arch-205` (row 21) and `CKAD` (row 31). Verify whether this is intentional. Do not deduplicate or assign files to either exam without checking.
2. The `CISSP` (row 35) and `Nutanix` (row 144) link parameters end in `sharingg`, not `sharing`. The folder ID may still resolve; normalize only after checking the target.
3. `WINDOWS 11 PRO` (row 122) points to a single Drive file rather than a folder. Treat it as a separate input shape.
4. `CLF-C02` (row 48) has a `Done` status without a supplied Drive link.
5. Normalize display codes such as `AB - 900` only for catalog matching; retain the original sheet label and verify the authoritative vendor exam code.

## Folder readiness spot-check

- `AB-900`: folder can be listed, with `PDF` and `VCE` child folders. The PDF child folder contains one PDF whose displayed name indicates 89 questions.
- `SC-200`: folder can be listed, with `PDF` and `VCE` child folders. The PDF child folder contains one PDF whose displayed name indicates 436 questions.
- These numbers come from filenames, **not** from extraction or verification of question counts. The PDFs were not downloaded, inspected or imported. VCE files are not to be processed.

## Next safe steps

1. Confirm the owner has rights to use the question PDFs and to create derivative study/practice materials.
2. Decide which exam to prepare first, accounting for sheet status and official exam availability. `AB-900` and `SC-200` have confirmed folder/PDF structure but are not yet selected.
3. Build a normalized catalog with vendor, original code, canonical code, sheet status, source-folder reference and review flags; keep private Drive links outside repository commits.
4. Prepare a secure owner-input handoff to the temporary GitHub Actions runner without committing raw PDFs, private Drive URLs or credentials. The current workflow expects `workspace/` inputs and does not itself provide private Google Drive authentication.
5. Run the pinned skill, create the batched author files using an AI/human, rerun writing and validation, verify `check_bank`, import conformance and package scanning.
6. Keep all output in draft pending the required human review and report SHA-256 checksums and GitHub run URLs.

## Evidence and boundaries

The source sheet and nested folder lists were read through the connected Google Drive account on the review date. No real exam pipeline workflow was dispatched. No assertion of publication readiness, verified answer keys, or completed exam processing is made in this report.
