#!/usr/bin/env python3
"""Validate editorial metadata for AI-reviewed articles without rewriting legacy posts."""
from pathlib import Path
import re
import sys

ROOT = Path('content/blog')
errors = []
checked = 0
for path in ROOT.glob('*/index.md'):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        errors.append(f'{path}: missing YAML frontmatter')
        continue
    front = text.split('\n---\n', 1)[0][4:]
    fields = {}
    for line in front.splitlines():
        match = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip('"\'')
    if not fields.get('ai_reviewer'):
        continue  # Legacy human-reviewed posts: preserve existing semantics
    checked += 1
    for key in ('ai_generated', 'ai_model', 'ai_reviewer', 'ai_review_status', 'draft'):
        if not fields.get(key):
            errors.append(f'{path}: missing {key}')
    if fields.get('ai_generated') != 'true':
        errors.append(f'{path}: AI-reviewed article must declare ai_generated: true')
    if fields.get('human_reviewer'):
        errors.append(f'{path}: human_reviewer must not be set without a real human review')
    status = fields.get('ai_review_status')
    if status not in ('passed', 'failed', 'pending', 'passed_draft_only'):
        errors.append(f'{path}: invalid ai_review_status {status!r}')
    if fields.get('draft') == 'false':
        if status != 'passed':
            errors.append(f'{path}: publication requires ai_review_status: passed')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', fields.get('review_date', '')):
            errors.append(f'{path}: publication requires review_date YYYY-MM-DD')
print(f'Validated {checked} AI-reviewed blog article(s)')
if errors:
    print('\n'.join('ERROR: ' + e for e in errors), file=sys.stderr)
    sys.exit(1)
