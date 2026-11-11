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
