---
name: testing-bacanovel
description: Test Bacanovel site end-to-end — importer CLI, browser JS, and Hugo build. Use when verifying importer changes, template JS changes, or general site health.
---

# Testing Bacanovel

## Prerequisites

- Hugo Extended (v0.110+ required for `hugo.toml` config format)
- Node.js + npm (for Tailwind CSS and Pagefind)
- Python 3 (for importer and unit tests)
- pytest (`pip install pytest`)

## Setup

### Install Dependencies
```bash
npm install
pip install pytest
```

### Build the Site
```bash
npm run build
```
This runs: Tailwind CSS build → Hugo build → Pagefind index generation.

The built site goes to `public/`.

### Serve Locally

The apt-installed Hugo (v0.92) does NOT support `hugo.toml` — you need Hugo Extended v0.110+.

If Hugo Extended is available:
```bash
hugo server -D --bind 0.0.0.0 --port 1313
```

If Hugo server has issues, serve the pre-built `public/` directory:
```bash
cd public && python3 -m http.server 1313 --bind 0.0.0.0
```
Note: This serves static files only — no live reload.

## Unit Tests

```bash
python3 -m pytest tests/test_importer.py -x --tb=short
```
Expected: All tests pass. These cover `slugify()`, `sanitize_body()`, `now_iso()`, `chapter_filename()`, `find_hugo_root()`, and more.

## Importer CLI Testing

The importer (`importer.py`) has two modes:
1. **Batch mode**: `python3 importer.py <directory>` — imports from lncrawl split format
2. **Single chapter mode**: `python3 importer.py --novel-slug <slug> --chapter <num> <file>`

### Test: Malformed meta.json
```bash
TMPDIR=$(mktemp -d)
echo '{bad json' > "$TMPDIR/meta.json"
mkdir "$TMPDIR/001"
python3 importer.py "$TMPDIR"; echo "EXIT=$?"
```
Expected: Error message containing `meta.json tidak valid`, exit code 1, no traceback.

### Test: Bad chapter JSON skipped
```bash
TMPDIR=$(mktemp -d)
echo '{"title":"Test","author":"A","status":"ongoing","genres":["F"],"synopsis":"S"}' > "$TMPDIR/meta.json"
mkdir "$TMPDIR/001"
echo '{"title":"Ch1","body":"Good."}' > "$TMPDIR/001/1.json"
echo '{bad' > "$TMPDIR/001/2.json"
python3 importer.py "$TMPDIR"; echo "EXIT=$?"
```
Expected: `Warning: Skipping` for bad file, good chapter written, exit code 0.

### Test: Missing input file
```bash
python3 importer.py --novel-slug test --chapter 1 /nonexistent/file.txt; echo "EXIT=$?"
```
Expected: `Error: File /nonexistent/file.txt tidak ditemukan.`, exit code 1.

## Browser JS Testing

Requires site served on localhost. Open browser to `http://localhost:1313/`.

### Test: Corrupt localStorage cleanup (novel page)
1. Navigate to a novel page (e.g., `/novels/petualangan-dunia-paralel/`)
2. In console: `localStorage.setItem('last-read:petualangan-dunia-paralel', '{bad json')`
3. Reload the page
4. Check console for `Failed to parse reading progress:` warning
5. Verify: `localStorage.getItem('last-read:petualangan-dunia-paralel')` returns `null`

### Test: NaN font scale fallback (chapter page)
1. On any page, in console: `localStorage.setItem('reading-font-scale', 'garbage')`
2. Navigate to a chapter page (e.g., `/novels/petualangan-dunia-paralel/chapter-0001/`)
3. Verify: `document.getElementById('reading-area').style.fontSize` equals `'100%'`
4. Verify: `localStorage.getItem('reading-font-scale')` now equals `'100'`

### Test: Search error handling
1. If `/_pagefind/pagefind.js` is unavailable (404 or missing directory)
2. Click the search input on the homepage
3. Verify: Page shows `Pencarian belum tersedia.` text below the search bar
4. Verify: Console shows `Pagefind not available:` warning (not an unhandled error)

## Known Issues

- The Pagefind search index might be at `pagefind/` instead of `_pagefind/` depending on the Pagefind version and config. The search template imports from `/_pagefind/pagefind.js`. If search always shows "Pencarian belum tersedia.", check if the index directory name matches.
- Hugo v0.92 (apt default on Ubuntu 22.04) does not support `hugo.toml` config. You need Hugo Extended v0.110+ from the Hugo GitHub releases or snap.
- Giscus comments require the repo to have the Giscus app installed — console errors about giscus are expected in local testing.

## Devin Secrets Needed

No secrets required for local testing. All tests run against localhost with no external auth.
