# Agent instructions for mathorax1-hue/exam

This repository runs the CertPassly exam pipeline in GitHub Actions. All AI coding assistants working here must follow these instructions.

## Source of truth

- Skill source: https://github.com/msaqlainhaneef1/certpassly-exam-pipeline
- Workflow: .github/workflows/certpassly.yml
- Skill checkout path in GitHub Actions: `certpassly-exam-pipeline/`
- Workspace path: `workspace/`
- Pin currently used by the workflow: `13dea6bab662ab1c4bbf87017e912e519907c8bc`

Also read this repository's [operations handbook](docs/CERTPASSLY-OPERATIONS.md), [upstream revision status](docs/UPSTREAM_STATUS.md) and [work log](docs/WORK-LOG.md) before each session or code change. Their reports must be treated as claims to verify, not proof by themselves.

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

## Workflow behavior

The Actions workflow checks out the pinned public skill into a separate directory, installs Python dependencies, runs `certpassly-pipeline --help`, runs regression tests, and runs two synthetic end-to-end demo pipelines with import conformance checks. It does not permanently install the skill into ChatGPT or copy the skill code into this repository.

To run manually: open Actions > CertPassly skill environment > Run workflow.

- `verify`: install and test only; no owner data required.
- `pipeline`: run on a configured exam code in `workspace/`; needs `workspace/config/pipeline.yaml`, vendor config, catalog and owner files as defined in the manual.
- Offline mode prevents fetching official sources; a clean runner requires previously saved official pages for a complete offline run.
- The `author` stage is an AI-authored batch of workspace files; GitHub Actions does not call an AI model. If it stops to request author files, generate and review those separately before rerunning.
- Runner files are ephemeral. Preserve only approved, non-sensitive output artifacts; avoid publishing raw owner PDFs or extracts.
- Exercise the synthetic demo and tests before running a real exam.

## Reporting checklist

Give the exact run URL, source revision SHA, results for CLI help and regression tests, exam/stage executed, validation and import checks, flagged items, any skipped steps, and where approved outputs were stored. Explicitly distinguish *workflow configured*, *run started*, and *run passed*.
