# Phase 8 — Replace Cusdis with Giscus

## What was added
- `layouts/partials/giscus.html` — new partial that renders the Giscus comments widget. Reads `data-repo`, `data-repo-id`, `data-category`, `data-category-id` from `hugo.toml` `[params.giscus]`. Uses `pathname` mapping so each chapter URL maps to a unique GitHub Discussion. Language set to `id` (Indonesian). Theme and input position are configurable.
- `[params.giscus]` section in `hugo.toml` with placeholder values (`repo = "owner/bacanovel-site"`, `repoId = "REPLACE_ME"`, `category = "Announcements"`, `categoryId = "REPLACE_ME"`).

## What was removed
- `layouts/partials/cusdis.html` — the old Cusdis comments partial (28 lines). No longer referenced from any template.

## What was changed
- `layouts/_default/single.html`: the comment section now calls `partial "giscus.html"` instead of `partial "cusdis.html"`. The dict passes `repo`, `repoId`, `category`, `categoryId` from site params, plus `mapping: "pathname"` and `lang: "id"`.
- `hugo.toml`: added `[params.giscus]` block.

## Why
- AGENTS.md: "Use Giscus if comments are needed. Do not build a custom comment backend unless there is a strong later reason."
- The old Cusdis integration had a hardcoded placeholder `appID: "your-cusdis-app-id"` in `single.html`. Cusdis is a hosted service with a free tier; Giscus is backed by GitHub Discussions, which is more familiar to developers and has no external dependency beyond GitHub.
- `pathname` mapping is the correct choice for Bacanovel because every chapter has a unique, stable URL (`/novels/<slug>/chapter-NNNN/`). Giscus will create one Discussion per chapter URL automatically.
- The config is centralized in `hugo.toml` so the deployer only needs to fill in `repoId` and `categoryId` once; every chapter page inherits the values.

## Build verification

```text
$ rm -rf public resources && hugo --minify
Pages: 11
Total in 67 ms
```

Chapter page includes:
```html
<div class="giscus mt-10"></div>
<script>
  s.src = 'https://giscus.app/client.js';
  s.setAttribute('data-repo', 'owner/bacanovel-site');
  s.setAttribute('data-repo-id', 'REPLACE_ME');
  s.setAttribute('data-category', 'Announcements');
  s.setAttribute('data-category-id', 'REPLACE_ME');
  s.setAttribute('data-mapping', 'pathname');
  s.setAttribute('data-lang', 'id');
</script>
```

No Cusdis references remain anywhere in the build output.

## Setup required before deploy
1. Create a public GitHub repo for the site (e.g., `bacanovel-site`).
2. Enable GitHub Discussions on the repo, create an "Announcements" category.
3. Install the Giscus app on the repo: https://github.com/apps/giscus.
4. Visit https://giscus.app to get `data-repo-id` and `data-category-id`.
5. Replace `REPLACE_ME` in `hugo.toml` `[params.giscus]` with the real IDs.

## Remaining issues (deferred)
- The Giscus widget loads with `data-theme="light"`. For dark mode, the theme should switch to `dark` when the user toggles dark mode. This requires a small script to call `giscus.setTheme()` on theme change. Can be wired into the existing `theme-toggle-script.html` partial in a future pass.
- The `data-input-position="bottom"` is a good default for reading flows (comment box below the text). Can be changed later if needed.
