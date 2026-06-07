# Phase 5 — Remove SPA shell + Phase 6 — Static homepage

## What was added
- `layouts/index.html` — new SEO-first static homepage. Renders a grid of novel cards from `content/novels/`. Each card shows: cover image, title, status badge, author, summary (2-line clamp), genre chips, chapter count, and a "Baca Novel" button. No JavaScript, no hash routing, no `fetch('/index.json')`.
- `hugo.toml`: added `[params]` section with `description` (site-level meta description for the homepage and any page that lacks its own).

## What was removed
- `layouts/index.html` (old SPA shell) — the entire `homepage-view` / `reading-view` toggle, `#chapter-content`, `#novel-list`, `#font-size-indicator`, `#cusdis_thread` SPA container, and the `<script src="/js/app.js" defer>` tag. This was the original entry point that rendered a full single-page application with hash-based routing for novel browsing and chapter reading.
- `layouts/index.json` — the JSON feed (`{{- range .Site.RegularPages | jsonify }}`) that fed the SPA's `fetch('/index.json')`. No longer needed because chapters are now real HTML pages with unique URLs.
- `static/js/app.js` — the `SPARouter` class (163 lines): `renderNovelKatalog()`, `renderDaftarBab()`, `handleRoute()`, `setupNavigationButtons()`, `reloadComments()`, `changeFontSize()`. All of these are now either replaced by Hugo templates (chapter listing, novel listing) or by the chapter page's inline script (font size).
- `layouts/partials/novel-card.html` — the old SPA-era partial with hardcoded "Petualangan Dunia Paralel" / "Oleh: Penulis Hebat" / "Fantasy • Action • Isekai" text. The new homepage renders novel data dynamically from front matter.

## What was changed
- `layouts/partials/head.html`: description logic refined — the homepage now uses `.Site.Params.description` (from `[params]` in `hugo.toml`) instead of trying to auto-extract from `.Content` (which is the SPA shell with no body text). Chapter pages continue to auto-extract from their rendered content. `.Site.Description` was attempted but doesn't exist in Hugo 0.162.1; `.Site.Params.description` is the correct path.

## Why
- AGENTS.md: "Do not reintroduce SPA chapter routing", "Avoid SPA hash routing for chapter reading", "One chapter = one unique URL", "Each chapter must be a real Hugo page rendered to HTML." The SPA shell violated all of these by serving chapters as `#/read/<slug>` hashes, with content fetched at runtime from `index.json`. Search engines cannot index `#/read/...` URLs.
- AGENTS.md: "Homepage: novel list, latest updates, search entry point." The new homepage is a real HTML page listing all novels — exactly what the brief describes.
- SPA removal also eliminates the Cusdis comment container in `index.html` (the `#cusdis_thread` div with `data-app-id="9e4028b0-..."`) which was a hardcoded SPA-only integration point. Giscus replaces it in Phase 8.

## Build verification

```text
$ rm -rf public resources && hugo --minify
Pages: 11
Total in 56 ms
```

HTML output:
```text
public/categories/index.html
public/index.html
public/novels/index.html
public/novels/petualangan-dunia-paralel/chapter-0001/index.html
public/novels/petualangan-dunia-paralel/chapter-0002/index.html
public/novels/petualangan-dunia-paralel/chapter-0003/index.html
public/novels/petualangan-dunia-paralel/index.html
public/tags/index.html
```

Homepage:
- Title: "Novel Reading - Baca Novel Online"
- Description: "Baca novel online gratis. Koleksi novel terbaru, bab baru setiap hari."
- No `app.js` reference, no hash routing, no SPA containers.
- Novel card renders with cover, title, "Ongoing" status badge, author, summary, genre chips, chapter count, "Baca Novel" link.

Chapter page (unchanged from Phase 2):
- Title: "Bab 1: Terbangun di Hutan Misterius - Petualangan Dunia Paralel"
- Description auto-extracted from content.
- og:type = article.

## Remaining issues (deferred)
- `public/novels/index.html` still renders as a generic section listing (the parent of the novels section). Can be replaced with a redirect to `/` or a duplicate novel list in Phase 7.
- The orphan `static/js/` directory was removed along with `app.js`. No other JS files remain.
- The Cloudflare beacon script in `baseof.html` is still hardcoded. Will be addressed in Phase 11.
