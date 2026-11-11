# AB-900 real exam intake

Status: **Intake and official-fact preflight complete; authoring, validation and packaging NOT complete**
Date: 2026-11-11
Exam: Microsoft AB-900
Official certification: Microsoft 365 Certified: Copilot and Agent Administration Fundamentals
Source: owner-authorized PDF in connected Google Drive, referenced in owner-provided exam sheet (no private Drive ID or URL stored here)
Upstream skill pin: `13dea6bab662ab1c4bbf87017e912e519907c8bc`

## Owner permissions

The owner explicitly confirmed in chat on 2026-11-11 that they have permission to use the PDFs to prepare exam materials. This is a statement by the owner, not independent legal verification. No original file content or raw extracted questions are committed to this repository.

## Private PDF preflight evidence

- PDF filename: `AB-900 (89 Questions).pdf`
- Byte size: `2,850,806`
- SHA-256: `e0e989699408066d157b41929d2b2bbaec6386e596a9645adacb0b48f3bc6001`
- Page count: `92`
- Unique numbered questions: `89`, consecutively 1 through 89
- Numbered questions with visible one-letter answer strings in PDF text: `37`
- `HOTSPOT` questions whose textual `Correct Answer:` field is blank: `52`
- The 52 items require image-region inspection and visual transcription. Do not assume they have no answer; keyed answers may be shown in images instead of text. No key was guessed.
- Image-bearing pages: `78`; embedded image references across the PDF: `110`. These counts describe the PDF's structure, not the number of actual question exhibits.
- Cover and introductory material contain seller text and marketing lines. These must be removed from generated outputs by the skill's cleanup and package gates; raw extracts must not be shipped.

## Official Microsoft exam facts (checked 2026-11-11)

1. Official exam page: https://learn.microsoft.com/en-us/credentials/certifications/exams/ab-900/
2. Official study guide: https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ab-900

Facts observed on the current official Microsoft pages:
- Exam duration: **45 minutes**
- Passing score: **700 or greater**
- The study-guide's skills measured are effective from **2026-10-14**
- Current skills/weights:
  - Identify the core features and objects of Microsoft 365 services: 30-35%
  - Understand data protection and governance tasks for Microsoft 365 and Copilot: 35-40%
  - Perform basic administrative tasks for Copilot and agents: 25-30%

### Owner cover conflicts

The supplied PDF's cover lists `Passing Score: 800` and `Time Limit: 120 min`, which disagree with the official Microsoft pages above. For all draft exam settings, **use official 700 and 45 minutes**, not the owner-cover figures. Record those conflicts in `bank_meta.json` and `REVIEW.md` during authoring.

These official facts are a preflight human/AI research summary. They do **not** substitute for the skill's saved vendor-page source files with verifiable URL, SHA-256 and exact quote. The real pipeline must create that evidence before validation.

## Immediate next stages

1. Securely stage the owner PDF outside Git on the pipeline runner. The current GitHub Actions checkout has no authenticated Google Drive session; do not assume that a Drive folder visible to ChatGPT is anonymously fetchable from the runner.
2. Generate the workspace configuration from the pinned upstream examples, including the actual rights statement and current date, without modifying upstream defaults for safety gates.
3. Save and hash the official Microsoft exam page and study guide, and record sourced facts, source quotes and gaps.
4. Run intake, extract, textfix, visual classification and answer research. Use the source PDF SHA above to verify correct input.
5. Visually inspect the 52 hotspot/image-keyed questions. Preserve original question and option wording and keys; flag any unavailable image or unresolved answer.
6. Create batched AI author files, then run pages, writing, import, bank, validate, conformance and package. Do not mark draft items verified or published.
7. Review unresolved owner keys and generate an evidence-backed report with stage exit codes, counts, SHA-256, gate results, package scan and exact CI run URL.

## Explicit limits

- No real GitHub Actions exam pipeline has been dispatched.
- No PDF or extracted question bank is stored in Git.
- The preflight is not proof that the 52 visual items have been transcribed, that any answer is correct, or that the generated package passes validation.
- The pinned skill's synthetic tests passing is distinct from a real AB-900 end-to-end run.
