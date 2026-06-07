# Phase 9 — Pagefind search integration

## What was added
- `layouts/partials/search.html` — Pagefind-powered search bar. Renders an input with a magnifying glass icon, debounced search (200ms), and a results dropdown showing up to 8 hits with title + content preview. Pagefind JS is loaded lazily on first input focus via dynamic `import('/_pagefind/pagefind.js')`. Gracefully falls back to "Pencarian belum tersedia." if Pagefind index is not built.
- Search bar added to homepage (`layouts/index.html`) between the site header and the novel grid.
- `build:index` script in `package.json`: `npx pagefind --site public` — runs after Hugo build to index all HTML files.
- `build` script updated: `npm run build:css && hugo --minify && npm run build:index`.
- `pagefind` added to `devDependencies` in `package.json` (version `^1.3.0`).

## What was removed
- Nothing.

## What was changed
- `package.json`: added `pagefind` dep, added `build:index` script, updated `build` script chain.

## Why
- AGENTS.md: "Use Pagefind. Do not introduce an external search server. Search should remain static and client-side."
- Pagefind is the standard static search tool for Hugo/JAMstack sites. It runs at build time to create a search index, then the client-side JS does fuzzy matching. No server, no API keys, no external service.
- The 200ms debounce and lazy loading ensure search doesn't impact page load performance.
- The `pathname` mapping means every chapter page gets its own search result entry — consistent with the SEO-first approach.

## Build verification

```text
$ rm -rf public resources && hugo --minify
Pages: 11
Total in 79 ms
```

Homepage includes:
- `<input id="search-input" placeholder="Cari novel atau bab..." aria-label="Cari novel atau bab">`
- `<div id="search-results" class="hidden">` container
- Inline script that loads Pagefind on focus, debounces input, renders hit cards

The Pagefind index (`/_pagefind/`) is NOT generated yet because `pagefind` npm package is not installed (network timeout). After `npm install`, running `npm run build:index` will create the index.

## Setup required
1. `npm install` (installs pagefind along with other deps)
2. `npm run build` (builds CSS, Hugo HTML, then Pagefind index)
3. The search bar will automatically work — no configuration needed

## Remaining issues (deferred)
- Pagefind not installed due to network timeout during this session. The `package.json` is configured and will work once `npm install` succeeds.
- The search results don't show novel/chapter metadata (just title + content excerpt). Could be improved by adding `data-pagefind-meta` attributes to templates in a future pass.
- No dedicated `/search` page — the search bar is embedded on the homepage only. Could be added as a standalone page later if needed.
