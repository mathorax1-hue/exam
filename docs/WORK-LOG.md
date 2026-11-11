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

## Open items

- Confirm the expanded demo workflow run succeeds. Record its run ID and conclusion.
- Confirm weekly upstream-watch has write permission and records changes correctly when upstream advances. Its manual trigger may also be tested in GitHub UI.
- Complete all graded training exercises on synthetic data before claiming formal training completion.
- For a real exam: obtain owner-rights confirmation, configure the workspace, prepare saved official sources and author files, run all gates, and review the draft package. Do not commit owner inputs to this repository.
- Live site importer acceptance is not established by the upstream static conformance test.

## Logging rule

For later changes, record: date, what was changed, why, commit SHA, CI URL/result, source revision checked, validation evidence and unresolved decisions. Never put tokens, real question content, raw extracts, seller strings or private source material in this file.
