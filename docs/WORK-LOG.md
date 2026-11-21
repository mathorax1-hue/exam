# Work log

## 2026-11-21 (Asia/Karachi)

- Reviewed and adopted upstream v1.3.0 (`d9b6bf67efb870019dd88caeffa90952b7e000d3`) for the public synthetic QA workflow and the new three-phase reusable workflow.
- Real owner-PDF runs stay in private raw-exam. Public dispatch of the three-phase workflow is refused.
- The older `process-exams.yml` pin is unchanged until that private workflow is reviewed separately.
- Site import testing is a local sandbox gate, not part of public Actions.

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

## 2026-11-11: Ready-exams proof contract and independent release acceptance

- Private `mathorax1-hue/ready-exams` now has `docs/RELEASE-CONTRACT.md`, `scripts/verify_releases.py`, adversarial synthetic tests, `.github/workflows/verify-ready-exams.yml`, and a `.gitignore` that prevents ordinary accidental addition of owner PDFs or secrets. The verifier also rejects prohibited raw file extensions anywhere in the destination.
- Ready-exams CI [run 43029234211](https://github.com/mathorax1-hue/ready-exams/actions/runs/43029234211) concluded **success**. This proves the verification implementation and current repository state passed; the destination still had **zero real exam releases**.
- Public processor gained `scripts/build_release_evidence.py`: it cryptographically records saved official vendor HTML snapshot hashes, sourced quotes, question audit counts, stage exits, input PDF checksum, package scan and all required validation proof files. The private workflow now invokes the separate audit gate and only then attempts promotion.
- Public synthetic processor test [run 43028614506](https://github.com/mathorax1-hue/exam/actions/runs/43028614506) passed. The private workflow pins processor commit `b016956761e030aa3d74c215802757487a39dae7` and upstream CertPassly skill `13dea6bab662ab1c4bbf87017e912e519907c8bc`.
- The legacy public Drive intake workflow was retired because the owner source PDFs now live in private `raw-exam`; this also removes an obsolete failing CI path. Documentation was updated to point to the private source importer and proof-gated release.
- The latest private raw batch [run 43028722983](https://github.com/mathorax1-hue/raw-exam/actions/runs/43028722983) was queued at the time of this handoff; do not claim a final result until it concludes. Earlier reports showed 185 source folders, 46 eligible for pre-author stages, 139 needing source/code mapping review, and no completed package.
- The private promotion token check [run 43024897974](https://github.com/mathorax1-hue/raw-exam/actions/runs/43024897974) failed because `CERTPASSLY_REPOS_PAT` was not found in the **private raw-exam Actions secrets**. That must be fixed and retested before cross-repo publication of validated draft packages.
- **No human/site publication approval has been performed**. Passing all structural and proof checks results in an evidence-backed `validated_draft`, not a guaranteed 100% correct or published certification exam.

## 2026-11-11: Official-name preflight improvement and readiness monitor

- Confirmed the prior real batch remained blocked at official-source research; examples AB-900, AZ-900 and AI-103 extracted their PDFs and saved official Microsoft sources but lacked a matching verified certification name in generated research. Other vendors may lack a published weighted skills outline; those remain blocked.
- Updated public `scripts/process_raw_exam.py` to derive a name only from the original SHA-256-matched saved Microsoft certification page H1, and only when its literal text is present in that source. Added four synthetic tests for a legitimate title, tampered HTML, nonofficial URLs and non-Microsoft vendors. Public processor CI [43030764143](https://github.com/mathorax1-hue/exam/actions/runs/43030764143) passed.
- Pinned private `raw-exam` processing workflow to tested public processor commit `5988ee5fd523999009f0f6b2559d50bb4da9f734`. New private all-exam run: [43031064207](https://github.com/mathorax1-hue/raw-exam/actions/runs/43031064207). Final stage results are not yet established.
- Created [private raw-exam issue #1](https://github.com/mathorax1-hue/raw-exam/issues/1), tracking 185 source folders, 139 blocked mappings/source choices, unresolved official research, AI/human authoring and token-gated validated drafts.
- Changed the existing one-time assistant review into a daily conditional readiness monitor starting November 11, 2026 at 20:00 Pakistan time. It checks CI, statuses, output evidence and user-action blockers and only claims completion on actual proof.
- A working `CERTPASSLY_REPOS_PAT` in private `raw-exam` Actions secrets remains necessary for validated packages to be pushed to private `ready-exams`. No credential value was requested or recorded.

## 2026-11-11: Verified real pre-author progress and destination access

- Private raw processing [run 43031064207](https://github.com/mathorax1-hue/raw-exam/actions/runs/43031064207) demonstrates the hash-verified Microsoft name fix works. Specifically, **AB-900** and **AI-103** completed all eight real preparation stages with exit 0. Both are **needs_author**, not ready or published.
- AB-900: 89 source items, 37 text-visible answer keys, 52 visual items (25 candidate image keys, 27 without parsed visual key), and one undecided spelling correction on q050. The original source remains private. Private [review checklist](https://github.com/mathorax1-hue/raw-exam/blob/main/exams/AB-900/REVIEW-CHECKLIST.md) and [issue #2](https://github.com/mathorax1-hue/raw-exam/issues/2) identify the remaining work.
- AI-103: 130 extracted source items, 90 text-visible answers and 36 visual items without machine-read candidate keys. The [private checklist](https://github.com/mathorax1-hue/raw-exam/blob/main/exams/AI-103/REVIEW-CHECKLIST.md) records the IDs requiring human transcription.
- Re-ran private [destination-PAT verification](https://github.com/mathorax1-hue/raw-exam/actions/runs/43024897974), **attempt 2**; the job completed **success**, confirming private `ready-exams` access. No token value was revealed or stored.
- Updated the private [completion tracker issue #1](https://github.com/mathorax1-hue/raw-exam/issues/1) with these verified milestones. Remaining blocked source mappings, owner answer review, AI authoring and downstream checks must be completed before a draft can be promoted.
- The daily conditional readiness monitor checks for meaningful progress or user-action blockers. It is not a substitute for actual human review or publication sign-off.

## 2026-11-11: Protect private Actions credits and begin CertPassly Team AI authoring

- Confirmed GitHub's standard public runners are free for public repos, while GitHub Free private repositories have limited monthly included Actions compute. Do not assume public reusable workflow code makes a private-caller job free.
- Replaced the private raw-exam workflow's automatic 46-exam fanout with a cheap push sentinel and **manual-only real exam processing**. Default target is one exam, with a hard maximum of three manually selected jobs and max-parallel one. Added `start_index` for paginated batches. Capped per-exam job timeout at 40 minutes, set inventory retention to 3 days while keeping small private authoring-result artifacts for 14 days to avoid expensive re-extraction, and added skip-install checks for system PDF utilities. Synthetic cost planner tests passed in public processor CI.
- GitHub cancelled the older expensive fanout, and [private budget sentinel run 43035259600](https://github.com/mathorax1-hue/raw-exam/actions/runs/43035259600) passed without real exam jobs. Later short workflow-update sentinel runs also passed.
- Both private PDF import workflows now run **only manually**, avoiding unintended full reimports on catalog or workflow edits.
- Private ready-exams verification now checks **only changed releases and their ZIPs** on normal pushes. Removed weekly all-release scans. Explicit manual `full_audit: true` remains available. [Private verification run 43035883822](https://github.com/mathorax1-hue/ready-exams/actions/runs/43035883822) passed. This does not prove any real exam has yet shipped.
- Public exam Actions now own pinned upstream regression tests, two full synthetic demo pipelines and schema/lint tests; heavy full synthetic QA has a weekly public schedule. The unsafe public real-owner-data pipeline mode was retired. No private owner questions, PDFs, tokens or drafts enter public Actions.
- The generated release metadata and destination proof verifier require the organizational editorial byline **CertPassly Team** and the honest status `AI-assisted draft; independent human subject review pending`. See [AI editorial policy](AI-EDITORIAL-POLICY.md). This is a team editorial credit, not a false individual byline or a human sign-off.
- Commenced actual editorial work: five original, option-by-option AB-900 explanation drafts were committed to private `raw-exam/exams/AB-900/authoring-drafts/round-001.json` (commit `04a6c0ba42b63aa9440d5641a675fe9bebbd008c`). These are deliberately flagged `key_could_not_be_checked` until official pages are cached and hashed; they are NOT ready author inputs.
- Created daily ChatGPT automation `Prepare CertPassly author drafts` to work on small, grounded private author batches, beginning 2026-11-12 at approximately 09:00 Pakistan time. It may commit private verified drafts and report blockers, but must never invent keys or human approvals, or trigger private Actions merely for partial authoring.
- The private raw-to-ready PAT access test previously passed on attempt 2, with no token value viewed or stored.
- Remaining reality: 185 raw source folders, zero independently verified ready releases at last check. Mapping gaps, visual answer review, full AI author JSON and validation still need completion; publication is separate.

- Follow-up: the private source job's `exam-result-*` artifacts remain available for 14 days for grounded AI writing, while lightweight inventory artifacts expire after 3 days. This preserves authoring evidence without repeatedly spending private runner minutes.


## 2026-11-12: Reusable evidence tools and private recovery workflow

- Central skill source remains public \`msaqlainhaneef1/certpassly-exam-pipeline\` at pinned revision \`13dea6bab662ab1c4bbf87017e912e519907c8bc\`. Connected accounts currently have read but not direct push permission there; **this is not an upstream skill commit**.
- Added \`scripts/audit_question_evidence.py\` at commit \`7233b418a27a20775069f6195b6525c4b57cc45e\`, with synthetic tests committed at \`3060dacb1d70685e86811e2ba7560c07fcf72263\`. It distinguishes AI source-supported checks from final approvals and fails closed on missing proof, unsigned review, record mismatches or unresolved conflicts.
- Added \`scripts/unpack_artifact_tree.py\` at commit \`e14d0f58f823506d7fbecfea8de011af9eef07a9\`, with synthetic tests committed at \`b73e57d9841f3e43d515af83f331f5d4bd009f12\`. It turns nested ZIP artifacts into plain directories with SHA-256 file manifests and guards against unsafe paths and collisions. The extraction ZIP is input only, not a committed output.
- Both tools use **Python standard library only**; no new pip dependencies, credentials or private owner data. Ten synthetic tests passed locally. Public processor test Action \`43183489036\` concluded success on commit \`b73e57d9841f3e43d515af83f331f5d4bd009f12\`.
- Upstream migration still needed: maintainer-authorized commit of these generic scripts and tests to the main skill repo, update AGENTS.md/HANDOVER.md/operator guide, run upstream tests on Linux and Windows, and then explicitly review the raw-exam workflow pin. Do not silently repin or claim the upstream skill has been upgraded.
- Private AB-900 recovery snapshot has a separate handover at \`raw-exam/docs/AI-SESSION-HANDOVER.md\`. Do not move its question records, screenshots, archive, or private chat content into this public repo.
- This tooling is supplementary. It cannot bypass image/answer review, official source SHA-256 evidence, owner key conflicts, writing and bank gates, independent proof verification or site publication approval.


## 2026-11-17: Weekly upstream review and repository visibility check

- Verified GitHub repository metadata: `mathorax1-hue/exam` is **public**, not private. Corrected the operations handbook and made the public-data boundary explicit. The tracked tree contains no owner PDF, archive, image, office-document file, or owner-data directory; keep all real source material, question text, answer keys, private links, authoring drafts, and exam packages in private `raw-exam` / `ready-exams` or approved private storage. No repository visibility setting was changed.
- Reviewed this repository's agent instructions, operations handbook, upstream status, work log, and all three workflows. Read the upstream instructions, skill, operator guide, training exercises, lessons, and relevant site-format/OCR/fidelity guidance at the reviewed pin `13dea6bab662ab1c4bbf87017e912e519907c8bc`, then compared them with upstream `main` at `d9b6bf67efb870019dd88caeffa90952b7e000d3`.
- Upstream `main` is 14 commits ahead and identifies as v1.3.0. The candidate adds a site-format v2 exam JSON export, a separate technical-only default path, local Tesseract OCR, mutually exclusive question-type rules, dual-pass OCR agreement, 100% source-word coverage with no extra words, and a strict fidelity gate that holds uncertain items instead of guessing. The research/AI authoring path remains separate. No upstream source was copied into this repository.
- Upgrade review findings: upstream's 15 Nov test table reports substantial held-item counts on the four sample PDFs (including 44 of 92 for AB-730), so the new gate improves conservatism but does not make every exam complete. The v2 schema is copied from site worktree commit `a3009daa5758a4401ceadd9cf765d8a36bff22bc`; upstream says the site v2 feature flag is off by default, official link hosts need configuration, and unresolved answer-reveal/security and trial-entitlement issues block production use. The release notes do not establish an AB-900 result or live importer acceptance.
- Candidate upstream CI [run 43702498376](https://github.com/msaqlainhaneef1/certpassly-exam-pipeline/actions/runs/43702498376) passed all four Linux/Windows and Python 3.11/3.13 matrix jobs (178 tests per job). Earlier 15 Nov candidate runs exposed a missing Windows Tesseract PATH setup and a missing `os` import; later commits fixed those and the latest matrix is green. Latest logs still show Python `ResourceWarning` messages in `package_guard.py` and Node.js 20 deprecation warnings for `actions/checkout@v4` / `actions/setup-python@v5`.
- This workspace's latest upstream-watch [run 43926791440](https://github.com/mathorax1-hue/exam/actions/runs/43926791440), processor test [run 43902282496](https://github.com/mathorax1-hue/exam/actions/runs/43902282496), and pinned synthetic QA [run 43845165104](https://github.com/mathorax1-hue/exam/actions/runs/43845165104) all concluded **success**. The processor suite ran 40 tests; pinned skill CI ran 112 tests, and both synthetic demos reported 429 checks passed with 25/25 import-conformance files. The scheduled upstream-watch has already recorded the latest observed upstream SHA in `docs/UPSTREAM_STATUS.md`.
- Decision: keep the executable workflow pin at `13dea6bab662ab1c4bbf87017e912e519907c8bc`. Do not upgrade until a separate reviewed change proves v2 importer compatibility, resolves the site-side reveal/security and entitlement blockers, evaluates held-item handling, and passes synthetic plus owner-authorized representative tests. No real owner exam was run, no private artifact was opened or changed, and no release was promoted.

The three-phase workflow applies every certpassly-exam-skill/patches/upstream/v1.3.0-*.patch to pinned v1.3.0, in name order (ligature complete-words, then OCR retry / review sheet / owner corrections), until those fixes are in an upstream tag. The site import gate remains local only.
