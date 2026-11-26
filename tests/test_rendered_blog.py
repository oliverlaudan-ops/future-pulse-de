"""Synthetic HTML and real Hugo regression tests; never publication approvals."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rendered', ROOT / 'scripts/validate-rendered-blog.py')
rendered = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rendered)

GOOD = '<article class="post-single"><details class="toc" open><a href="#gr%C3%BCn">Grün</a></details><h2 id="grün">Grün</h2></article>'

class RenderedTests(unittest.TestCase):
    def test_valid_unicode(self):
        self.assertEqual(rendered.check_article(GOOD), [])

    def test_missing_closed_empty_and_broken(self):
        for html in ('<h2 id="x">X</h2>', GOOD.replace(' open', ''),
                     GOOD.replace('href="#gr%C3%BCn"', 'href="#missing"'),
                     GOOD.replace('<a href="#gr%C3%BCn">Grün</a>', ''),
                     GOOD.replace('</article>', '<h3 id="other">Other</h3></article>'),
                     GOOD.replace('</article>', '<h2 id="grün">Duplicate</h2></article>'),
                     '<details class="toc" open></details><details class="toc"><a href="#x">X</a></details><h2 id="x">X</h2>'):
            with self.subTest(html=html):
                self.assertTrue(rendered.check_article(html))

    def test_foreign_toc_rejected(self):
        html = '<details class="toc" open><a href="#x">X</a></details><article class="post-single"><h2 id="x">X</h2></article>'
        self.assertTrue(rendered.check_article(html))
        self.assertTrue(rendered.check_article(GOOD.replace('<article class="post-single">', '').replace('</article>', '')))

    def test_home_requires_dynamic_entry_not_static_link(self):
        self.assertEqual(rendered.Page('<a href="/blog/test/">Static</a>').entries, [])
        html = '<article class="post-entry"><a class="entry-link" href="https://future-pulse.de/blog/test/"></a></article>'
        self.assertEqual(rendered.Page(html).entries, ['/blog/test/'])

    @unittest.skipUnless(shutil.which('hugo'), 'Hugo required for integration test')
    def test_real_hugo_and_home_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / 'layouts', root / 'layouts')
            (root / 'themes').symlink_to(ROOT / 'themes', target_is_directory=True)
            (root / 'hugo.toml').write_text('baseURL = "https://future-pulse.de/"\ntheme = "PaperMod"\n[params]\nmainSections = ["blog"]\n')
            article = root / 'content/blog/test/index.md'
            article.parent.mkdir(parents=True)
            article.write_text('---\ntitle: Test\ndate: 2026-01-01\nShowToc: true\nTocOpen: true\nai_generated: true\n---\n## First\nText\n## Second\nText\n')
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            subprocess.run(['hugo', '--minify'], cwd=root, check=True, capture_output=True)
            html = root / 'public/blog/test/index.html'
            self.assertEqual(rendered.check_article(html.read_text()), [])
            command = ['python3', str(ROOT / 'scripts/validate-rendered-blog.py')]
            result = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            home = root / 'public/index.html'
            home.write_text('<a href="/blog/test/">Only static</a>')
            result = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('absent from dynamic homepage', result.stderr)

    @unittest.skipUnless(shutil.which('hugo'), 'Hugo required for integration test')
    def test_hidden_articles_fail_closed(self):
        for setting in ('headless: true', 'build:\n  list: never'):
            with self.subTest(setting=setting), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / 'hugo.toml').write_text('baseURL = "https://example.org/"\n')
                article = root / 'content/blog/test/index.md'
                article.parent.mkdir(parents=True)
                article.write_text('---\ntitle: Test\nai_generated: true\n' + setting + '\n---\n## Heading\n')
                subprocess.run(['hugo', '--buildDrafts', '--buildFuture'], cwd=root, check=True, capture_output=True)
                for flags in ([], ['--preview']):
                    result = subprocess.run(['python3', str(ROOT / 'scripts/validate-rendered-blog.py'), *flags], cwd=root, capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('missing from Hugo all manifest', result.stderr)
