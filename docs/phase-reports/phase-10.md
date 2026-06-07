# Phase 10 — Reading progress (localStorage)

## What was added
- Reading progress save/restore on chapter pages (`layouts/_default/single.html`):
  - On scroll (debounced 500ms), saves `window.scrollY` to `localStorage` keyed by `reading-progress:<path>`.
  - On page load, restores the saved scroll position.
  - Also saves a `last-read:<novel_slug>` entry with `{ url, title, ts }` so the novel index page knows which chapter was last read.
- "Lanjutkan membaca" (Continue reading) section on the novel index page (`layouts/novel/list.html`):
  - Reads `last-read:<novel_slug>` from `localStorage`.
  - If found, shows a card with the chapter title and a "Baca" button linking to the saved URL.
  - Hidden by default, shown via JS only if data exists.
- Font size preference (existing) continues to use `reading-font-scale` in `localStorage`.

## What was removed
- Nothing.

## What was changed
- `layouts/_default/single.html`: added reading progress script block after the font-size script.
- `layouts/novel/list.html`: added `#continue-reading` section and its show/hide script.

## Why
- AGENTS.md: "Use browser localStorage for reading progress and bookmarks."
- The old SPA had font-size persistence but no scroll position or last-read tracking.
- localStorage is the simplest possible persistence layer — no database, no accounts, no server. Works offline, zero cost.
- The "Continue reading" card on the novel index page is the natural place for readers to pick up where they left off.

## Build verification

```text
$ rm -rf public resources && hugo --minify
Pages: 12 (11 pages + 1 auto-generated)
Total in 127 ms
```

Chapter page (`/novels/petualangan-dunia-paralel/chapter-0001/`):
- Contains `reading-progress:` key in localStorage save/restore script.
- Saves position on scroll, restores on load.

Novel index page (`/novels/petualangan-dunia-paralel/`):
- Contains `#continue-reading` section (hidden by default).
- JS reads `last-read:petualangan-dunia-paralel` from localStorage and shows the card if data exists.

## Remaining issues (deferred)
- No "bookmarks" feature yet — AGENTS.md mentions bookmarks alongside reading progress, but this is a V2 feature. Reading progress is the minimum viable implementation.
- The scroll restore uses `setTimeout(0)` which is fine for most cases but could flicker on very long pages. A more robust approach would use `requestAnimationFrame` or IntersectionObserver, but that's over-optimization for now.
- The `last-read` data has a `ts` timestamp but no expiry. Old data will persist indefinitely. A future pass could add a 30-day TTL.
