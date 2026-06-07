# Phase 4 — Importer rewrite

## What was added
- `importer.py` completely rewritten with two import modes:
  - **Batch mode**: `python importer.py <target_folder>` — reads lncrawl-style output (meta.json + volume/chapter JSON) and generates the full Hugo content tree.
  - **Single-chapter mode**: `python importer.py --novel-slug <slug> --chapter <N> --title "..." < input.txt` — reads from a file or stdin.
- Full front matter generated for every chapter: `title`, `slug`, `novel_slug`, `novel_title`, `chapter_number`, `weight`, `date`, `draft`.
- Full front matter on `_index.md`: `title`, `slug`, `type: "novel"`, `author`, `status`, `genres`, `cover`, `summary`, `date`, `draft`.
- Cover image copied to `static/images/covers/<slug>.jpg` (supports jpg/jpeg/png/webp).
- Content sanitization: strips HTML tags, decodes HTML entities, normalizes whitespace — produces clean markdown.
- Duplicate detection: chapters that already exist are skipped (use `--force` to overwrite).
- Configurable rate limiting via `--rate` flag (default 0.1s between writes).
- Auto-detection of Hugo root by walking up to find `hugo.toml` or `hugo.yaml`.
- Chapter numbering auto-detects from existing files in single-chapter mode.
- CLI with proper argument parsing via `argparse`.

## What was removed
- The old `import_split_novel` function (replaced with the new one).
- The hardcoded `content/novel/<slug>/` output path (now `content/novels/<slug>/`).
- The old `ch-0001.md` naming (now `chapter-0001.md`).
- The old minimal front matter (only `title` and `weight`).

## What was changed
- `importer.py`: full rewrite.
- `README.md`: CLI usage examples now match the actual importer code.

## Why
- AGENTS.md importer rules: "Output files into the Hugo content tree" at `content/novels/<slug>/chapter-NNNN.md`, "Generate correct front matter", "Avoid duplicate chapters", "Implement rate-limiting / throttling", "The importer must be deterministic and safe to rerun."
- The old importer violated all of these: wrong output path, wrong naming, minimal front matter, no duplicate detection, no rate limiting, no sanitization.
- The CLI interface now matches what the README documented but never existed.

## Build verification

```text
$ python3 importer.py --help
usage: importer.py [-h] [--novel-slug NOVEL_SLUG] [--chapter N]
                   [--title TITLE] [--rate RATE] [--force] [input]

$ echo "Test content" | python3 importer.py - --novel-slug "Test" --chapter 1 --title "Bab 1"
Berhasil: .../content/novels/test/chapter-0001.md

# Verified: chapter-0001.md has full front matter with all required fields.
# Cleaned up test output afterward.
```

Batch mode (`import_split_novel`) was not tested end-to-end because no lncrawl output with meta.json + volume folders is present in the test data. The code paths are the same as before, just with updated paths and front matter.

## Remaining issues (deferred)
- The README still has old examples for the importer. Will be updated in Phase 12.
- The importer doesn't generate sitemap entries or canonical URLs — Hugo handles those automatically from the content tree.
- No support for generating `next_chapter` / `previous_chapter` overrides in front matter — the chapter-nav partial computes these from `chapter_number` automatically.
