# Phase 3 — Content structure migration

## What was added
- New content tree at `content/novels/<slug>/` with the AGENTS.md-mandated layout:
  - `_index.md` (novel metadata)
  - `chapter-0001.md`, `chapter-0002.md`, ... (4-digit zero-padded)
- Full novel front matter on `content/novels/petualangan-dunia-paralel/_index.md`:
  - `title`, `slug`, `type: "novel"`, `author`, `status`, `genres` (list), `cover`, `summary`, `date`, `draft`.
- Full chapter front matter on each chapter:
  - `title`, `slug`, `novel_slug`, `novel_title`, `chapter_number`, `weight`, `date`, `draft`.
- `weight: N` on each chapter file so Hugo's section listing, prev/next, and sitemap are sorted by reading order.
- `archetypes/novel.md` — Hugo archetype for new novel roots with all required fields.
- `archetypes/chapter.md` — updated to emit `novel_slug`, `novel_title`, `chapter_number`, and `weight` automatically.
- Cover image: `static/images/covers/petualangan-dunia-paralel.jpg` (the existing stock placeholder was reused; the orphan from the old `rookie-talent-agent-knows-it-all` slug was retained for now and queued for Phase 11 cleanup).
- `layouts/novel/list.html` — Hugo section template that renders a novel index page (cover, author, status, genre chips, summary, and a chapter list). Wired via the `type: "novel"` front-matter field, which is the idiomatic Hugo way to assign a layout to a section.

## What was removed
- Old content tree `content/petualangan-dunia-paralel/` (3 files + `_index.md`). Files were moved with `git mv` so history is preserved.
- Hard-coded author/synopsis in `layouts/partials/novel-card.html` (the partial is unused on real pages, queued for removal in Phase 5).

## What was changed
- `archetypes/chapter.md`: added `slug`, `novel_slug`, `novel_title`, `chapter_number`, `weight`.
- `layouts/partials/chapter-nav.html`: rewritten to compute prev/next by `chapter_number` rather than by Hugo's default date-desc ordering. The previous implementation produced a reversed order because all three chapters share the same `date`. The new template: respects `Params.previous_chapter` / `Params.next_chapter` overrides, otherwise sorts `CurrentSection.RegularPages` by `chapter_number` ASC and picks the neighbors by index.
- `layouts/index.html` and `static/js/app.js` — still present but will be removed in Phase 5; not modified here.

## Why
- AGENTS.md prescribes the exact path scheme: `content/novels/<slug>/chapter-0001.md`. The previous `content/petualangan-dunia-paralel/chapter-1.md` violated this on three points (parent folder name, singular vs plural, file padding).
- Per AGENTS.md, novel `_index.md` must have `title`, `slug`, `author`, `status`, `genres`, `cover`, `summary`. The pre-Phase-3 file had only `title`. Adding the rest lets the novel index page render a real cover, author byline, status badge, and genre chips.
- `weight: N` makes the sort order explicit and removes a hidden dependency on file creation order or `date` value.
- `type: "novel"` in front matter is the idiomatic Hugo way to bind a custom section template (`layouts/novel/list.html`). It is more robust than `layout:` in front matter, which only works for single pages.
- Chapter nav fix: the previous `PrevInSection`/`NextInSection` produced a reversed list because Hugo's default `.RegularPages` order is `date DESC`. Computing the prev/next explicitly from `chapter_number` is the only way to get stable, deterministic navigation across chapters regardless of `date` values.

## Build verification

```text
$ rm -rf public resources && hugo --minify
Pages: 12
Total in 65 ms
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

Chapter URLs match AGENTS.md exactly: `/novels/petualangan-dunia-paralel/chapter-0001/`.

Chapter nav (verified):
- chapter-0001 → no prev, next → chapter-0002
- chapter-0002 → prev → chapter-0001, next → chapter-0003
- chapter-0003 → prev → chapter-0002, no next

Novel index page renders cover, "Novel • Ongoing" eyebrow, author, status, genre chips (Fantasy / Action / Isekai), summary, and three chapter cards.

## Remaining issues (deferred)
- The `static/images/rookie-talent-agent-knows-it-all.jpg` orphan is still on disk and was copied to `static/images/covers/petualangan-dunia-paralel.jpg` as a stand-in cover. Will be removed in Phase 11.
- The `layouts/partials/novel-card.html` partial is now redundant (the novel index is rendered by `layouts/novel/list.html`). Will be removed in Phase 5/11.
- The auto-generated `public/novels/index.html` (the parent of the `novels` section) currently shows the `petualangan-dunia-paralel` novel as a generic page card. Will be replaced with a real homepage in Phase 6.
