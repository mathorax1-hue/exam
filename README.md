# CertPassly exam workspace

This **public code-only repository** is the control and operating workspace for the [CertPassly exam pipeline](https://github.com/msaqlainhaneef1/certpassly-exam-pipeline).

It does **not** contain a vendored copy of the upstream proprietary skill. GitHub Actions checks out a pinned upstream revision and installs it temporarily on a runner.

## Start here

1. [AI agent instructions](AGENTS.md) explain what agents must read and what they must never do.
2. [Operations handbook](docs/CERTPASSLY-OPERATIONS.md) has the full local runbook, stage map, author files, security policies and completion checklist.
3. [Skill installation and full synthetic demos](.github/workflows/certpassly.yml) run in free public GitHub Actions only. They never use owner PDFs or answer keys.
4. [Upstream revision status](docs/UPSTREAM_STATUS.md) records new source revisions without silently upgrading them.
5. [Repository work log](docs/WORK-LOG.md) contains decisions, evidence, unresolved items and changes.

## Run public QA

The public [CertPassly synthetic QA](.github/workflows/certpassly.yml) workflow runs pinned skill regression tests, two complete synthetic demo pipelines and their import checks. It runs weekly or manually. [Public processor tests](.github/workflows/test-processor.yml) run on changes to processor code and tests.

Real owner-PDF processing happens only in the private `raw-exam` Actions workflow. It is manually triggered, runs one exam by default, has a strict limit of three exam jobs, and uses `start_index` to page through eligible sources. GitHub Actions compute in a private caller is still private-billed even if it invokes public reusable workflow code.

Original editorial content uses the **CertPassly Team** byline. See [AI editorial policy](docs/AI-EDITORIAL-POLICY.md). It records AI-assisted draft status, source evidence and pending human review.
## Private raw → processing → private ready workflow

The production-style batch workflow is in [private raw-exam Actions](https://github.com/mathorax1-hue/raw-exam/actions/workflows/process-exams.yml). It runs **from** the private raw-exam repo, checks out public processor scripts at a reviewed commit, and installs the pinned upstream skill. Only the matching exam's PDF is fetched from Git LFS, SHA-256 verified and copied into a temporary runner workspace.

The [planner](scripts/plan_exam_processing.py) records all source directories; sources with missing official exam mapping, ambiguous aliases or multiple PDFs are blocked for review. The [per-exam runner](scripts/process_raw_exam.py) completes catalog through intent, then stops at `needs_author` when reviewed authoring files are absent. The skill does not invoke an AI model itself.

An exam can be promoted to [private ready-exams](https://github.com/mathorax1-hue/ready-exams) **only after** the author files are supplied and author, pages, writing, import, bank, validate, conformance and package scan pass. The private raw repository keeps per-run status dashboards in `reports/processing/`. No source PDF or incomplete draft is promoted.

The `CERTPASSLY_REPOS_PAT` secret must be configured in the **private raw-exam** repository's Actions secrets, with Contents read/write access to private `ready-exams` for gated cross-repo promotion. Do not copy PATs into public files.

## Source import and proof-backed releases

The original exam PDFs are imported and stored only in the [private raw-exam repository](https://github.com/mathorax1-hue/raw-exam), with Git LFS and SHA-256 manifests. The old public Drive intake workflow has been retired because it was superseded by the private raw-source architecture.

The public processing code provides [release evidence generation](scripts/build_release_evidence.py). Every fully prepared exam must create a traceable proof bundle before the private workflow pushes to [ready-exams](https://github.com/mathorax1-hue/ready-exams). The destination runs an independent [release verifier](https://github.com/mathorax1-hue/ready-exams/blob/main/scripts/verify_releases.py), checks source-page digests, all question and bank checks, and rescans the ZIP.

[Ready-exams release contract](https://github.com/mathorax1-hue/ready-exams/blob/main/docs/RELEASE-CONTRACT.md) defines the exact evidence files. Passing all automated gates means an **evidence-backed validated draft**, not a 100% factual guarantee or website publication.

## Maintenance

The separate [upstream-watch workflow](.github/workflows/upstream-watch.yml) checks upstream main on Mondays at 08:00 UTC. It commits a change to the **revision status document only if the upstream SHA or reviewed pin changed**. It does not auto-upgrade executable code. Any changes to the pin require an explicit review and new tests.

The skill source is marked proprietary by its author. Refer to it by Git URL rather than copying or republishing its implementation.
