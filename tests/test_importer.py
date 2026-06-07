"""Unit tests for importer.py — the Bacanovel content importer."""

import argparse
import json
import os
import shutil
import sys
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importer


class TestSlugify(unittest.TestCase):
    """Tests for the slugify() helper."""

    def test_basic_lowercase(self):
        self.assertEqual(importer.slugify("Hello World"), "hello-world")

    def test_special_characters_replaced(self):
        self.assertEqual(importer.slugify("Hello, World!"), "hello-world")

    def test_multiple_dashes_collapsed(self):
        self.assertEqual(importer.slugify("a---b"), "a-b")

    def test_leading_trailing_dashes_stripped(self):
        self.assertEqual(importer.slugify("--hello--"), "hello")

    def test_numbers_preserved(self):
        self.assertEqual(importer.slugify("Chapter 123"), "chapter-123")

    def test_empty_string(self):
        self.assertEqual(importer.slugify(""), "")

    def test_unicode_characters_replaced(self):
        self.assertEqual(importer.slugify("café résumé"), "caf-r-sum")

    def test_already_slug(self):
        self.assertEqual(importer.slugify("already-a-slug"), "already-a-slug")

    def test_mixed_case_and_symbols(self):
        self.assertEqual(importer.slugify("The King's Reign (Vol. 2)"), "the-king-s-reign-vol-2")


class TestSanitizeBody(unittest.TestCase):
    """Tests for the sanitize_body() helper."""

    def test_empty_string(self):
        self.assertEqual(importer.sanitize_body(""), "")

    def test_none_input(self):
        self.assertEqual(importer.sanitize_body(None), "")

    def test_plain_text_unchanged(self):
        self.assertEqual(importer.sanitize_body("Hello world"), "Hello world")

    def test_br_tags_converted_to_newlines(self):
        result = importer.sanitize_body("Line1<br>Line2<br/>Line3<BR />Line4")
        self.assertIn("Line1\nLine2", result)
        self.assertIn("Line3\nLine4", result)

    def test_p_tags_converted_to_newlines(self):
        result = importer.sanitize_body("<p>Paragraph 1</p><p>Paragraph 2</p>")
        self.assertIn("Paragraph 1", result)
        self.assertIn("Paragraph 2", result)

    def test_html_tags_stripped(self):
        result = importer.sanitize_body("<div><strong>Bold</strong> text</div>")
        self.assertEqual(result, "Bold text")

    def test_html_entities_decoded(self):
        text = "&ldquo;Hello&rdquo; &mdash; &amp; &lt;tag&gt; &nbsp; &quot;ok&quot;"
        result = importer.sanitize_body(text)
        self.assertIn("\u201c", result)  # left double quote
        self.assertIn("\u201d", result)  # right double quote
        self.assertIn("\u2014", result)  # em dash
        self.assertIn("&", result)
        self.assertIn("<tag>", result)
        self.assertIn('"ok"', result)

    def test_single_quote_entities(self):
        result = importer.sanitize_body("&lsquo;hi&rsquo;")
        self.assertIn("\u2018", result)
        self.assertIn("\u2019", result)

    def test_ndash_entity(self):
        result = importer.sanitize_body("1&ndash;10")
        self.assertIn("\u2013", result)

    def test_multiple_newlines_collapsed(self):
        result = importer.sanitize_body("Line1\n\n\n\n\nLine2")
        self.assertEqual(result, "Line1\n\nLine2")

    def test_tabs_replaced_with_spaces(self):
        result = importer.sanitize_body("Hello\tworld")
        self.assertNotIn("\t", result)
        self.assertIn("Hello world", result)

    def test_whitespace_stripped(self):
        result = importer.sanitize_body("  \n  Hello  \n  ")
        self.assertEqual(result, "Hello")


