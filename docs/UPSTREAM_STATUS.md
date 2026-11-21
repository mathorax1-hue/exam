# CertPassly upstream revision watch

- Source repository: https://github.com/msaqlainhaneef1/certpassly-exam-pipeline
- Workflow's reviewed source pin: `c8d4400598c225c6a32f029f28ca24429649edd6` (tag v1.3.1)
- Previous pin (kept for the older private process-exams.yml until that workflow is reviewed separately): `13dea6bab662ab1c4bbf87017e912e519907c8bc`
- Latest observed upstream main: `c8d4400598c225c6a32f029f28ca24429649edd6`
- Revision observation date (UTC): `2026-11-21`
- Schedule: Mondays at 08:00 UTC (13:00 Pakistan Standard Time)
- Policy: Record upstream changes with a Git commit when the observed revision changes. Never auto-upgrade unreviewed revisions.
- Upgrade procedure: Read `docs/CERTPASSLY-OPERATIONS.md`, compare upstream changes, review instructions and tests, then update the pin by a reviewed change. The three-phase workflow now uses v1.3.1. The public synthetic QA workflow pin is updated in a later change so this commit does not start that path-triggered job.

The heavy three-phase job now runs in this public exam repository so minutes bill to the public account. Private raw-exam keeps the owner data and, by default, only dispatches the public runner. A private reusable fallback remains, disabled by default. Public logs print counts only, and a leak-check scans the published job log for question text. The three-phase workflow checks out pinned v1.3.1 and applies any leftover certpassly-exam-skill/patches/upstream/v1.3.1-*.patch files in name order. The v1.3.0 skill patches are already in that tag. The site import gate remains local only.
