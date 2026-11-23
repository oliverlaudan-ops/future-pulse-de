"""Isolated evidence-contract regression tests; fixtures are not real approvals."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

VALIDATOR = Path(__file__).resolve().parents[1] / 'scripts/validate-blog-frontmatter.py'

class ReviewGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.article = self.root / 'content/blog/test/index.md'
        self.article.parent.mkdir(parents=True)
        self.article.write_text('---\nai_generated: true\nai_model: writer\nai_reviewer: reviewer\nai_review_status: passed_draft_only\ndraft: true\n---\nTest article\n')
        self.evidence = self.root / 'reviews/test.json'
        self.evidence.parent.mkdir()
        self.report = dict(article_path='content/blog/test/index.md', article_sha256=self.sha(), writer='writer', reviewer='reviewer', status='passed_draft_only', review_date='2026-11-23', sources=['https://example.org/source'], findings='Synthetic contract fixture, not a genuine editorial approval. ' * 3, gates={k: 'passed' for k in ('primary_sources', 'factual_accuracy', 'seo', 'duplicate_check', 'internal_links', 'metadata', 'readability')})

    def sha(self):
        return hashlib.sha256(self.article.read_bytes()).hexdigest()

    def save(self):
        self.evidence.write_text(json.dumps(self.report))

    def check(self, expected):
        result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_missing_report(self): self.check(1)
    def test_invalid_json(self):
        self.evidence.write_text('{'); self.check(1)
    def test_invalid_shape(self):
        self.evidence.write_text('[]'); self.check(1)
    def test_wrong_hash(self):
        self.report['article_sha256'] = '0' * 64; self.save(); self.check(1)
    def test_complete_report(self): self.save(); self.check(0)
    def test_later_article_change(self):
        self.save(); self.article.write_text(self.article.read_text() + 'Changed\n'); self.check(1)
    def test_self_review(self):
        self.report['writer'] = ' REVIEWER '; self.save(); self.check(1)
    def test_missing_reviewer_even_with_human(self):
        self.article.write_text(self.article.read_text().replace('ai_reviewer: reviewer', 'human_reviewer: Someone')); self.check(1)
    def test_missing_draft_is_not_exemption(self):
        self.article.write_text(self.article.read_text().replace('draft: true\n', '')); self.check(1)
    def test_non_draft_valid_report(self):
        self.article.write_text(self.article.read_text().replace('draft: true\n', '').replace('passed_draft_only', 'passed').replace('ai_model: writer', 'ai_model: writer\nreview_date: 2026-11-23'))
        self.report.update(status='passed', article_sha256=self.sha()); self.save(); self.check(0)
    def test_gate_not_passed(self):
        self.report['gates']['seo'] = 'pending'; self.save(); self.check(1)
    def test_invalid_date(self):
        self.report['review_date'] = '2026-99-99'; self.save(); self.check(1)

    def test_report_can_follow_article_commit(self):
        def git(*args):
            return subprocess.check_output(['git', *args], cwd=self.root, text=True).strip()
        git('init', '-q')
        git('config', 'user.name', 'Fixture')
        git('config', 'user.email', 'fixture@example.invalid')
        git('commit', '--allow-empty', '-qm', 'base')
        base = git('rev-parse', 'HEAD')
        git('add', 'content'); git('commit', '-qm', 'article without evidence')
        def validate(expected):
            r = subprocess.run([sys.executable, str(VALIDATOR), '--base', base], cwd=self.root, capture_output=True, text=True)
            self.assertEqual(r.returncode, expected, r.stdout + r.stderr)
        validate(1)
        self.save(); git('add', 'reviews'); git('commit', '-qm', 'later evidence')
        validate(0)
        self.article.write_text('---\ntitle: Removed metadata\n---\nChanged article\n')
        git('add', 'content'); git('commit', '-qm', 'changed article')
        validate(1)

if __name__ == '__main__': unittest.main()
