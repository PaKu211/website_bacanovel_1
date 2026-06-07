# Bacanovel AGENTS.md

## Project Goal
Build **Bacanovel**, a light-novel website that can be completed quickly, maintained by a solo developer, and monetized with traffic + ads.

Primary objective:
- Get the site online fast
- Make every chapter indexable by search engines
- Keep hosting cost at $0 if possible
- Avoid overengineering

## Core Direction
**Bacanovel V3 is Hugo-first, SEO-first, static-first.**

Use this stack:
- Hugo Extended
- GitHub repo(s)
- Cloudflare Pages for hosting
- Tailwind CSS for styling
- Pagefind for search
- Giscus for comments
- localStorage for reading progress and bookmarks
- Cloudflare Web Analytics and Google Search Console

Do **not** default to Astro, SSR, Turso, R2, KV, or SPA chapter reading unless explicitly required later.

## Non-Negotiable Product Principles
1. One chapter = one unique URL.
2. Each chapter must be a real Hugo page rendered to HTML.
3. SEO must be preserved for every chapter.
4. Simplicity beats cleverness.
5. Anything that increases maintenance or blocks publishing should be avoided.
6. Monetization depends on traffic, not framework complexity.

## Current Preferred Site Model
- Homepage: novel list, latest updates, search entry point
- Novel page: cover, metadata, summary, chapter list
- Chapter page: readable text, prev/next navigation, ads, comments

Avoid SPA hash routing for chapter reading.

## Content Structure
Use this preferred structure:

```text
content/
└── novels/
    └── <novel-slug>/
        ├── _index.md
        ├── chapter-0001.md
        ├── chapter-0002.md
        └── ...
```

### Novel metadata in `_index.md`
Required fields:
- title
- slug
- author
- status
- genres
- cover
- summary

### Chapter metadata
Required fields:
- title
- chapter number
- novel slug
- date
- any additional source metadata needed for navigation or import

## Routing Rules
- Do not use hash-based routes for chapters.
- Every chapter must be reachable through a unique path.
- Prefer clean paths such as:
  - `/novels/<slug>/`
  - `/novels/<slug>/chapter-0001/`

## Search Rules
Use Pagefind.
Do not introduce an external search server.
Search should remain static and client-side.

## Comments Rules
Use Giscus if comments are needed.
Do not build a custom comment backend unless there is a strong later reason.

## Bookmark / Continue Reading Rules
Use browser localStorage.
Do not add accounts or a database for these features in V1.

## Ads Rules
- Keep ad placement modular using a partial like `layouts/partials/ad-slot.html`
- Do not hardcode a specific ad provider into page layouts
- Make it easy to switch between ad networks later
- Ads should not break readability

## Importer / Automation Rules
The importer is important. Treat it as a first-class part of the system.

The importer should:
- Fetch novel/chapter content from the source pipeline
- **Clean and aggressively sanitize content**
- Generate Hugo Markdown files
- **Implement rate-limiting / throttling**
- Preserve slug consistency
- Generate correct front matter
- Avoid duplicate chapters
- Output files into the Hugo content tree

The importer must be deterministic and safe to rerun.

## Repository Strategy
- **Must be separated from the start into two separate repositories:**
- `bacanovel-site` (Specifically for code, themes, Hugo layouts, configurations, and Tailwind)
- `bacanovel-content` (Specifically for imported text/markdown files under the `content/novels/` folder)
- Use Cloudflare Pages to build from the `bacanovel-site` repo, and pull the `bacanovel-content` repo as a git submodule or via build script fetch.
- Do not use branches as a long-term separation strategy.


## Memory Strategy
Use the following priority order for long-term context:
1. `AGENTS.md` for rules that must always be followed
2. Checked-in docs for project-specific conventions
3. Git commit history and repo structure for implementation details
4. Optional memory service only for soft preferences, recurring workflows, or helpful reminders
5. Use mem0 for memory

### Canonical Rule
`AGENTS.md` is the source of truth for project behavior. Never rely on external memory as the only place where important rules live.

### Recommended Default for Bacanovel
- Do not add an external memory service yet unless there is a clear pain point.
- If an external memory service becomes necessary later, prefer a self-hostable or open-source option first.
- Keep the canonical project rules inside `AGENTS.md`, not inside memory only.
- Store only stable preferences or recurring workflow hints in memory; do not store anything that changes the project’s technical rules.

### Best-Fit Choice If Memory Is Needed Later
- **First choice:** Mem0, if you want a lightweight memory layer focused on recall and simple integration.
- **Second choice:** Supermemory, if you later need a broader context platform with connectors and richer memory infrastructure.

### Practical Rule for This Project
If a fact changes the build, the content model, the routing, the importer, or the deployment flow, it belongs in the repo docs or code, not in memory.

## Build Rules
Local build script should remain simple.
Typical build flow:
- build Tailwind CSS
- run Hugo build
- run Pagefind index generation if needed
- deploy to Cloudflare Pages

Do not add unnecessary build steps.

## File / Folder Guidance
Preferred folders:
- `layouts/` for templates and partials
- `assets/` for source CSS and other build assets
- `static/` for final static assets only
- `content/` for Hugo content
- `scripts/` or `importer.py` for content automation

Avoid storing generated content in places that make the repo hard to understand.

## Code Style Rules
- Prefer small, readable files over large abstractions
- Use clear naming
- Prefer explicit templates and partials
- Keep logic in importer scripts or Hugo templates, not hidden in complex client-side JS
- Minimize dependencies
- Remove dead code rather than keeping it “just in case”

