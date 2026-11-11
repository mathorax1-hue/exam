# CertPassly operations and handoff

Last reviewed: 2026-11-11
Workspace repository: `mathorax1-hue/exam` (private)
Upstream skill: https://github.com/msaqlainhaneef1/certpassly-exam-pipeline
Pinned upstream revision: `13dea6bab662ab1c4bbf87017e912e519907c8bc`

This is an operational summary for this workspace, **not** a redistribution of the upstream proprietary skill. Always read the original upstream `AGENTS.md`, `SKILL.md`, `docs/AI-OPERATOR-GUIDE.md`, `docs/AI-TRAINING-EXERCISES.md`, `reference/lessons-learned.md`, `reference/writing-brief.md`, and `HANDOVER.md` at the exact pinned revision before a real run. Use `AGENTS.md` here as the entry point.

## Architecture and authority

```text
mathorax1-hue/exam (this repo)
  AGENTS.md                         This repo's agent instructions
  .github/copilot-instructions.md   Copilot entry point
  .github/workflows/certpassly.yml  Install, test, demo, optional exam
  .github/workflows/upstream-watch.yml  Weekly upstream revision record
  docs/CERTPASSLY-OPERATIONS.md     This handoff
  docs/UPSTREAM_STATUS.md           Observed source revision vs pin
  workspace/                        Optional owner-supplied exam workspace

GitHub Actions runner (temporary)
  repo/                              This repository checkout
  certpassly-exam-pipeline/          Upstream pinned source checkout
```

The Actions runner installs the skill from upstream with `pip install -e`. The source code is not copied or vendorized into this repository. The upstream project is proprietary, and should not be republished without permission. GitHub Actions does not run the ChatGPT model, independently author questions, access the CertPassly site, modify a database, or publish content.

## Operator training status

The core upstream instructions and manual were reviewed for this setup. Reading is **not** proof of completing the graded training exercises or a model-weight update. The workflow runs the offline Python test suite and synthetic demo pipelines. The exercises in `docs/AI-TRAINING-EXERCISES.md`, Levels 0 through 6, include deliberate break/fix cases and must be completed and evidenced separately before claiming a person or agent has passed all training levels.

## Hard rules

- Use official vendor product names, exam names and codes exactly. CertPassly is the site brand.
- All exam facts require a saved official vendor page with source ID, URL, SHA-256 and exact supporting quote. An unpublished fact remains "not published by the vendor".
- Accept questions only from owner-supplied PDFs with confirmed rights, never invented question stems, options, or keys.
- Do not change a keyed answer or option order. Flag wrong, outdated, or arguable owner keys and explain the evidence.
- A missing answer is researched only against saved official sources. If still missing, mark `answer_not_found` and exclude from scoring. Do not pretend it was verified.
- Keep all 30 question types distinct; image-only items require a visual check. Skip binary VCE input.
- Remove seller, competitor, contact and marketing lines using the configured denylist. Do not output banned terms in reports. Never ship raw extracts or unredacted cleanup files.
- Apply only spelling, grammar, or punctuation repairs to question text. The key and option-order identity digest must remain equal. Log changes.
- Use plain English, short sentences, no typographic dashes and no banned stock AI phrases. Edit only flagged writing parts and rerun the writing check.
- Pages and bank remain **draft**. Require human publish review. Do not claim conformance with a live importer without a live site test.
- Never commit real source PDFs, extracted questions, credentials, private links, keys or package data to Git. Never force-push.
- Run only one writer per `out/<EXAM>/` folder.

## Pipeline stage map

1. `catalog`: owner sheet or catalog and reviews
2. `intake`: files, hashes, rights confirmation
3. `sources`: saved official vendor HTML/text and source hashes
4. `research`: official facts and gaps
5. `extract`: text and visual extraction from owner PDF
6. `textfix`: correction proposals, protected words
7. `answer_research`: official source evidence for missing keys
8. `intent`: search questions based on sourced facts
9. `author`: batched AI-authored files supplied separately
10. `pages`: draft pages and shared sections
11. `writing`: writing gates and targeted fix list
12. `import`: site-format CSV and metadata
13. `bank`: question types, explanations, settings and review logs
14. `validate`: validation gates, bank checks and hashes
15. `package`: sanitized, scanned draft zip

The runner only **checks** the presence of author files at stage 9. It does not call an AI. Missing inputs stop the run; do not invent them to make the workflow green.

## Private source intake and proof-backed release architecture

Owner exam inputs and Google Drive links are stored only in private `mathorax1-hue/raw-exam`; source PDFs are kept with Git LFS, each verified against its recorded SHA-256 manifest. The public `exam` repository contains script and workflow code only. The former public `.github/workflows/exam-intake.yml` has been retired in favor of the private raw repository's import and processing workflows.

