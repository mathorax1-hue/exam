# CertPassly workspace work log

This log records GitHub workspace setup and safe operational changes. It is not a record of any real exam having been processed.

## 2026-11-11: Initial workflow and AI instructions

- Confirmed this repository: `mathorax1-hue/exam`, branch `main`.
- Added `.github/workflows/certpassly.yml` to check out upstream pinned commit `13dea6bab662ab1c4bbf87017e912e519907c8bc`, install Python 3.11 and PDF tools, run CLI help and regression tests.
- Initial runner commit: `683d0e33aa01ca405fb442132eee079a3d8804a5`.
- Initial workflow proof: [run 43011456006](https://github.com/mathorax1-hue/exam/actions/runs/43011456006), status **success**.
- Added `AGENTS.md` and `.github/copilot-instructions.md` to direct assistants to upstream skill documents.
- Read the upstream skill entry, agent rules, operator guide, training exercises, lessons learned, writing guidance and handoff. Reading is not training completion.

## 2026-11-11: Operations and recurring change tracking

- Added `docs/CERTPASSLY-OPERATIONS.md` as the local, original operating handoff.
- Added `docs/UPSTREAM_STATUS.md` and `.github/workflows/upstream-watch.yml` for scheduled source revision tracking. It may commit **only metadata**; it does not change the pinned executable skill revision.
- Expanded the main workflow to run synthetic Microsoft and generic-vendor demos plus their import conformance checks. Demo workflow commit: `73bbb6b321baed1a2acba2c65f477e30b8303e77`.
- Added `README.md`, a safer `.gitignore`, and this work log.
- Manual real-exam processing has **not** been run. The upstream graded AI training exercises have **not** all been manually completed.
- The weekly upstream-watch schedule has been created, but its first scheduled run remains to be confirmed.


## 2026-11-11: Confirmed tests and scheduled recurring review

- GitHub Actions [run 43012583788](https://github.com/mathorax1-hue/exam/actions/runs/43012583788) concluded **success**. Verified job-step results: skill checkout, Python setup, system PDF tools, package install, CLI help, regression suite and synthetic demos all succeeded.
- The exam processing step was skipped because this was a push-triggered verification, not a manual real-exam run.
- A weekly assistant review is enabled for Tuesdays, approximately 15:00 Asia/Karachi, beginning 2026-11-17. It compares upstream changes, checks GitHub Action results, and updates safe repository docs when there is a material change. The assistant automation is separate from the GitHub scheduled SHA tracker.
- The automatic SHA tracker is scheduled for Mondays 08:00 UTC. Its first scheduled execution has not yet been observed.
- Neither schedule retrains the assistant. No upstream source pin update, real exam run or publication is authorized by either schedule.

## Open items

- Expanded demo verification **completed**: [run 43012583788](https://github.com/mathorax1-hue/exam/actions/runs/43012583788) succeeded; install, CLI, regression tests and both synthetic end-to-end demos were all green. The manual real-exam job was intentionally skipped.
- Confirm weekly upstream-watch has write permission and records changes correctly when upstream advances. Its manual trigger may also be tested in GitHub UI.
- Complete all graded training exercises on synthetic data before claiming formal training completion.
- For a real exam: obtain owner-rights confirmation, configure the workspace, prepare saved official sources and author files, run all gates, and review the draft package. Do not commit owner inputs to this repository.
- Live site importer acceptance is not established by the upstream static conformance test.

## Logging rule

For later changes, record: date, what was changed, why, commit SHA, CI URL/result, source revision checked, validation evidence and unresolved decisions. Never put tokens, real question content, raw extracts, seller strings or private source material in this file.

## 2026-11-11: First Google Sheets exam catalog reviewed

- Connected to the owner-provided Google Sheet named `Exams` and read the complete populated tab through row 164.
- Logged counts, unusual links, duplicate folder assignment and two folder structure spot-checks in `docs/EXAM-CATALOG-REVIEW.md` (commit `6d722ea42c0207b73369066d7c9ffe182e7f4d68`).
- Did **not** commit folder URLs, question PDFs, or private exam inputs; did **not** run a real exam or infer an owner-rights statement.
- Real processing remains gated on owner rights confirmation, exam selection and secure input handoff to GitHub Actions.

## 2026-11-11: AB-900 owner authorization and PDF preflight

- Owner confirmed permission to use exam PDFs in chat. This is recorded as an owner statement, not independently validated rights.
- Downloaded the AB-900 PDF from the connected Google Drive account into the temporary private workspace, not the Git repository.
- Inspected the PDF: 92 pages, 89 consecutively numbered questions, 37 text-visible answer keys and 52 hotspot items with blank answer text that need visual key review.
- Compared the supplied cover's exam limits against Microsoft's official current AB-900 exam page and study guide; the cover differs. Do not use its numbers as official facts.
- Committed sanitized intake summary in `docs/AB-900-INTAKE.md` (commit `01f779d46fbabdefda14b7a8fa4e4183f6b605ab`). Original input, raw text and private Drive links were not committed.
- Real GitHub Actions exam stages, the required author batch, full validation and final package are **not** complete.

## 2026-11-11: Added on-demand owner-authorized intake workflow

- Added `.github/workflows/exam-intake.yml`, commit `e5d81ac41cd49bc0467b9e2e579470b46d35367a`.
- The workflow allows a manually supplied exam code, vendor, Drive folder URL and rights confirmation. It prepares a temporary workspace and attempts catalog, intake, sources, research, extraction, textfix, answer research and intent with the pinned skill.
- Only a metadata report is uploaded as an Actions artifact. Real owner files and extracted questions stay off Git and out of artifacts.
- This workflow **has not been dispatched or tested on AB-900**. An authenticated Drive connection in ChatGPT is not a credential on a GitHub-hosted runner, so folder accessibility must be verified in the actual run.
- Readme and operations handbook were updated with instructions and limitations. The AI author stage and full package remain separate, unmet steps.

## 2026-11-11: Private raw-to-ready batch processing enabled

- Verified the architecture: `mathorax1-hue/exam` is **public code-only**; `mathorax1-hue/raw-exam` and `mathorax1-hue/ready-exams` are **private**.
- Added `scripts/plan_exam_processing.py` and `scripts/process_raw_exam.py` to public processor code. Source PDFs remain in private raw repository and are fetched one at a time via Git LFS, matched to the SHA-256 manifest.
- Added private `raw-exam/.github/workflows/process-exams.yml`, which runs all eligible mapped exam sources, reports blocked sources, executes pre-author stages, uploads **private** stage artifacts, and promotes a package only if author, writing, bank, validation, import conformance and package scanning all pass.
- Corrected two live integration issues: private Git LFS checkout credentials and the restricted syntax of the upstream YAML parser. The runner now preserves upstream YAML and changes only the owner-rights string.
- Improved the runner to extract authorized PDFs **before** official-source research, and to retry blocked vendor HTML retrieval using the upstream skill's documented optional Playwright browser if rendering was unavailable.
- Latest live run: [43025342443](https://github.com/mathorax1-hue/raw-exam/actions/runs/43025342443), started 2026-11-11; verify final conclusion before claiming completion.
- Verified live private plan artifact: **185 source manifests, 46 queued for stage processing, 139 blocked before processing**. Blocking issues include missing official exam URLs, provisional aliases requiring official exam-code identification, and 2 records needing a single selected PDF. Block reason counts overlap.
- One confirmed real-source example: AAIR extracted 90 questions from an owner PDF; catalog, intake, extraction, and official-source retrieval succeeded, but research blocked because the saved official page lacks a weighted exam skill outline. The artifact status is `needs_official_sources`, not ready. Do not invent vendor weights.
- Promotion token validation workflow [43024897974](https://github.com/mathorax1-hue/raw-exam/actions/runs/43024897974) confirmed `CERTPASSLY_REPOS_PAT` was **missing from raw-exam Actions secrets** at verification time. The user must add it to the private `raw-exam` repository for future cross-repo promotions; the value must not be pasted into chat.
- As of this log, no real exam package has been confirmed promoted or published. The upstream skill has no built-in AI call for the author stage. No auto-generated invented keys or author files were added.
- One-time scheduled follow-up was configured to review the active batch run and report the resulting status counts. Continue to verify repository/Actions state rather than assuming success.
