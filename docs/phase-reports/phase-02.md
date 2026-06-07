# Phase 2 — Full SEO meta tags

## What was added
- Per-page `description`: derived from `Params.summary` → `Params.description` → auto-extracted from `.Content` (plainified and truncated to 160 chars). Whitespace, newlines, and HTML entities are normalized so the resulting `content` attribute is a single clean line.
- `canonical` URL: emitted from `.Permalink` on every page.
- `robots` meta: `index, follow` on all pages.
- `theme-color` meta: `#0f172a` (Tailwind slate-900) for mobile browser chrome.
- Open Graph: `og:site_name`, `og:title`, `og:description`, `og:url`, `og:type` (article on pages, website on nodes), `og:locale` (`id_ID` to match the site's audience), `og:image` (when `.Params.cover` or `.Params.image` is set).
- Twitter card: `summary_large_image` with title, description, and image.

## What was removed
- Nothing.

## What was changed
- `layouts/partials/head.html`: rewritten from a 1-line stylesheet link to a full SEO partial. The inline dark-mode detection script is preserved unchanged.

## Why
- AGENTS.md SEO rules: "Every chapter page must have: Unique URL, Unique title, Canonical URL, Meta description." Pre-Phase 2 had no description, no canonical, and no social-share metadata.
- Social previews (WhatsApp, Telegram, Twitter, Discord, Slack) all read Open Graph tags. Without `og:title`/`og:description`/`og:image`, shared chapter links render as bare URLs and produce no clicks.
- `og:type=article` on chapter pages is what Facebook and LinkedIn use to decide whether to render the "Article" preview card.
- Auto-derived descriptions are a deliberate SEO trade-off: a hand-written front-matter `summary` will always win; the fallback extraction guarantees no chapter is ever shipped without *some* description.

## Build verification

```text
$ rm -rf public resources && hugo --minify
Pages: 11
Total in 74 ms
```

Sample output (chapter page):
```html
<title>Bab 1: Terbangun di Hutan Misterius - Petualangan Dunia Paralel</title>
<meta name="description" content="Ketika aku membuka mata, suara burung asing menggema di antara dedaunan yang belum pernah kulihat sebelumnya. Matahari pagi menyaring cahayanya melalui kanopi …">
<link rel="canonical" href="/petualangan-dunia-paralel/chapter-1/">
<meta name="robots" content="index, follow">
<meta property="og:site_name" content="Novel Reading">
<meta property="og:title" content="Bab 1: Terbangun di Hutan Misterius | Novel Reading">
<meta property="og:description" content="Ketika aku membuka mata, suara burung asing …">
<meta property="og:url" content="/petualangan-dunia-paralel/chapter-1/">
<meta property="og:type" content="article">
<meta property="og:locale" content="id_ID">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Bab 1: Terbangun di Hutan Misterius | Novel Reading">
<meta name="twitter:description" content="Ketika aku membuka mata, suara burung asing …">
```

Sample output (novel index page):
```html
<title>Petualangan Dunia Paralel | Novel Reading</title>
<meta name="description" content="Selamat datang di kumpulan bab Petualangan Dunia Paralel. …">
<meta property="og:type" content="website">
```

## Remaining issues (deferred)
- Homepage description is empty because the homepage currently renders the SPA shell with no body content. Will be fixed in Phase 6 when the homepage is rebuilt as a real novel list.
- `og:image` is not emitted yet because no novel has a `.Params.cover`. Will be wired up in Phase 3 when novel metadata is added.
- Twitter handle is not set (no `twitter:site`/`twitter:creator`). Will be added when the site gets a Twitter identity, or left as-is for now.
