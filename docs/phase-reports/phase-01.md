# Phase 1 — Per-chapter HTML output

## What was added
- `outputs.page = ["HTML"]` in `hugo.toml` so every chapter renders to a real HTML page.
- `outputs.section = ["HTML"]` so novel index pages (chapter listings) render to HTML.
- `outputs.home = ["HTML", "JSON"]` retained so the homepage has both a server-rendered HTML shell and the JSON feed used by the (then-still-existing) SPA fallback.
- Plain `<link rel="stylesheet" href="/css/main.css">` in `layouts/partials/head.html` — replaced the previous Hugo Pipes `resources.Get | css.TailwindCSS | minify | fingerprint` chain. The compiled v4 output is served from `static/css/main.css` directly. This decouples CSS from the Hugo version's `css.TailwindCSS` support and makes Cloudflare Pages deploys deterministic.
- Tailwind v4.3.0 (`tailwindcss` + `@tailwindcss/cli`) added as devDependencies. The v3 `tailwindcss@^3.4.19` and the separate `dependencies` block were collapsed.
- `assets/css/main.css` switched from v3 directives (`@tailwind base; @tailwind components; @tailwind utilities;`) to v4 syntax: `@import "tailwindcss";` + `@config "../../tailwind.config.js";`. The `@config` directive keeps the existing `tailwind.config.js` (`content`, `darkMode: 'class'`, `theme.extend`) in play, so no template or config refactor was needed.

## What was removed
- The Hugo Pipes pipeline (`css.TailwindCSS | minify | fingerprint`) from `head.html`. The fingerprint/integrity attribute is gone (accepted trade — keeps the build deterministic and the URL stable).
- `@tailwindcss/cli` as a runtime `dependency` (was a v3-era habit). It's now a `devDependency` alongside the engine.

## What was changed
- `hugo.toml`: outputs flipped.
- `layouts/partials/head.html`: Hugo Pipes replaced with a plain `<link>`.
- `assets/css/main.css`: v3 → v4 syntax.
- `package.json`: deps reshuffled.
- `package-lock.json`: regenerated against `tailwindcss@4.3.0` + `@tailwindcss/cli@4.3.0`.

## Why
- AGENTS.md non-negotiable: "One chapter = one unique URL" and "Each chapter must be a real Hugo page rendered to HTML." The pre-Phase 1 site had only the SPA homepage and JSON feed — chapter pages were never real HTML, which broke SEO and made the site invisible to crawlers.
- Hugo Pipes + `css.TailwindCSS` only works on Hugo versions that bundle the standalone Tailwind executable. Tailwind v4 ships a different package layout, so the v3 Hugo Pipes invocation would silently fail on future Hugo upgrades. Moving to a plain `<link>` removes that risk.
- v4.3.0 is the latest stable Tailwind. Staying on v3.4 would have required either keeping deprecated dependencies or doing the migration later under worse conditions.

## Build verification

```text
$ rm -f static/css/main.css && npm run build:css
≈ tailwindcss v4.3.0
Done in 481ms

$ rm -rf public resources && npm run build
Pages: 11
Static files: 3
Total in 77 ms
```

HTML files emitted:
```text
public/categories/index.html
public/index.html
public/petualangan-dunia-paralel/chapter-1/index.html
public/petualangan-dunia-paralel/chapter-2/index.html
public/petualangan-dunia-paralel/chapter-3/index.html
public/petualangan-dunia-paralel/index.html
public/tags/index.html
```

Sitemap includes all three chapter URLs with `lastmod`. CSS link is present on every page.

## Remaining issues (deferred)
- Content path is `content/petualangan-dunia-paralel/`, not `content/novels/<slug>/` as AGENTS.md prescribes. Fixed in Phase 3.
- Chapter file naming is `chapter-1.md`, not `chapter-0001.md`. Fixed in Phase 3.
- SPA shell (`layouts/index.html`, `layouts/index.json`, `static/js/app.js`) is still present and served as a fallback. Removed in Phase 5.
- Homepage is the SPA shell, not a list of novels. Rebuilt in Phase 6.
- Comments still use Cusdis with a placeholder appID. Replaced with Giscus in Phase 8.
- Tailwind v4 emits a one-time deprecation warning for `@config` — accepted; the cleaner CSS-first config is a Phase 4+ (or later) cleanup.
