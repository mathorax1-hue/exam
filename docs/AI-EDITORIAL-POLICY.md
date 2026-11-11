# CertPassly Team editorial and AI authoring policy

Effective: 2026-11-11

## Attribution

**Original content produced for CertPassly must use the organizational editorial credit `CertPassly Team`, not a named individual author.**

- Generated exam explanations, study guides and landing-page prose may show the byline **Prepared by CertPassly Team**. This is an editorial brand credit, not a claim of an individual human author's identity or qualification.
- Final package `release.json` must set `author` and `editorial_credit` to `CertPassly Team`, with `editorial_process: AI-assisted draft; independent human subject review pending`.
- Where structured page schema does not support a distinct author field, include the editorial credit in a normal, unobtrusive paragraph of original prose when appropriate. Do **not** add a fabricated `author` property to the skill's strict CSV schema or misattribute a source vendor.
- The team credit is only for new CertPassly editorial material. Preserve official vendor names, exam codes, the source document's bibliographic attributions and owners' rights. Do not claim a nonexistent person reviewed an answer.
- Do not claim the draft is fully human-written. AI can write a draft, but the output remains flagged as AI-assisted and subject to human fact verification.

## Division of work and compute

| Work | Execution | Private Actions minutes |
| --- | --- | --- |
| Script lint, Python tests, synthetic demos, schema and regression checks, public upstream-version watch | Public `mathorax1-hue/exam` Actions | None for standard public runners |
| Read owner PDFs, extract images, inspect questions and owner answer keys | Private `raw-exam` Actions, manually triggered and capped | Yes, minimize |
| AI editorial analysis and writing of source-grounded explanations, page prose, and text-fix decisions | Connected ChatGPT session / scheduled authorized AI workflow, reading private material only through the private connector | No GitHub Actions minutes when no runner invoked |
| Validated ZIP promotion and its focused proof scan | Private source/destination Actions | Only when required |
| Human evidence/visual review and actual production importer approval | Authorized reviewers in private workflow | No routine Actions job required |

The public Actions runner **must not** be supplied owner PDF text, private exam extracts, answer-key files, private artifacts or repository credentials. A reusable workflow invoked from a private repository is still billed to the private caller. Do not send those files to public Actions to sidestep the free-plan compute quota.

## AI editorial procedure for each exam

1. Read the upstream pinned `AGENTS.md`, operator guide, writing brief and the private source manifest, raw questions, visual exhibits and official source snapshots.
2. Distinguish exactly what the owner PDF states from what the official vendor says. Cite the saved URL, SHA-256 and verbatim source quote for official facts.
3. Read questions and answer regions faithfully. Preserve owner answer keys, options, type and order. Never invent missing answers, original question stems or proof of correctness.
4. Draft the required JSON files in private `raw-exam/exams/<CODE>/authoring/`: `explanations_text.json`, `explanations_visual.json`, `page_prose.json`, `bank_meta.json`, and the other decision files when applicable. Drafts must follow the exact pinned skill schemas, not invented formats.
5. For visual questions, obtain and inspect the **actual images** before providing `visual_transcription.json`. If unreadable, mark unresolved and exclude from scoring or stop release; never infer a choice.
6. Verify the prose is original, plain English, accurate to the source and free of vendor impersonation, seller/competitor marketing and sensitive contact details. The editorial credit should say `CertPassly Team`.
7. Commit only reviewed draft material to private `raw-exam`, with work-log and citations. Perform heavy source processing only when needed, after local/content review is complete. Do not rerun a private pipeline simply to see whether author files are still missing.
8. Before promotion, require the full writing, question-bank, content, import-conformance, 64 skill validation gates, package scanner and independent source-to-output proof audit to pass. Packages stay `validated_draft`, not published, pending reviewer and live importer acceptance.

## Actual automation limitations

The pinned CertPassly scripts **do not call an AI model**. GitHub Actions cannot autonomously use the ChatGPT model merely because its instructions mention an author stage. The writing must be produced in an AI session with authorized access to the private inputs, followed by explicit source/evidence review. A scheduled ChatGPT task can attempt small, grounded author batches, but must not claim to have completed work if it could not access the sources or did not commit evidence.

The daily readiness/authoring automation can continue progress and report blockers, but does not guarantee all 185 owner exams will become fully validated without human visual-review and missing-official-source decisions.