For real exam processing, use `raw-exam/.github/workflows/process-exams.yml`. A source must have a real official exam code, matched vendor, rights statement, and exactly one chosen PDF before it is queued. The workflow executes pinned CertPassly stages and records private per-exam artifacts. Missing official source snapshots, reviewable question keys, and absent AI authoring files are explicit blockers.

A fully authored exam passes the upstream bank, writing, validation, import-conformance and package-guard checks. The additional public `scripts/build_release_evidence.py` captures source provenance, official vendor page hashes and quotes, question audit, stage exit codes and a cryptographic proof manifest. Only when the evidence proof also passes may the private runner promote the result to private `ready-exams`, which independently verifies every evidence file and rescans the package.

See the [ready-exams release contract](https://github.com/mathorax1-hue/ready-exams/blob/main/docs/RELEASE-CONTRACT.md). The stored result is `validated_draft` and remains unpublished pending accountable human subject-expert review and an actual production importer test. Do not call it 100% accurate solely because automated tests passed.

## Configuring a real exam

Create the following under `workspace/` only when authorized and when the data is safe to stage. Prefer a private artifact store for owner PDFs rather than committing them.

```text
workspace/
  config/pipeline.yaml              Derived from upstream config/pipeline.example.yaml
  config/vendors.yaml               Derived from upstream config/vendors.example.yaml
  sheet.csv or catalog.csv
  owner-files/<EXAM>/                Input PDF, handled securely outside Git where possible
  sources/<vendor>/                  Cached official pages with SHA-256
  cache/linkcheck.json               Required for offline validation of external links
  research/                           Sourced exam facts and author inputs
  out/<EXAM>/authoring/              Required before AI author stage passes
```

Edit `owner_rights_statement` in `workspace/config/pipeline.yaml` based on the actual owner's permission. Do not fabricate consent. Offline mode cannot discover sources that are not already saved; without cached official sources and link checks, a clean runner may stop at research or validation.

Start with `verify`. To run a real exam, use GitHub Actions > CertPassly skill environment > Run workflow > `pipeline`, supply its code, and choose online/offline intentionally. Avoid putting real exam questions in a Git commit. GitHub-hosted runners are ephemeral and must not be treated as persistent storage.

## Author-stage input contract

Files go under `workspace/out/<EXAM>/authoring/`, with visual transcription under `out/<EXAM>/extracted/`. See upstream manual section 7 for exact examples.

- `explanations_text.json`: original short explanations and one option rationale per text item; researched evidence IDs and accuracy flags
- `explanations_visual.json`: explanations shaped to the grid, dropdown or drag-and-drop item
- `page_prose.json`: original prose for seven page types, sourced claims, title and description candidates, shared keys
- `bank_meta.json`: topic mapping, off-syllabus notes, cover conflicts and skipped files
- `answer_research.json`: official quote and source for items with no owner key, if available
- `text_fixes_decisions.json`: accepted or rejected undecided spelling/grammar proposals, with explanations
- `extracted/visual_transcription.json`: human-reviewed transcription of visual items when needed

Never copy synthetic training demo prose into a real exam; it illustrates the file structure only.

## Before declaring a real exam complete

1. Record each executed stage and exit code; explain all skipped or blocked stages.
2. Confirm all current `validate` checks pass and `check_bank` reports zero failures.
3. Run `python scripts/check_import_conformance.py --root <workspace> --exam <CODE>` with exit 0.
4. Confirm the writing check is current and has 0 flags.
5. Confirm item counts, types, key identity, flags and missing-answer status in `REVIEW.md`.
6. Confirm package scan has 0 denylist hits. Record package bytes and SHA-256; never log banned text.
7. Record official source URLs, hashes and quotes, owner input hashes, and any reviewer decisions.
8. Distinguish import *file conformance* from an actual site importer test and draft output from publication.

## Reporting and changes

Use upstream operator guide section 13 as the full run-report template. Record date, exam, vendor, skill revision, GitHub run URL, source hashes, stage exit codes, bank counts, validation, test versions and owner decisions. Use `docs/WORK-LOG.md` for our repository-level changes; do not include proprietary input text.

When updating the skill revision:
- Review `docs/UPSTREAM_STATUS.md` and upstream changelog, compare changed scripts and instructions.
- Run all tests and the synthetic demos for the candidate revision.
- Update the workflow pin **only after a review**; do not automatically follow upstream main.
- Commit changes with proof. Do not force-push.
- Weekly upstream monitoring records a changed upstream SHA, but never deploys unreviewed upstream code.

## Known unresolved details

- The real site's importer acceptance of researched/unverified key fields has not been proved by the upstream project's static checks.
- Offline validation needs a saved link-check cache and vendor sources.
- PDF extraction can be affected by Poppler versions and lost ligature glyphs.
- The original skill has no built-in cross-process lock for concurrent runs writing the same exam output.
- The operator and AI training exercise paths are not a claim that the ChatGPT model itself has been trained.
