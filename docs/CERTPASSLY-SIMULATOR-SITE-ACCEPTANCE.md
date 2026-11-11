# CertPassly.com simulator product and publishing acceptance

Date: 2026-11-11
Editorial owner: **CertPassly Team**
Target domain: https://certpassly.com
Status: **Product and publishing criteria established; actual website implementation and live importer have NOT been verified**

## Scope requested by the owner

CertPassly is intended as a browser-based practical certification simulator with unlimited practice, realistic exam sessions, learning resources and accurate answer explanations. `raw-exam` stores authorized source PDFs, public `exam` stores workflow code, and private `ready-exams` stores only validated draft packages with evidence.

The owner confirmed source usage rights, but this is not independent proof of each certification vendor's permission to redistribute protected live questions. For the public site, prefer **original, source-grounded exam-style questions** rather than claims to possess leaked or real live exam questions. Neither the site nor its practice content is officially affiliated with certifying vendors unless independently authorized.

## What I could verify about the website

The public website `https://certpassly.com` and `https://www.certpassly.com` could not be retrieved through the available public web retrieval during this review. Exact-domain search also returned no inspectable pages. This is an **access limitation**, not proof the domain is offline.

The connected GitHub account exposes the `exam`, `raw-exam`, and `ready-exams` repositories, but no identifiable website frontend/backend/importer source repository. The pinned CertPassly pipeline creates static import packages; it does **not** authenticate to a production CMS or deploy to certpassly.com. A live publication claim must wait until actual website admin access and importer API/schema can be inspected.

## Competitor feature benchmark

Verified against the providers' own feature documentation where available:

| Provider | Documented capability | CertPassly product requirement |
| --- | --- | --- |
| MeasureUp | Practice and Certification modes; filters by missed/unseen questions, objective and difficulty; detailed performance reports | Unlimited configurable learning sessions, realistic timed exam, clear weak-domain analytics |
| Boson ExSim-Max | Study versus Simulation modes; multiple question types, answer explanations, category review | Unanswered simulation must conceal hints and solutions; explanation visible only in study/feedback mode |
| Tutorials Dojo | Timed, Review, Section-Based and randomized test modes, recurring updates | Repeatable full-length, domain-wise, missed-only and randomized exams |
| Whizlabs | Practice tests combined with broader courses/labs (secondary comparison only) | Link each answer to official vendor learning resources when available |

Source links checked on 2026-11-11:
- https://docs.measureup.com/how-to-configure-the-launch-of-a-practice-test
- https://docs.measureup.com/how-to-review-a-practice-test-score-report
- https://www.boson.com/Files/Support/BEE_User_Manual.pdf
- https://portal.tutorialsdojo.com/faqs/
- https://www.measureup.com/blog/best-self-paced-it-exam-simulators-compared.html

These are competitors' described capabilities, not independent proof of all claims. Do not copy competitor proprietary wording, images or question text.

## The practice learner journey

1. Search by official vendor and exam code. Show official version/update date, domains, credible source citations and transparent availability.
2. Choose **Study Mode** (unlimited attempts, immediate explanations), **Timed Exam Mode** (answers concealed until submission), **Domain Practice**, **Review Mistakes** or **Quick Revision**.
3. Render the actual question type, not always a generic multiple-choice list. Support image-grounded dropdown, Yes/No, ordering, matching, hotspot and performance-based question interactions where official exam simulators use them.
4. Keep a question navigator, mark-for-review feature, timer, resume, unanswered warning, accessible keyboard navigation and mobile layout.
5. At the end, show a score, objective/domain breakdown, incorrect/unseen counts, rationales for each option and official reference links. Scores are study feedback, not official exam results.
6. Offer unlimited new attempts and domain drilling while clearly distinguishing repeats from unseen questions. Store session history and learning progress with account privacy controls.

## Critical visual-asset rules

- Many source PDFs contain **both** the unanswered question screenshot and an answer screenshot with the correct option visibly marked.
- Use the original screenshot bytes as ground truth and produce sharp, lossless display copies without generative alterations. Source resolution cannot be recovered if the original is blurred.
- Before the learner submits an answer, the simulator may display only a verified **question_prompt** image. A marked **answer_reference** image must be hidden from the frontend/client payload until feedback, including alt text, HTML data attributes, preloaded hidden images and API responses.
- For dropdowns/Yes-No and similar answer-area screenshots, the preferred final UI is **native accessible HTML interaction** constructed from verified question text/options, with source image as an evidence/reference asset. Do not use a low-resolution answer screenshot as the interactive widget.
- Preserve original images, SHA-256, per-image role, question ID, visual-key reviewer decision and its provenance in private `raw-exam`.
- Block release if an image role is unreviewed, the key is unverified, any answer image is exposed before submission, or assets are missing/illegible.

Image QA code: [`scripts/audit_visual_assets.py`](../scripts/audit_visual_assets.py). AB-900 private role evidence: `raw-exam/exams/AB-900/visual-role-audit.json`.

## Site-import acceptance gate (not yet executed)

The real site importer must be inspected rather than guessed. Required proof before production:

- Import format version and content schema confirmed from actual site code/API.
- Staging/dry-run import accepts one fully validated draft with zero broken relations or missing media.
- The rendered question count, answer count and question-type counts match `ready-exams` release evidence.
- Every question image loads at correct scale; answer-reference images and keys are **not accessible or visible before submission** in frontend and API responses.
- Study, timed, resume, retry, score, domain review and mobile/keyboard use have passed realistic end-to-end tests.
- An atomic publish/rollback path with content version, reviewer identity and exact package hash is recorded.
- Only authorized content is published; no original owner PDF, seller/competitor advertising, secrets, raw extracts or sensitive source paths are exposed.
- Actual site URL, release ID, import execution log, screenshot evidence and reviewer decision saved privately; update `published` only after the real website confirms.

### Access dependency

**Do not claim a live website import or publication** until the certpassly.com administrative console or actual website code/importer is available to the connected tools. GitHub proof gates alone establish only `validated_draft`.

Private GitHub Actions minutes are limited; use the free public `exam` repository for synthetic UI/schema tests and public code quality, and private runs only for specific authorized exam imports or media audits.
