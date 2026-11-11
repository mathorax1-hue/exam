# CertPassly exam workspace

This private repository is the control and operating workspace for the [CertPassly exam pipeline](https://github.com/msaqlainhaneef1/certpassly-exam-pipeline).

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

No real exam questions or private owner PDFs belong in Git commits. Do not treat the synthetic demo as a real exam or the static import checker as a live-site import test.

## Real exam intake without committing owner PDFs

The [secure exam intake workflow](.github/workflows/exam-intake.yml) accepts the exam code, official vendor, an owner-authorized Drive **folder** URL and a rights confirmation during a manual GitHub Actions run. It creates a temporary workspace, executes the pre-author stages using the pinned skill and uploads only a metadata summary, not the PDF or extracted questions.

**Important:** The Google Drive folder must be readable by the GitHub runner without ChatGPT's connected Google Drive account. A link that only works through a private Google login will fail. Workflow inputs are recorded in GitHub Actions run metadata, so treat folder URLs as sensitive and use only folders you are permitted to share with that runner. This job does not complete the required AI author stage or produce a final exam package.

AB-900 intake findings: [docs/AB-900-INTAKE.md](docs/AB-900-INTAKE.md).

## Maintenance

The separate [upstream-watch workflow](.github/workflows/upstream-watch.yml) checks upstream main on Mondays at 08:00 UTC. It commits a change to the **revision status document only if the upstream SHA or reviewed pin changed**. It does not auto-upgrade executable code. Any changes to the pin require an explicit review and new tests.

The skill source is marked proprietary by its author. Refer to it by Git URL rather than copying or republishing its implementation.
