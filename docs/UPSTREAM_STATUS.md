# CertPassly upstream revision watch

- Source repository: https://github.com/msaqlainhaneef1/certpassly-exam-pipeline
- Workflow's reviewed source pin: `d9b6bf67efb870019dd88caeffa90952b7e000d3` (tag v1.3.0)
- Previous pin (kept for the older private process-exams.yml until that workflow is reviewed separately): `13dea6bab662ab1c4bbf87017e912e519907c8bc`
- Latest observed upstream main: `d9b6bf67efb870019dd88caeffa90952b7e000d3`
- Revision observation date (UTC): `2026-11-21`
- Schedule: Mondays at 08:00 UTC (13:00 Pakistan Standard Time)
- Policy: Record upstream changes with a Git commit when the observed revision changes. Never auto-upgrade unreviewed revisions.
- Upgrade procedure: Read `docs/CERTPASSLY-OPERATIONS.md`, compare upstream changes, review instructions and tests, then update the pin by a reviewed change. The three-phase workflow and the public synthetic QA workflow now use v1.3.0.

The three-phase workflow applies every certpassly-exam-skill/patches/upstream/v1.3.0-*.patch to pinned v1.3.0, in name order (ligature complete-words, then OCR retry / review sheet / owner corrections, then 400 dpi page-region retry and the AI vision hook, including the original-OCR AI acceptance check), until those fixes are in an upstream tag. The site import gate remains local only.
