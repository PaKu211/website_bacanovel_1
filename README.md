# Bacanovel

Light-novel reading website built with Hugo, Tailwind CSS, and static-first architecture.

## Stack

- **Hugo Extended** — static site generator
- **Tailwind CSS v4** — utility-first CSS (via CLI, not Hugo Pipes)
- **Pagefind** — static client-side search
- **Giscus** — comments via GitHub Discussions
- **localStorage** — reading progress and bookmarks (no backend)
- **Cloudflare Pages** — hosting (zero cost)

## Quick start

```bash
npm install
npm run build
```

This runs:
1. `build:css` — Tailwind CLI compiles `assets/css/main.css` → `static/css/main.css`
2. `hugo --minify` — Hugo builds HTML pages to `public/`
3. `build:index` — Pagefind indexes the built HTML for search

For development:

```bash
npm run dev
```

Runs Tailwind in watch mode and Hugo dev server concurrently.

## Content structure

```
content/
└── novels/
    └── <novel-slug>/
        ├── _index.md          # Novel metadata (title, author, cover, genres, summary)
        ├── chapter-0001.md    # Chapter with full front matter
        ├── chapter-0002.md
        └── ...
```

### Novel `_index.md`

```yaml
---
title: "Novel Title"
slug: "novel-slug"
type: "novel"
author: "Author Name"
status: "ongoing"
genres:
  - Fantasy
  - Action
cover: "/images/covers/novel-slug.jpg"
summary: "Short description of the novel."
date: 2026-06-01T06:00:00+07:00
draft: false
---
```

### Chapter front matter

```yaml
---
title: "Bab 1: Chapter Title"
slug: "chapter-0001"
novel_slug: "novel-slug"
novel_title: "Novel Title"
chapter_number: 1
weight: 1
date: 2026-06-01T06:00:00+07:00
draft: false
---
```

## URL structure

| Page | URL |
|---|---|
| Homepage | `/` |
| Novel index | `/novels/<slug>/` |
| Chapter | `/novels/<slug>/chapter-0001/` |

Every chapter is a real HTML page with a unique URL. No hash routing, no SPA.

## Importer

The importer reads lncrawl-style output and generates Hugo content files.

### Batch import

```bash
python3 importer.py /path/to/lncrawl-output/
```

Expected folder structure:
```
/path/to/lncrawl-output/
├── meta.json       # Novel metadata
├── cover.jpg       # Cover image
├── 001/            # Volume number
│   ├── 1.json      # Chapter JSON
│   └── 2.json
└── 002/
    └── 1.json
```

### Single chapter import

```bash
echo "Chapter text content" | python3 importer.py --novel-slug "Novel Title" --chapter 1 --title "Bab 1"
```

### Importer flags

| Flag | Description |
|---|---|
| `--novel-slug` | Novel slug (required for single import) |
| `--chapter` | Chapter number (auto-detected if omitted) |
| `--title` | Chapter title (default: "Bab N") |
| `--rate` | Delay between writes in seconds (default: 0.1) |
| `--force` | Overwrite existing files |

## Configuration

### `hugo.toml`

```toml
baseURL = "/"
languageCode = "id-id"
title = "Novel Reading"
buildFuture = true

[params]
  description = "Site description for SEO."

  [params.giscus]
    repo = "owner/repo"
    repoId = "REPLACE_ME"
    category = "Announcements"
    categoryId = "REPLACE_ME"

[outputs]
  home = ["HTML", "JSON"]
  page = ["HTML"]
  section = ["HTML"]

[markup.goldmark.renderer]
  unsafe = true
```

### Giscus setup

1. Create a public GitHub repo
2. Enable GitHub Discussions with an "Announcements" category
3. Install the Giscus app: https://github.com/apps/giscus
4. Get IDs from https://giscus.app
5. Fill in `[params.giscus]` in `hugo.toml`

## Features

| Feature | Implementation |
|---|---|
| SEO | Unique URLs, canonical, OG/Twitter meta, auto-descriptions |
| Search | Pagefind (static, client-side) |
| Comments | Giscus (GitHub Discussions) |
| Dark mode | Tailwind `dark:` classes + localStorage toggle |
| Font size | Adjustable 90%-140%, saved in localStorage |
| Reading progress | Scroll position saved per chapter, "Continue reading" on novel page |
| Ads | Modular `ad-slot.html` partial (top/middle/bottom) |
| Analytics | Cloudflare Web Analytics (hardcoded beacon in `baseof.html`) |

## Deployment (Cloudflare Pages)

1. Push to GitHub
2. Connect repo in Cloudflare Pages
3. Build settings:
   - Build command: `npm install && npm run build`
   - Build output directory: `public`
   - Node.js version: 18+ (in compatibility flags)
4. Set custom domain in Cloudflare Pages dashboard

## Project structure

```
├── archetypes/           # Hugo archetypes (chapter.md, novel.md)
├── assets/css/main.css   # Tailwind entrypoint + custom components
├── content/novels/       # Novel and chapter markdown files
├── layouts/
│   ├── _default/         # baseof.html, list.html, single.html
│   ├── index.html        # Homepage (novel listing)
│   ├── novel/            # Novel section layout (list.html)
│   └── partials/         # ad-slot, chapter-nav, giscus, head, search, etc.
├── static/images/covers/ # Cover images
├── docs/phase-reports/   # Migration phase reports
├── importer.py           # Content importer
├── hugo.toml             # Hugo configuration
├── tailwind.config.js    # Tailwind theme config
└── package.json          # Build scripts and dependencies
```

## Phase reports

Migration history is documented in `docs/phase-reports/`:

- `phase-01.md` — Per-chapter HTML output, Tailwind v4 upgrade
- `phase-02.md` — Full SEO meta tags
- `phase-03.md` — Content structure migration
- `phase-04.md` — Importer rewrite
- `phase-05-06.md` — SPA removal + static homepage
- `phase-08.md` — Giscus comments
- `phase-09.md` — Pagefind search
- `phase-10.md` — Reading progress
- `phase-11.md` — Repo hygiene