class TestNowIso(unittest.TestCase):
    """Tests for the now_iso() helper."""

    def test_format_has_wita_offset(self):
        result = importer.now_iso()
        self.assertTrue(result.endswith("+08:00"))

    def test_format_is_iso8601(self):
        result = importer.now_iso()
        # Should match YYYY-MM-DDTHH:MM:SS+08:00
        import re
        self.assertRegex(result, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00")


class TestChapterFilename(unittest.TestCase):
    """Tests for the chapter_filename() helper."""

    def test_single_digit(self):
        self.assertEqual(importer.chapter_filename(1), "chapter-0001.md")

    def test_double_digit(self):
        self.assertEqual(importer.chapter_filename(42), "chapter-0042.md")

    def test_triple_digit(self):
        self.assertEqual(importer.chapter_filename(100), "chapter-0100.md")

    def test_four_digit(self):
        self.assertEqual(importer.chapter_filename(9999), "chapter-9999.md")

    def test_five_digit(self):
        self.assertEqual(importer.chapter_filename(10000), "chapter-10000.md")


class TestFindHugoRoot(unittest.TestCase):
    """Tests for the find_hugo_root() helper."""

    def setUp(self):
        """Reset the global HUGO_ROOT cache before each test."""
        importer.HUGO_ROOT = None

    def test_finds_hugo_toml_in_cwd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            toml_path = os.path.join(tmpdir, "hugo.toml")
            with open(toml_path, "w") as f:
                f.write("")
            with patch("os.getcwd", return_value=tmpdir):
                result = importer.find_hugo_root()
            self.assertEqual(result, tmpdir)

    def test_finds_hugo_yaml_in_parent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = os.path.join(tmpdir, "hugo.yaml")
            with open(yaml_path, "w") as f:
                f.write("")
            child = os.path.join(tmpdir, "subdir")
            os.makedirs(child)
            with patch("os.getcwd", return_value=child):
                importer.HUGO_ROOT = None
                result = importer.find_hugo_root()
            self.assertEqual(result, tmpdir)

    def test_fallback_to_cwd_when_no_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("os.getcwd", return_value=tmpdir):
                importer.HUGO_ROOT = None
                result = importer.find_hugo_root()
            self.assertEqual(result, tmpdir)

    def test_caches_result(self):
        importer.HUGO_ROOT = "/cached/path"
        result = importer.find_hugo_root()
        self.assertEqual(result, "/cached/path")

    def tearDown(self):
        importer.HUGO_ROOT = None


class TestEnsureDir(unittest.TestCase):
    """Tests for the ensure_dir() helper."""

    def test_creates_nested_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "a", "b", "c")
            importer.ensure_dir(nested)
            self.assertTrue(os.path.isdir(nested))

    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "x")
            importer.ensure_dir(nested)
            importer.ensure_dir(nested)  # no error
            self.assertTrue(os.path.isdir(nested))


class TestWriteNovelIndex(unittest.TestCase):
    """Tests for write_novel_index()."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_writes_full_front_matter(self):
        meta = {
            "author": "Test Author",
            "status": "ongoing",
            "genres": ["Fantasy", "Action"],
            "synopsis": "A great novel.",
        }
        importer.write_novel_index(self.tmpdir, meta, "Test Novel", "test-novel", 10)

        index_path = os.path.join(self.tmpdir, "_index.md")
        self.assertTrue(os.path.exists(index_path))

        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('title: "Test Novel"', content)
        self.assertIn('slug: "test-novel"', content)
        self.assertIn('type: "novel"', content)
        self.assertIn('author: "Test Author"', content)
        self.assertIn('status: "ongoing"', content)
        self.assertIn("- Fantasy", content)
        self.assertIn("- Action", content)
        self.assertIn('cover: "/images/covers/test-novel.jpg"', content)
        self.assertIn('summary: "A great novel."', content)
        self.assertIn("draft: false", content)

    def test_skips_when_full_metadata_exists(self):
        index_path = os.path.join(self.tmpdir, "_index.md")
        original = '---\ntitle: "Existing"\ntype: "novel"\nauthor: "Someone"\n---\n'
        with open(index_path, "w") as f:
            f.write(original)

        importer.write_novel_index(self.tmpdir, {}, "New Title", "new-title", 0)

        with open(index_path, "r") as f:
            content = f.read()
        self.assertEqual(content, original)

    def test_overwrites_bare_index(self):
        index_path = os.path.join(self.tmpdir, "_index.md")
        with open(index_path, "w") as f:
            f.write('---\ntitle: "Bare"\n---\n')

        meta = {"author": "Author", "status": "completed", "genres": [], "synopsis": "Desc"}
        importer.write_novel_index(self.tmpdir, meta, "Bare", "bare", 0)

        with open(index_path, "r") as f:
            content = f.read()
        self.assertIn('author: "Author"', content)

    def test_handles_missing_optional_fields(self):
        meta = {}
        importer.write_novel_index(self.tmpdir, meta, "Minimal", "minimal", 0)

        index_path = os.path.join(self.tmpdir, "_index.md")
        with open(index_path, "r") as f:
            content = f.read()
        self.assertIn('title: "Minimal"', content)
        self.assertNotIn("author:", content)
        self.assertNotIn("genres:", content)

    def test_summary_field_from_summary_key(self):
        meta = {"summary": "From summary key."}
        importer.write_novel_index(self.tmpdir, meta, "Novel", "novel", 0)

        index_path = os.path.join(self.tmpdir, "_index.md")
        with open(index_path, "r") as f:
            content = f.read()
        self.assertIn('summary: "From summary key."', content)


class TestCopyCover(unittest.TestCase):
    """Tests for copy_cover()."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.tmpdir, "source")
        self.hugo_root = os.path.join(self.tmpdir, "hugo")
        os.makedirs(self.source_dir)
        os.makedirs(self.hugo_root)
        # Create hugo.toml so find_hugo_root works
        with open(os.path.join(self.hugo_root, "hugo.toml"), "w") as f:
            f.write("")
        importer.HUGO_ROOT = self.hugo_root

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        importer.HUGO_ROOT = None

    def test_copies_cover_jpg(self):
        cover = os.path.join(self.source_dir, "cover.jpg")
        with open(cover, "wb") as f:
            f.write(b"\xff\xd8cover-data")

        result = importer.copy_cover(self.source_dir, "test-novel")
        self.assertTrue(result)

        dest = os.path.join(self.hugo_root, "static", "images", "covers", "test-novel.jpg")
        self.assertTrue(os.path.exists(dest))

    def test_tries_alternative_extensions(self):
        cover = os.path.join(self.source_dir, "cover.png")
        with open(cover, "wb") as f:
            f.write(b"png-data")

        result = importer.copy_cover(self.source_dir, "test-novel")
        self.assertTrue(result)

    def test_returns_false_when_no_cover(self):
        result = importer.copy_cover(self.source_dir, "test-novel")
        self.assertFalse(result)


