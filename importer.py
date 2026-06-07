#!/usr/bin/env python3
"""
Bacanovel importer — reads lncrawl-style output or raw text and generates
Hugo Markdown files with full front matter.

Two modes:
  Batch:    python importer.py <target_folder>
            Reads meta.json + volume folders (lncrawl output format).
  Single:   python importer.py --novel-slug <slug> --chapter <N> [--title "..."] < input.txt
            Reads from stdin or a text file argument.

Output: content/novels/<slug>/chapter-NNNN.md
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone, timedelta

HUGO_ROOT = None
SUPPORTED_EXTENSIONS = (".txt", ".md")

WITA = timezone(timedelta(hours=8))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text):
    """Lowercase, strip non-alphanumeric, collapse dashes."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\-]", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def escape_yaml_string(text):
    """Escape a string for safe inclusion in double-quoted YAML values."""
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "")
    return text


def sanitize_body(text):
    """Strip residual HTML tags and normalize whitespace to clean markdown."""
    if not text:
        return ""
    # Remove HTML tags but keep their text content
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<p[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    # Decode common HTML entities
    text = text.replace("&ldquo;", "\u201c").replace("&rdquo;", "\u201d")
    text = text.replace("&lsquo;", "\u2018").replace("&rsquo;", "\u2019")
    text = text.replace("&mdash;", "\u2014").replace("&ndash;", "\u2013")
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    # Collapse whitespace: multiple newlines → double, tabs → spaces
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text


def now_iso():
    """Return current time in ISO 8601 with WITA offset."""
    return datetime.now(WITA).strftime("%Y-%m-%dT%H:%M:%S+08:00")


def chapter_filename(idx):
    """Return chapter filename: chapter-0001.md"""
    return f"chapter-{idx:04d}.md"


def find_hugo_root():
    """Walk up to find hugo.toml or hugo.yaml."""
    global HUGO_ROOT
    if HUGO_ROOT is not None:
        return HUGO_ROOT
    d = os.getcwd()
    while True:
        if os.path.isfile(os.path.join(d, "hugo.toml")) or os.path.isfile(os.path.join(d, "hugo.yaml")):
            HUGO_ROOT = d
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    # Fallback to cwd
    HUGO_ROOT = os.getcwd()
    return HUGO_ROOT


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def safe_path(base, target):
    """Ensure target is within base directory (prevent path traversal)."""
    real_base = os.path.realpath(base)
    real_target = os.path.realpath(target)
    if not real_target.startswith(real_base + os.sep) and real_target != real_base:
        raise ValueError(f"Path traversal detected: {target} escapes {base}")
    return real_target


# ---------------------------------------------------------------------------
# Chapter file writer (shared by batch and single import)
# ---------------------------------------------------------------------------

def write_chapter_file(file_path, title, chapter_num, novel_slug, novel_title, body):
    """Write a single chapter Markdown file with full front matter."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f'title: "{escape_yaml_string(title)}"\n')
        f.write(f'slug: "chapter-{chapter_num:04d}"\n')
        f.write(f'novel_slug: "{escape_yaml_string(novel_slug)}"\n')
        f.write(f'novel_title: "{escape_yaml_string(novel_title)}"\n')
        f.write(f"chapter_number: {chapter_num}\n")
        f.write(f"weight: {chapter_num}\n")
        f.write(f"date: {now_iso()}\n")
        f.write("draft: false\n")
        f.write("---\n")
        f.write(f"\n{body}\n")


# ---------------------------------------------------------------------------
# Novel index (_index.md)
# ---------------------------------------------------------------------------

def write_novel_index(novel_dir, meta_data, novel_title, novel_slug, chapter_count, rate=0):
    """Write or update the novel's _index.md with full front matter."""
    index_path = os.path.join(novel_dir, "_index.md")

    # If _index.md already exists, only overwrite if it's bare-bones (just title)
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            existing = f.read()
        if "type:" in existing or "author:" in existing:
            print(f"  _index.md already has full metadata, skipping write.")
            return

    author = meta_data.get("author", "").strip()
    status = meta_data.get("status", "ongoing").strip()
    genres = meta_data.get("genres", [])
    summary = meta_data.get("synopsis", meta_data.get("summary", "")).strip()
    cover_rel = f"/images/covers/{novel_slug}.jpg"

    with open(index_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f'title: "{escape_yaml_string(novel_title)}"\n')
        f.write(f'slug: "{escape_yaml_string(novel_slug)}"\n')
        f.write('type: "novel"\n')
        if author:
            f.write(f'author: "{escape_yaml_string(author)}"\n')
        f.write(f'status: "{escape_yaml_string(status)}"\n')
        if genres:
            f.write("genres:\n")
            for g in genres:
                f.write(f"  - {escape_yaml_string(g)}\n")
        f.write(f'cover: "{cover_rel}"\n')
        if summary:
            f.write(f'summary: "{escape_yaml_string(summary)}"\n')
        f.write(f'date: {now_iso()}\n')
        f.write("draft: false\n")
        f.write("---\n")
        f.write(f"\n{summary or novel_title}\n")

    print(f"  -> _index.md written: {novel_title}")


# ---------------------------------------------------------------------------
# Cover image
# ---------------------------------------------------------------------------

def copy_cover(target_folder, novel_slug):
    """Copy cover.jpg into static/images/covers/<slug>.jpg if it exists."""
    cover_src = os.path.join(target_folder, "cover.jpg")
    if not os.path.exists(cover_src):
        # Try common alternatives
        for alt in ("cover.jpeg", "cover.png", "cover.webp"):
            alt_path = os.path.join(target_folder, alt)
            if os.path.exists(alt_path):
                cover_src = alt_path
                break
        else:
            return False

    static_base = os.path.join(find_hugo_root(), "static")
    dest_dir = os.path.join(static_base, "images", "covers")
    ensure_dir(dest_dir)
    dest = os.path.join(dest_dir, f"{novel_slug}.jpg")
    safe_path(static_base, dest)
    shutil.copy2(cover_src, dest)
    print(f"  -> cover copied: static/images/covers/{novel_slug}.jpg")
    return True


# ---------------------------------------------------------------------------
# Batch import (lncrawl-style folders)
# ---------------------------------------------------------------------------

def import_split_novel(target_folder, rate=0.1, force=False):
    """
    Batch-import a novel from an lncrawl-style output folder.

    Expected structure:
      <target_folder>/
        meta.json           (title, author, status, genres, synopsis)
        cover.jpg           (optional cover image)
        001/                (volume number)
          1.json            (chapter number)
          2.json
        002/
          1.json
          ...
    """
    if not os.path.exists(target_folder):
        print(f"Error: Folder {target_folder} tidak ditemukan!")
        return False

    meta_path = os.path.join(target_folder, "meta.json")
    if not os.path.exists(meta_path):
        print(f"Error: Tidak menemukan meta.json di dalam {target_folder}!")
        return False

    print(f"Membaca metadata dari {meta_path}...")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)

    novel_title = meta_data.get("title", "Novel Tanpa Judul").strip()
    novel_slug = slugify(novel_title)

    hugo_root = find_hugo_root()
    content_base = os.path.join(hugo_root, "content")
    novel_dir = os.path.join(content_base, "novels", novel_slug)
    safe_path(content_base, novel_dir)
    ensure_dir(novel_dir)

    # 1. Write novel _index.md
    print(f"[1/4] Menulis _index.md...")
    write_novel_index(novel_dir, meta_data, novel_title, novel_slug, 0)

    # 2. Copy cover
    print(f"[2/4] Menyalin cover...")
    copy_cover(target_folder, novel_slug)

    # 3. Discover chapters
    print(f"[3/4] Menemukan bab...")
    volumes = [
        d for d in os.listdir(target_folder)
        if os.path.isdir(os.path.join(target_folder, d)) and d.isdigit()
    ]
    volumes.sort(key=int)

    chapters = []
    for vol in volumes:
        vol_dir = os.path.join(target_folder, vol)
        ch_files = [f for f in os.listdir(vol_dir) if f.endswith(".json")]
        ch_files.sort(key=lambda f: int(re.findall(r"\d+", f)[0]) if re.findall(r"\d+", f) else 0)
        for ch_file in ch_files:
            chapters.append((vol, ch_file))

    print(f"  Ditemukan {len(chapters)} bab dari {len(volumes)} volume.")

    # 4. Write chapters
    print(f"[4/4] Menulis chapter markdown...")
    written = 0
    skipped = 0

    for idx, (vol, ch_file) in enumerate(chapters, start=1):
        ch_path = os.path.join(target_folder, vol, ch_file)
        with open(ch_path, "r", encoding="utf-8") as f:
            ch_data = json.load(f)

        ch_title = ch_data.get("title", f"Bab {idx}").strip()
        ch_body = sanitize_body(ch_data.get("body", ch_data.get("content", "")))

        ch_filename = chapter_filename(idx)
        ch_file_path = os.path.join(novel_dir, ch_filename)

        # Duplicate detection
        if os.path.exists(ch_file_path) and not force:
            skipped += 1
            continue

        write_chapter_file(ch_file_path, ch_title, idx, novel_slug, novel_title, ch_body)

        written += 1
        if rate > 0:
            time.sleep(rate)

    print(f"\nSelesai! {written} bab ditulis, {skipped} dilewati (sudah ada).")
    return True


