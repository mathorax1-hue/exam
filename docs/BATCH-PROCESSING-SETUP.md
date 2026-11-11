# Batch processing: private raw exams to private validated drafts

Setup date: 2026-11-11
Public code repository: `mathorax1-hue/exam`
Private owner-source repository: `mathorax1-hue/raw-exam`
Private output repository: `mathorax1-hue/ready-exams`

## What actually runs

The real processing workflow is in the **private source repository**, at `raw-exam/.github/workflows/process-exams.yml`. This keeps execution logs, original PDFs, extracted questions and optional author artifacts away from the public processor.

The workflow invokes the public, reviewed processor scripts:

- `scripts/plan_exam_processing.py`: enumerate every source manifest, check for owner rights and exactly one PDF, verify mapped official exam code and vendor, and build an eligible matrix plus a blocked-source review list.
- `scripts/process_raw_exam.py`: load only the chosen PDF from Git LFS, compare bytes and SHA-256 against the source manifest, prepare a temporary CertPassly workspace, run catalog/intake/sources/research/extract/textfix/answer_research/intent, and proceed beyond `author` only if the reviewed author inputs exist.
- Pinned upstream CertPassly skill revision: `13dea6bab662ab1c4bbf87017e912e519907c8bc`. No silent upstream upgrade.

For a fully authored exam, the private job runs `author`, `pages`, `writing`, `import`, `bank`, `validate`, `package`; independently checks import conformance and the final package denylist scan; writes `release.json` with source and package hashes; then commits only sanitized generated package files to private `ready-exams` using Git LFS.

A successful package is **validated draft**, not a published website exam. Human publication review is still necessary.

## Current source inventory

On initial batch setup there were **185 raw source manifests and 190 PDF paths** in the private `raw-exam` repository. The pinned upstream lookup recognized 64 source directory codes. The remaining 121 need official exam-code mapping and/or other source input review. The live planner is authoritative about exact queue and blocked counts.

No `authoring/` JSONs were present on initial inspection. The skill does not call an AI itself, so this workflow cannot legally or technically claim that those raw exams are completed merely because intake or extraction passed. See the exact batch statuses in private `raw-exam/reports/processing/latest.json`.

## How to prepare and rerun one exam

1. In private `raw-exam`, identify `exams/<EXAM>/manifest.json`. Ensure the directory uses a real vendor exam code and the manifest contains an official exam URL or the pinned lookup recognizes the exam.
2. Ensure the source folder has **exactly one** selected owner PDF and its SHA-256 matches the manifest. Do not merge different PDFs or assign official codes to provisional aliases without verification.
3. Open private `raw-exam` Actions and select **Process raw exams into validated drafts**; choose `target=one` and the exact exam directory code. To process all eligible sources, choose `target=all`.
4. For an exam with status `needs_author`, download its **private** `exam-result-<CODE>` artifact, review the extracted questions and official evidence, and prepare the author files according to upstream operator-guide section 7. Store authoring JSON in private `exams/<CODE>/authoring/` and, where needed, `exams/<CODE>/visual_transcription.json`.
5. Rerun the same exam. Review writing and bank flags, and fix only flagged parts until all gates pass. A valid package should be automatically promoted to private `ready-exams/exams/<CODE>/`.

Required private author files include `explanations_text.json`, `page_prose.json`, `bank_meta.json`, with visual explanations, researched answers, text fix decisions and visual transcription added when the item types require them. Never fabricate missing answers or change owner keys.

## Credentials

`CERTPASSLY_REPOS_PAT` must be a **repository Actions secret in private `raw-exam`**, with fine-grained Contents Read and write for private `ready-exams`. It is used only for validated package promotion. The default GitHub Actions token handles private `raw-exam` source checkout and LFS reads. No PAT values, owner PDFs, owner Drive links, or question texts belong in the public `exam` Git history.

The workflow handles lack of PAT by failing the **promotion** step when a package has actually passed every gate. A pre-author run does not prove that the PAT is configured.

## Results and known issues

- First batch run: https://github.com/mathorax1-hue/raw-exam/actions/runs/43023682826 (cancelled after detecting that LFS downloads needed persisted checkout credentials).
- Second batch run: https://github.com/mathorax1-hue/raw-exam/actions/runs/43024141779 (superseded after discovering a missing `PyYAML` dependency).
- Corrected batch workflow run: https://github.com/mathorax1-hue/raw-exam/actions/runs/43024388458 (started 2026-11-11; completion and per-exam results must be verified from Actions and its final private report).

Status and pre-author input artifacts are private and have a 14-day retention. Large batches consume GitHub Actions minutes and vendor sites can rate-limit research. Only the live run conclusion and report prove what succeeded.

## Release evidence and destination verification (2026-11-11 update)

- The public processor generates `result/evidence-manifest.json` plus eight independent proof files under `result/proofs/`. Official saved HTML snapshots are rehashed and compared with the vendor research hashes. A question audit detects pending reviews, researched unverified keys, answer-not-found items and scoring exclusions.
- The raw private workflow's separate `audit` step generates and checks those proofs **after all 15 CertPassly stages and import conformance succeed**. It sets `steps.audit.outputs.ready=true` only if no unresolved review/evidence blockers exist.
- Promotion copies the ZIP, its scanner report, release metadata, evidence-manifest and all proof files to the private destination. Before pushing, the destination's own `scripts/verify_releases.py --exam <CODE>` must pass. Its CI reruns independent checks and ZIP scanning on each push.
- Proof files include SHA-256 for the owner input PDF, raw and processor Git revision, official source snapshot hashes and quotes, build bank checksum, all stage exit codes, validation checks, writing checks and package scan.
- No source PDF, direct owner Drive link or raw extracted question material is written to the public processor. Real output stays inside private repositories.
- **Validated draft is not website publication or 100% factual accuracy.** Human review and a live site importer trial remain separate requirements.
- The promotion token `CERTPASSLY_REPOS_PAT` is required in the private `raw-exam` Actions secrets. The last actual token-check workflow failed because it was missing. Do not claim cross-repository pushes work until that check passes.

[Ready-exams proof contract](https://github.com/mathorax1-hue/ready-exams/blob/main/docs/RELEASE-CONTRACT.md) | [Ready-exams CI](https://github.com/mathorax1-hue/ready-exams/actions/workflows/verify-ready-exams.yml)
