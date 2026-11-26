#!/usr/bin/env python3
"""Check actual Hugo HTML using Hugo's own permalink manifest, not slug guesses."""
import argparse
import csv
import io
from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import urlsplit, unquote


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.stack = []
        self.headings = []
        self.toc_links = []
        self.entries = []
        self.open_toc = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        in_article = any(x[3] for x in self.stack)
        article = tag == 'article' and 'post-single' in classes
        toc = in_article and tag == 'details' and 'toc' in classes and 'open' in attrs
        entry = tag == 'article' and bool({'post-entry', 'first-entry'} & set(classes))
        if toc and 'open' in attrs:
            self.open_toc = True
        in_toc = toc or any(x[1] for x in self.stack)
        in_entry = entry or any(x[2] for x in self.stack)
        if tag in ('h2', 'h3', 'h4', 'h5', 'h6') and not in_toc and in_article:
            self.headings.append(attrs.get('id'))
        if tag == 'a':
            href = attrs.get('href', '')
            if in_toc:
                self.toc_links.append(href)
            if in_entry and 'entry-link' in classes:
                self.entries.append(urlsplit(href).path)
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append((tag, toc, entry, article))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def check_article(html):
    page = Page(html)
    errors = []
    if not page.open_toc:
        errors.append('missing open details.toc')
    if not page.toc_links:
        errors.append('empty or missing rendered ToC links')
    targets = []
    for href in page.toc_links:
        target = unquote(href[1:]) if href.startswith('#') else ''
        targets.append(target)
        if not target or page.headings.count(target) != 1:
            errors.append('ToC link has no unique heading target: ' + href)
    if not set(x for x in page.headings if x).issubset(targets):
        errors.append('rendered headings missing from ToC')
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base')
    parser.add_argument('--site', default='public')
    parser.add_argument('--preview', action='store_true', help='manifest includes drafts/future; use matching non-deployable build')
    args = parser.parse_args()
    selected = None
    if args.base:
        selected = set(subprocess.check_output(['git', 'diff', '--name-only', '--diff-filter=ACMRT', '-z', args.base + '...HEAD', '--', 'content/blog'], text=True).split('\0'))
    else:
        selected = {str(p) for p in Path('content/blog').rglob('*.md') if 'ai_generated: true' in p.read_text()}
    selected = {p for p in selected if p.endswith('.md')}
    all_rows = list(csv.DictReader(io.StringIO(subprocess.check_output(['hugo', 'list', 'all'], text=True))))
    manifest = {row['path']: row for row in all_rows}
    rows = all_rows if args.preview else list(csv.DictReader(io.StringIO(
        subprocess.check_output(['hugo', 'list', 'published'], text=True))))
    site = Path(args.site)
    # Dynamic home list may paginate; static prose links are deliberately excluded.
    homes = [site / 'index.html', *site.glob('page/*/index.html')]
    entries = set()
    for home in homes:
        if home.is_file():
            entries.update(Page(home.read_text()).entries)
    errors = []
    for path in sorted(selected):
        row = manifest.get(path)
        if row is None:
            errors.append(f'{path}: missing from Hugo all manifest (hidden/headless pages are not allowed)')
        elif row['section'] != 'blog' or row['kind'] != 'page':
            errors.append(f'{path}: expected a blog page in Hugo manifest')
    checked = 0
    for row in rows:
        if row['path'] not in selected or row['section'] != 'blog' or row['kind'] != 'page':
            continue
        checked += 1
        url = urlsplit(row['permalink']).path
        html = site / unquote(url).lstrip('/') / 'index.html'
        if not html.is_file():
            errors.append(f"{row['path']}: missing rendered article {html}")
            continue
        errors.extend(f"{row['path']}: {e}" for e in check_article(html.read_text()))
        if url not in entries:
            errors.append(f"{row['path']}: absent from dynamic homepage list (including pagination)")
    print(f'Validated {checked} rendered blog article(s), preview={args.preview}')
    if errors:
        raise SystemExit('\n'.join(errors))


if __name__ == '__main__':
    main()
