# Phase 12 — README update

## What was added
- Complete rewrite of `README.md` covering: project overview, stack, quick start, content structure, URL structure, importer usage (batch + single chapter), configuration, Giscus setup, feature table, Cloudflare Pages deployment, project structure, and links to all phase reports.

## What was removed
- The old README (155 lines) which documented the SPA-era architecture, referenced non-existent CLI flags for the importer, and described Hugo Pipes CSS pipeline that no longer exists.

## What was changed
- `README.md`: complete rewrite.

## Why
- The old README was written for the SPA architecture. It documented `hugo server -D` as the dev workflow, referenced `resources.Get | css.TailwindCSS` in head.html, described the importer with flags that didn't exist in the code, and mentioned Cusdis for comments. All of this was outdated after the 12-phase migration.
- A correct README is critical for: onboarding new contributors, Cloudflare Pages build configuration, and personal reference after time away from the code.

## Final state

```
Tracked files: 20
HTML pages: 8 (homepage, novels index, novel page, 3 chapters, categories, tags)
Build: Tailwind v4.3.0 → Hugo → Pagefind (when installed)
```

## Summary of all phases

| Phase | Status | What |
|---|---|---|
| 1 | ✅ | Per-chapter HTML output, Tailwind v4 upgrade |
| 2 | ✅ | Full SEO meta tags (description, canonical, OG, Twitter) |
| 3 | ✅ | Content structure → `content/novels/<slug>/chapter-0001.md` |
| 4 | ✅ | Importer rewrite (batch + single, full front matter, sanitization) |
| 5+6 | ✅ | SPA shell removed, static homepage with novel listing |
| 7 | ✅ | Novel index page (cover, metadata, chapter list) |
| 8 | ✅ | Giscus comments (replaces Cusdis) |
| 9 | ✅ | Pagefind search integration |
| 10 | ✅ | Reading progress (localStorage scroll + last-read) |
| 11 | ✅ | Repo hygiene (untrack node_modules, lncrawl-data, public/) |
| 12 | ✅ | README rewrite |

All phases complete. The site is SEO-first, Hugo-first, static-first, and ready for Cloudflare Pages deployment.