class TestImportSplitNovel(unittest.TestCase):
    """Tests for import_split_novel() — batch import from lncrawl folders."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.tmpdir, "novel-source")
        self.hugo_root = os.path.join(self.tmpdir, "hugo")
        os.makedirs(self.source_dir)
        os.makedirs(self.hugo_root)
        with open(os.path.join(self.hugo_root, "hugo.toml"), "w") as f:
            f.write("")
        importer.HUGO_ROOT = self.hugo_root

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        importer.HUGO_ROOT = None

    def _write_meta(self, title="Test Novel", **extra):
        meta = {"title": title, "author": "Author", "status": "ongoing", "genres": ["Fantasy"], "synopsis": "A test."}
        meta.update(extra)
        with open(os.path.join(self.source_dir, "meta.json"), "w") as f:
            json.dump(meta, f)

    def _write_chapter(self, volume, chapter_num, title="Chapter", body="Content"):
        vol_dir = os.path.join(self.source_dir, f"{volume:03d}")
        os.makedirs(vol_dir, exist_ok=True)
        ch_data = {"title": title, "body": body}
        with open(os.path.join(vol_dir, f"{chapter_num}.json"), "w") as f:
            json.dump(ch_data, f)

    def test_returns_false_for_missing_folder(self):
        result = importer.import_split_novel("/nonexistent/path")
        self.assertFalse(result)

    def test_returns_false_for_missing_meta(self):
        result = importer.import_split_novel(self.source_dir)
        self.assertFalse(result)

    def test_imports_chapters_successfully(self):
        self._write_meta()
        self._write_chapter(1, 1, title="Bab 1", body="Chapter 1 content")
        self._write_chapter(1, 2, title="Bab 2", body="Chapter 2 content")

        result = importer.import_split_novel(self.source_dir, rate=0)
        self.assertTrue(result)

        novel_dir = os.path.join(self.hugo_root, "content", "novels", "test-novel")
        self.assertTrue(os.path.exists(os.path.join(novel_dir, "chapter-0001.md")))
        self.assertTrue(os.path.exists(os.path.join(novel_dir, "chapter-0002.md")))
        self.assertTrue(os.path.exists(os.path.join(novel_dir, "_index.md")))

    def test_chapter_front_matter_is_correct(self):
        self._write_meta()
        self._write_chapter(1, 1, title="Bab 1", body="Body text")

        importer.import_split_novel(self.source_dir, rate=0)

        ch_path = os.path.join(self.hugo_root, "content", "novels", "test-novel", "chapter-0001.md")
        with open(ch_path, "r") as f:
            content = f.read()

        self.assertIn('title: "Bab 1"', content)
        self.assertIn('slug: "chapter-0001"', content)
        self.assertIn('novel_slug: "test-novel"', content)
        self.assertIn('novel_title: "Test Novel"', content)
        self.assertIn("chapter_number: 1", content)
        self.assertIn("weight: 1", content)
        self.assertIn("draft: false", content)
        self.assertIn("Body text", content)

    def test_skips_existing_chapters_without_force(self):
        self._write_meta()
        self._write_chapter(1, 1, title="Bab 1", body="Original")

        importer.import_split_novel(self.source_dir, rate=0)

        # Modify the chapter source
        self._write_chapter(1, 1, title="Bab 1", body="Updated")

        # Import again without force
        importer.import_split_novel(self.source_dir, rate=0)

        ch_path = os.path.join(self.hugo_root, "content", "novels", "test-novel", "chapter-0001.md")
        with open(ch_path, "r") as f:
            content = f.read()
        self.assertIn("Original", content)
        self.assertNotIn("Updated", content)

    def test_overwrites_with_force(self):
        self._write_meta()
        self._write_chapter(1, 1, title="Bab 1", body="Original")

        importer.import_split_novel(self.source_dir, rate=0)

        self._write_chapter(1, 1, title="Bab 1", body="Updated")
        importer.import_split_novel(self.source_dir, rate=0, force=True)

        ch_path = os.path.join(self.hugo_root, "content", "novels", "test-novel", "chapter-0001.md")
        with open(ch_path, "r") as f:
            content = f.read()
        self.assertIn("Updated", content)

    def test_multi_volume_ordering(self):
        self._write_meta()
        self._write_chapter(1, 1, title="Vol1Ch1", body="v1c1")
        self._write_chapter(2, 1, title="Vol2Ch1", body="v2c1")

        importer.import_split_novel(self.source_dir, rate=0)

        novel_dir = os.path.join(self.hugo_root, "content", "novels", "test-novel")
        # chapter-0001.md should be from vol 1, chapter-0002.md from vol 2
        with open(os.path.join(novel_dir, "chapter-0001.md"), "r") as f:
            self.assertIn("v1c1", f.read())
        with open(os.path.join(novel_dir, "chapter-0002.md"), "r") as f:
            self.assertIn("v2c1", f.read())


class TestImportSingleChapter(unittest.TestCase):
    """Tests for import_single_chapter()."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.hugo_root = os.path.join(self.tmpdir, "hugo")
        os.makedirs(self.hugo_root)
        with open(os.path.join(self.hugo_root, "hugo.toml"), "w") as f:
            f.write("")
        importer.HUGO_ROOT = self.hugo_root

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        importer.HUGO_ROOT = None

    def _make_args(self, novel_slug=None, chapter=None, title=None, force=False, input_path=None):
        return argparse.Namespace(
            novel_slug=novel_slug,
            chapter=chapter,
            title=title,
            force=force,
            input=input_path,
        )

    def test_returns_false_without_novel_slug(self):
        args = self._make_args(novel_slug=None, chapter=1, input_path="-")
        result = importer.import_single_chapter(args)
        self.assertFalse(result)

    def test_imports_from_file(self):
        # Create a text file
        txt_path = os.path.join(self.tmpdir, "chapter.txt")
        with open(txt_path, "w") as f:
            f.write("Chapter content here.")

        args = self._make_args(
            novel_slug="my-novel",
            chapter=1,
            title="Bab 1: Intro",
            input_path=txt_path,
        )
        result = importer.import_single_chapter(args)
        self.assertTrue(result)

        ch_path = os.path.join(self.hugo_root, "content", "novels", "my-novel", "chapter-0001.md")
        self.assertTrue(os.path.exists(ch_path))

        with open(ch_path, "r") as f:
            content = f.read()
        self.assertIn('title: "Bab 1: Intro"', content)
        self.assertIn('novel_slug: "my-novel"', content)
        self.assertIn("Chapter content here.", content)

    def test_imports_from_stdin(self):
        args = self._make_args(novel_slug="my-novel", chapter=2, input_path="-")
        with patch("sys.stdin", StringIO("Stdin content")):
            result = importer.import_single_chapter(args)
        self.assertTrue(result)

        ch_path = os.path.join(self.hugo_root, "content", "novels", "my-novel", "chapter-0002.md")
        with open(ch_path, "r") as f:
            content = f.read()
        self.assertIn("Stdin content", content)

    def test_auto_detects_chapter_number(self):
        novel_dir = os.path.join(self.hugo_root, "content", "novels", "my-novel")
        os.makedirs(novel_dir)
        # Pre-create two chapters
        for i in [1, 2]:
            with open(os.path.join(novel_dir, f"chapter-{i:04d}.md"), "w") as f:
                f.write("existing")

        txt_path = os.path.join(self.tmpdir, "chapter.txt")
        with open(txt_path, "w") as f:
            f.write("New chapter")

        args = self._make_args(novel_slug="my-novel", chapter=None, input_path=txt_path)
        result = importer.import_single_chapter(args)
        self.assertTrue(result)

        # Auto-detected chapter number should be 3
        ch_path = os.path.join(novel_dir, "chapter-0003.md")
        self.assertTrue(os.path.exists(ch_path))

    def test_refuses_overwrite_without_force(self):
        novel_dir = os.path.join(self.hugo_root, "content", "novels", "my-novel")
        os.makedirs(novel_dir)
        with open(os.path.join(novel_dir, "chapter-0001.md"), "w") as f:
            f.write("existing content")

        txt_path = os.path.join(self.tmpdir, "chapter.txt")
        with open(txt_path, "w") as f:
            f.write("New content")

        args = self._make_args(novel_slug="my-novel", chapter=1, input_path=txt_path)
        result = importer.import_single_chapter(args)
        self.assertFalse(result)

    def test_overwrites_with_force(self):
        novel_dir = os.path.join(self.hugo_root, "content", "novels", "my-novel")
        os.makedirs(novel_dir)
        with open(os.path.join(novel_dir, "chapter-0001.md"), "w") as f:
            f.write("old content")

        txt_path = os.path.join(self.tmpdir, "chapter.txt")
        with open(txt_path, "w") as f:
            f.write("new content")

        args = self._make_args(novel_slug="my-novel", chapter=1, force=True, input_path=txt_path)
        result = importer.import_single_chapter(args)
        self.assertTrue(result)

        with open(os.path.join(novel_dir, "chapter-0001.md"), "r") as f:
            content = f.read()
        self.assertIn("new content", content)

    def test_default_title_when_not_specified(self):
        txt_path = os.path.join(self.tmpdir, "chapter.txt")
        with open(txt_path, "w") as f:
            f.write("content")

        args = self._make_args(novel_slug="my-novel", chapter=5, title=None, input_path=txt_path)
        importer.import_single_chapter(args)

        ch_path = os.path.join(self.hugo_root, "content", "novels", "my-novel", "chapter-0005.md")
        with open(ch_path, "r") as f:
            content = f.read()
        self.assertIn('title: "Bab 5"', content)

    def test_content_is_sanitized(self):
        txt_path = os.path.join(self.tmpdir, "chapter.txt")
        with open(txt_path, "w") as f:
            f.write("<p>Hello</p><br><strong>World</strong>&amp;More")

        args = self._make_args(novel_slug="my-novel", chapter=1, input_path=txt_path)
        importer.import_single_chapter(args)

        ch_path = os.path.join(self.hugo_root, "content", "novels", "my-novel", "chapter-0001.md")
        with open(ch_path, "r") as f:
            content = f.read()
        # HTML tags should be stripped
        self.assertNotIn("<p>", content)
        self.assertNotIn("<strong>", content)
        self.assertIn("Hello", content)
        self.assertIn("World", content)
        self.assertIn("&More", content)


class TestMainCLI(unittest.TestCase):
    """Tests for the main() CLI entrypoint."""

    def test_no_args_prints_help_and_exits(self):
        with patch("sys.argv", ["importer.py"]):
            with self.assertRaises(SystemExit) as cm:
                importer.main()
            self.assertEqual(cm.exception.code, 1)

    def test_batch_mode_dispatches_to_import_split_novel(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("sys.argv", ["importer.py", tmpdir]):
                with patch("importer.import_split_novel") as mock_fn:
                    importer.main()
                    mock_fn.assert_called_once_with(tmpdir, rate=0.1, force=False)

    def test_single_mode_dispatches_to_import_single_chapter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            txt = os.path.join(tmpdir, "ch.txt")
            with open(txt, "w") as f:
                f.write("text")
            with patch("sys.argv", ["importer.py", txt, "--novel-slug", "test"]):
                with patch("importer.import_single_chapter") as mock_fn:
                    importer.main()
                    mock_fn.assert_called_once()
                    args = mock_fn.call_args[0][0]
                    self.assertEqual(args.novel_slug, "test")


if __name__ == "__main__":
    unittest.main()
