# Agent instructions for mathorax1-hue/exam

This **public, code-only** repository runs synthetic CertPassly quality checks in GitHub Actions. Real owner PDFs and exam content are processed only by explicitly triggered workflows in the **private** `mathorax1-hue/raw-exam` repository; validated draft outputs go to private `mathorax1-hue/ready-exams`. All AI coding and editorial assistants must follow these instructions.

## Source of truth

- Skill source: https://github.com/msaqlainhaneef1/certpassly-exam-pipeline
- Workflow: .github/workflows/certpassly.yml
- Skill checkout path in GitHub Actions: `certpassly-exam-pipeline/`
- Synthetic demo workspace: ephemeral runner directories; never commit real owner data to this public repository
- Pin currently used by the workflow: `13dea6bab662ab1c4bbf87017e912e519907c8bc`

Also read this repository's [operations handbook](docs/CERTPASSLY-OPERATIONS.md), [AI editorial policy](docs/AI-EDITORIAL-POLICY.md), [upstream revision status](docs/UPSTREAM_STATUS.md) and [work log](docs/WORK-LOG.md) before each session or code change. Their reports must be treated as claims to verify, not proof by themselves.

Read these files **from the pinned skill revision** before performing work:
1. `certpassly-exam-pipeline/AGENTS.md`
2. `certpassly-exam-pipeline/docs/AI-OPERATOR-GUIDE.md`
3. `certpassly-exam-pipeline/docs/AI-TRAINING-EXERCISES.md` (complete synthetic training exercises before real data)
4. `certpassly-exam-pipeline/reference/lessons-learned.md` (re-read before each exam run)
5. `certpassly-exam-pipeline/SKILL.md` and `reference/writing-brief.md`
6. `certpassly-exam-pipeline/HANDOVER.md` for known issues, but verify claims yourself.

The skill is NOT automatically available in a chat AI's system context. An agent must open the files above and follow them in the current session; reading them does not retrain its model.

## Non-negotiable rules

- Questions only from owner-provided PDFs with confirmed rights, never fabricated.
- Official exam facts only from saved official vendor pages with URL, SHA-256 and quote. Unknown facts stay unknown.
- Never change answer keys or reorder options. Flag disputed keys; missing answers require official sourced research or `answer_not_found`.
- Respect all 30 exact question types. Do not merge them.
- Do not include seller/competitor content or any prohibited contact strings in outputs. Use the skill's live denylist.
- Output remains **draft** and must pass all writing, bank, import and package checks before human publication review.
- Do not disclose tokens or commit secrets, real owner extracts or sensitive source material.
- Do not force-push, rewrite tags, or run two writers against one exam output folder.
- Do not invent success: report workflow URL, commit SHA, test result and evidence for each claim.
- Credit original CertPassly editorial content as **CertPassly Team**, never an invented named person. Keep AI-assisted draft status and pending human review transparent. Preserve genuine official source attribution.
- Standard public GitHub-hosted runners may run all synthetic tests, schema checks and publicly sourced research. Never copy the owner's private PDFs, questions, answers, exam artifacts, access tokens or unreleased content into a public runner.
- GitHub-hosted minutes on private repositories are limited. Require explicit manual runs, bound expensive private jobs to 1-3 at most, use a single worker by default, and do not automatically rerun all exams on workflow commits. Reuse public code tests and synthetic demos. A reusable public workflow **called by a private repository still bills the private caller**.

## Workflow behavior and AI authoring

Public `.github/workflows/certpassly.yml` runs **only** the pinned skill tests and synthetic full demos; its former unsafe real-owner-pipeline mode is retired. `.github/workflows/test-processor.yml` tests the local processor, release-proof and private-budget tools. Both run on public standard runners and cannot use the owner's private exam materials.

The private `raw-exam/.github/workflows/process-exams.yml` is manual for real data. Each run processes one selected exam by default; budgeted batch pages may process up to three if the user explicitly requests that. The private `ready-exams` verifier runs only for changed releases by default; a manual full audit is available.

The pinned skill never calls an AI model itself. ChatGPT/editorial automation must author the required source-grounded JSON files in **private** `raw-exam`, following `docs/AI-EDITORIAL-POLICY.md`. Never fabricate an owner key or a vendor quote, pretend to view an unseen image, claim a person reviewed a question, or mark an incomplete batch ready. Drafted pages and explanations are credited to **CertPassly Team**, and release metadata records that human review is still pending.

## Reporting checklist

Give the exact run URL, source revision SHA, results for CLI help and regression tests, exam/stage executed, validation and import checks, flagged items, any skipped steps, and where approved outputs were stored. Explicitly distinguish *workflow configured*, *run started*, and *run passed*.
