#!/usr/bin/env python3
"""
build-image-manifest.py
=======================

Reads Hugo blog posts under content/blog/**/index.md, walks the YAML
frontmatter for `cover.image` entries, classifies the image origin
(KI-generiert / lizenziertes Stock / eigenes Asset / unbekannt), and
emits:

  - static/image-manifest.json   (machine-readable, published)
  - build/image-manifest-stats.txt (human-readable summary)

Run from repo root:
  python3 build/build-image-manifest.py

Deterministic — the same cover URLs always hash to the same
`image_id`. Re-runs only add `last_verified_at`. This means we can
keep the JSON file in Git and see provenance drift across edits.

Heuristic notes:

  We do NOT pretend to be a real C2PA verifier. We classify by URL
  origin heuristics (Generator-Hostname → Klasse). To know more, an
  auditor would need a side-channel (export tickets, licence PDFs,
  prompt logs in our private archive).
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS = sorted((REPO_ROOT / "content" / "blog").rglob("index.md"))
OUT_JSON = REPO_ROOT / "static" / "image-manifest.json"
OUT_STATS = REPO_ROOT / "build" / "image-manifest-stats.txt"

GENERATOR_HOSTS = {
    "seedream":           "ai-generated/seedream",
    "cdn.leonardo.ai":    "ai-generated/leonardo-ai",
    "cdn.midjourney.com": "ai-generated/midjourney",
    "cdn.openai.com":     "ai-generated/dall-e",
    "replicate.delivery": "ai-generated/replicate",
    "images.weserv.nl":   "proxy/unknown-origin",
    "unsplash":           "stock/unsplash",
    "cdn.pixabay.com":    "stock/pixabay",
    "images.pexels.com":  "stock/pexels",
    "cdn.istockphoto.com":"stock/istock",
}


def classify(url: str) -> str:
    for needle, label in GENERATOR_HOSTS.items():
        if needle in url:
            return label
    if "raw.githubusercontent.com" in url:
        return "self-hosted/github-raw"
    if "future-pulse.de" in url or url.startswith("/"):
        return "self-hosted/local"
    return "unknown/manual-review"


def short_hash(*parts: str) -> str:
    h = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return h[:16]


def parse_frontmatter(text: str):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}, ""
    fm_block = m.group(1)
    body = text[m.end():]
    return _walk_yaml(fm_block), body


def _walk_yaml(block: str):
    """Tiny subset of YAML parsing — only top-level + 1 nested level, no lists of maps."""
    out = {}
    cur_key = None
    cur_map = None
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and ":" in line:
            key, _, val = line.partition(":")
            val = val.strip().strip('"').strip("'")
            if not val:
                cur_key = key.strip()
                cur_map = {}
                out[cur_key] = cur_map
            else:
                out[key.strip()] = val
                cur_key = None
                cur_map = None
        elif line.startswith("  ") and cur_map is not None and ":" in line:
            key, _, val = line.partition(":")
            val = val.strip().strip('"').strip("'")
            cur_map[key.strip()] = val
    return out


def main() -> int:
    items = []
    seen_ids = set()
    for post in POSTS:
        slug = post.parent.name
        text = post.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        cover = fm.get("cover") or {}
        url = cover.get("image", "").strip().strip('"').strip("'")
        if not url:
            continue
        image_id = short_hash(slug, url)
        if image_id in seen_ids:
            continue
        seen_ids.add(image_id)
        items.append({
            "image_id":         image_id,
            "post_slug":        slug,
            "post_url":         f"https://future-pulse.de/blog/{slug}/",
            "image_url":        url,
            "alt_text":         cover.get("alt", "").strip(),
            "caption":          cover.get("caption", "").strip(),
            "provenance_class": classify(url),
            "c2pa_manifest":    None,  # wir generieren kein Manifest, wir dokumentieren das Fehlen
            "last_verified_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })

    counts = {}
    for it in items:
        counts[it["provenance_class"]] = counts.get(it["provenance_class"], 0) + 1

    payload = {
        "schema": "future-pulse-de/image-manifest",
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator":     "build/build-image-manifest.py",
        "scope":         f"{len(POSTS)} blog posts scanned under content/blog/",
        "method":        "URL-origin classification heuristic, not C2PA verification",
        "c2pa_strategy": "We do NOT embed fake C2PA signatures into images we don't own. "
                         "This manifest is the honest disclosure of provenance we can attest to.",
        "summary":       counts,
        "items":         sorted(items, key=lambda i: (i["provenance_class"], i["post_slug"])),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
                        encoding="utf-8")

    OUT_STATS.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"Image-Manifest Summary — generated {payload['generated_at']}",
        f"Scope: {payload['scope']}",
        "",
        f"{'count':>5}  class",
    ]
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"{v:5d}  {k}")
    lines.append("")
    lines.append(f"Total entries: {len(items)}")
    lines.append(f"Output: {OUT_JSON.relative_to(REPO_ROOT)}")
    OUT_STATS.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