# ---------------------------------------------------------------------------
# Single chapter import (CLI / stdin)
# ---------------------------------------------------------------------------

def import_single_chapter(args):
    """Import a single chapter from a text file or stdin."""
    hugo_root = find_hugo_root()

    if not args.novel_slug:
        print("Error: --novel-slug wajib diisi.")
        return False

    novel_slug = slugify(args.novel_slug)
    content_base = os.path.join(hugo_root, "content")
    novel_dir = os.path.join(content_base, "novels", novel_slug)
    safe_path(content_base, novel_dir)
    ensure_dir(novel_dir)

    # Read content
    if args.input and args.input != "-":
        with open(args.input, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = sys.stdin.read()

    content = sanitize_body(content)

    # Determine chapter number
    chapter_num = args.chapter
    if not chapter_num:
        # Auto-detect from existing files
        existing = [
            f for f in os.listdir(novel_dir)
            if f.startswith("chapter-") and f.endswith(".md")
        ]
        chapter_num = len(existing) + 1

    title = args.title or f"Bab {chapter_num}"
    ch_filename = chapter_filename(chapter_num)
    ch_file_path = os.path.join(novel_dir, ch_filename)

    if os.path.exists(ch_file_path) and not args.force:
        print(f"Error: {ch_filename} sudah ada. Gunakan --force untuk menimpa.")
        return False

    write_chapter_file(ch_file_path, title, chapter_num, novel_slug, args.novel_slug, content)

    print(f"Berhasil: {novel_dir}/{ch_filename}")
    return True


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Bacanovel importer — generate Hugo Markdown from novel text."
    )
    parser.add_argument("input", nargs="?", help="Path to text file or folder (use - for stdin)")
    parser.add_argument("--novel-slug", help="Novel slug (for single-chapter import)")
    parser.add_argument("--chapter", type=int, help="Chapter number (default: auto-detect)")
    parser.add_argument("--title", help="Chapter title")
    parser.add_argument("--rate", type=float, default=0.1, help="Delay between writes in seconds (default: 0.1)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(1)

    # Batch mode: if input is a directory
    if os.path.isdir(args.input):
        import_split_novel(args.input, rate=args.rate, force=args.force)
    else:
        import_single_chapter(args)


if __name__ == "__main__":
    main()
