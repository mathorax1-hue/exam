# CertPassly exam workspace

This **public code-only repository** is the control and operating workspace for the [CertPassly exam pipeline](https://github.com/msaqlainhaneef1/certpassly-exam-pipeline).

It does **not** contain a vendored copy of the upstream proprietary skill. GitHub Actions checks out a pinned upstream revision and installs it temporarily on a runner.

## Start here

1. [AI agent instructions](AGENTS.md) explain what agents must read and what they must never do.
2. [Operations handbook](docs/CERTPASSLY-OPERATIONS.md) has the full local runbook, stage map, author files, security policies and completion checklist.
3. [Skill installation and demo tests](.github/workflows/certpassly.yml) run in GitHub Actions, with an option for a configured real exam.
4. [Upstream revision status](docs/UPSTREAM_STATUS.md) records new source revisions without silently upgrading them.
5. [Repository work log](docs/WORK-LOG.md) contains decisions, evidence, unresolved items and changes.

## Execute

Visit [GitHub Actions](https://github.com/mathorax1-hue/exam/actions/workflows/certpassly.yml), choose **Run workflow**, and select **verify** to install, run Python tests, run both synthetic demo pipelines, and check the demo import files.

Real `pipeline` runs need properly configured workspace inputs and confirmed usage rights. The `author` stage requires separate AI/human-authored files and will stop if they are absent. It is not a hosted AI service.

No real exam questions, private owner PDFs, or private Drive links belong in Git commits to this public repository. Do not treat the synthetic demo as a real exam or the static import checker as a live-site import test.

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