## What to Prioritize When Working on the Repo
If you are unsure what to do next, prioritize in this order:
1. Chapter pages render correctly as HTML
2. SEO metadata is correct on every page
3. Importer reliably creates content files
4. Search works with Pagefind
5. Comments work with Giscus
6. Reading progress works locally
7. Ads are inserted cleanly
8. Analytics and Search Console are configured

## What Not to Do
- Do not reintroduce SPA chapter routing
- Do not add a database unless there is a proven need
- Do not add SSR infrastructure unless the site outgrows static hosting
- Do not build a complex microservice architecture
- Do not optimize for hypothetical scale before the site has traffic
- Do not introduce new frameworks just because they are modern

## Decision Rule
When in doubt, choose the solution that:
- is easiest to maintain alone
- keeps chapter URLs indexable
- supports ads well
- keeps deploys cheap
- can be understood again after a few weeks away from the code

## Recommended Workflow for Future Changes
For any new feature or refactor:
1. Audit the current repo state.
2. Identify what is already working.
3. Make the smallest safe change.
4. Verify build output.
5. Verify chapter pages and SEO.
6. Only then add the next feature.

## Daily Coding Workflow for AI Assistance
When asked to help with code, follow this order:
1. Read the relevant files first.
2. Summarize the current state in plain language.
3. Identify risks and likely side effects.
4. Propose the smallest change that solves the problem.
5. Only then edit the code.
6. After editing, explain exactly what changed.
7. If a change touches routing, content structure, or build flow, check the impact on SEO and deploy output.

## Safe Change Rules
- Prefer one focused change per task.
- Do not refactor unrelated files unless necessary.
- Do not replace a working system with a “better” one just because it is newer.
- Do not add new dependencies unless they clearly reduce complexity or solve a real problem.
- Preserve existing content and configuration unless the task explicitly requires changing them.
- If a change affects chapter URLs, Hugo templates, or build output, treat it as high risk.

## Refactor Order
When refactoring, use this order:
1. Templates and content model
2. Importer logic
3. Build scripts
4. Styling
5. Optional enhancements

This order keeps the publishing flow stable while the design evolves.

## Feature Addition Order
If unsure what to build next, use this order:
1. Chapter pages render correctly
2. Novel pages render correctly
3. SEO metadata is complete
4. Search works
5. Comments work
6. Reading progress works locally
7. Ads are placed cleanly
8. Analytics are configured
9. Only then consider extra features

## Mission Statement
Bacanovel should become:
- easy to publish to
- easy to search
- easy to read
- easy to monetize
- easy to maintain

It should **not** become a fragile overengineered platform.


Always use Context7 when I need library/API documentation, code generation, setup or configuration steps without me having to explicitly ask.






# AI CODING OPERATING PROCEDURE

## General Rule

Before making any code change:

1. Read relevant files first.
2. Explain the current implementation.
3. Explain the problem.
4. Explain the proposed solution.
5. Identify risks.
6. Only then modify files.

Never skip analysis and jump directly into implementation.

### Exception for Minor Changes
Jika perubahan bersifat minor (hanya memperbaiki typo teks, mengubah warna/spacing Tailwind, atau perbaikan kosmetik yang tidak menyentuh logic, routing, importer, maupun struktur konten), Langkah 1-3 boleh dilewati. AI cukup memberikan penjelasan singkat tentang apa yang diubah secara langsung.

---

# Project Context

This project is Bacanovel.

Primary goal:

Traffic
→ SEO
→ Ads
→ Revenue

Not:

Framework experimentation.

When making decisions:

SEO > Convenience

Simplicity > Cleverness

Shipping > Perfection

---

# Required Output Format

When working on a task:

## Step 1

Current State

Explain:

* How the current system works
* Files involved
* Dependencies involved

---

## Step 2

Problem Analysis

Explain:

* Root cause
* Risks
* Alternative solutions

---

## Step 3

Implementation Plan

List:

* Files to modify
* Files to create
* Files to delete

---

## Step 4

Code Changes

Only after steps 1-3 are complete.

---

## Step 5

Verification

Explain:

* Build impact
* SEO impact
* Deploy impact

---

# Hugo Rules

Always prefer:

* Hugo native features
* Hugo templates
* Hugo content model

Avoid:

* Complex client-side rendering
* SPA architecture
* JavaScript-heavy solutions

Unless explicitly required.

---

# SEO Rules

Every chapter page must have:

* Unique URL
* Unique title
* Canonical URL
* Meta description

Any change that weakens SEO must be flagged.

---

# Importer Rules

Importer is a critical system.

Before changing importer:

Explain:

* Current workflow
* New workflow
* Migration risks

Never change content structure casually.

---

# Dependency Rules

Before adding a dependency:

Explain:

1. Why it is needed.
2. Existing alternatives.
3. Long-term maintenance cost.

Default answer should be:

Do not add dependency.

Unless justified.

---

# Refactor Rules

Do not refactor unrelated code.

Bad:

Task:
Fix chapter navigation.

Result:
20 files changed.

Good:

Task:
Fix chapter navigation.

Result:
2 files changed.

---

# Architecture Rules

Do not introduce:

* Astro
* Next.js
* SSR
* Databases
* Search servers
* Microservices

Unless explicitly requested.

Current architecture:

Hugo
+
Cloudflare Pages
+
Pagefind
+
Giscus
+
localStorage

---

# When Unsure

Ask:

"Do you prefer the simpler solution or the more scalable solution?"

Default to:

Simpler solution.

---

# Emergency Rule

If a proposed change:

* Alters chapter URLs
* Alters content structure
* Alters importer output
* Alters deployment process

Treat it as HIGH RISK.

Require explanation before implementation.

