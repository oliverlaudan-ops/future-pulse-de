# Future Pulse SEO – Regeln für neue Artikel

**Stand:** 2026-05-18 | **Verantwortlich:** Viv (AI Agent)

---

## Technisches Setup

- **Stack:** Hugo + PaperMod Theme, GitHub Pages
- **Repo:** `oliverlaudan-ops/future-pulse-de`
- **Artikel-Pfad:** `content/blog/{slug}/index.md`
- **Deploy:** Push auf `main` → GitHub Actions baut & deployt automatisch
- **Site-Title:** `Future Pulse` (wird automatisch an jeden Title angehängt: `{Artikel-Title} | Future Pulse`)

---

## Frontmatter-Template (PFLICHT)

```yaml
---
title: "Keyword-optimierter Titel (max. 45 Zeichen!)"
date: YYYY-MM-DD
draft: false
description: "Klick-optimierte Meta-Description, 150-160 Zeichen. Mit konkreten Zahlen, Benefit und CTA."
summary: "Kurze Zusammenfassung für die Blog-Übersichtsseite. 1-2 Sätze."
tags: ["Tag1", "Tag2", "Tag3"]
keywords: ["hauptkeyword", "long-tail keyword 1", "long-tail keyword 2"]
author: "Oliver Laudan"
cover:
 image: ""
 alt: "Beschreibender Alt-Text mit Keyword"
 caption: "Bildunterschrift"
 relative: false
ShowToc: true
TocOpen: true
---
```

---

## REGEL 1: Title-Tag (KRITISCH)

**Max. 42–45 Zeichen** im Frontmatter (wegen `| Future Pulse` Suffix = 16 Zeichen)

Formel: `[Hauptkeyword]: [Benefit/Lösung] [Jahr]`

✅ "ChatGPT Prompts: 10 Vorlagen für 2026" (39 Zeichen)
✅ "KI-Kompetenz aufbauen: Der 30-Tage-Plan" (41 Zeichen)
❌ "Prompt Engineering Deutsch: Der komplette Guide für 2026" (57 Zeichen → 73 mit Suffix = ABGESCHNITTEN)

---

## REGEL 2: Meta-Description

- **Länge:** 150–160 Zeichen (optimal: 155)
- **Hauptkeyword** in den ersten 120 Zeichen
- **Pflicht:** Zahl + Benefit + CTA + Jahreszahl [2026]

✅ "7 No-Code-Plattformen für KI-Agenten im Vergleich: Zapier, Make, n8n & mehr. Kosten, Features & praxisnahe Use Cases – dein erster KI-Agent in 15 Minuten. [2026]"

---

## REGEL 3: URL-Slug

- Kurz, max. 60 Zeichen
- Hauptkeyword enthalten
- Nur Kleinbuchstaben und Bindestriche
- Keine Umlaute (ä→ae, ö→oe, ü→ue, ß→ss)

✅ `/blog/chatgpt-prompts-anfaenger/`
❌ `/blog/der-ultimative-guide-zum-thema-künstliche-intelligenz-für-anfänger-2026/`

---

## REGEL 4: Interne Verlinkung (PFLICHT)

Jeder Artikel MUSS am Ende haben:

```markdown
---

## Weiterführende Artikel

- [Verwandter Artikel 1](/blog/slug-1/)
- [Verwandter Artikel 2](/blog/slug-2/)
- [Verwandter Artikel 3](/blog/slug-3/)
```

Plus 2–3 interne Links im Fließtext mit beschreibenden Anchor-Texten.

---

## REGEL 5: Content-Qualität

- Mindestlänge: 800 Wörter (optimal: 1000–1500)
- Struktur: Min. 3 H2-Überschriften
- Keyword in den ersten 100 Wörtern
- Absätze: Max. 3–4 Sätze
- Mindestens 1 Liste pro Artikel
- Fettungen für wichtige Begriffe
- Fazit/Zusammenfassung am Ende
- `ShowToc: true` immer aktiviert

---

## REGEL 6: Sprache & Tonalität

- Du-Ansprache (nicht "man" oder "Sie")
- Professionell, aber nahbar
- Aktive Sprache
- Fachbegriffe erklären
- Emojis: Sparsam, max. 2–3 pro Abschnitt
- Deutsch als Hauptsprache

---

## REGEL 7: Tags und Keywords

- Tags: 3–5 relevante Tags (bestehende wiederverwenden)
- Keywords: 3–5 Keywords im Frontmatter

Bestehende Tags: ChatGPT, Prompt Engineering, KI-Tools, KI-Trends, Productivity, KI-Modelle, Automatisierung, No-Code, AI Agents, Claude AI, OpenAI, Gemini, GPT-5

---

## REGEL 8: Konfiguration NICHT ändern

- `hugo.toml` → Site-Title muss `Future Pulse` bleiben
- `static/robots.txt` → Custom robots.txt mit Bot-Blocks
- `enableRobotsTXT = false` → Muss false bleiben
- `.github/workflows/hugo.yml` → baseURL muss `https://future-pulse.de/` sein
- `layouts/partials/extend_footer.html` → Cookie Consent Banner
- `layouts/partials/google_analytics.html` → GA lädt nur nach Consent
- `layouts/partials/footer.html` → Nicht ändern!
- Impressum und Datenschutzerklärung → Nur mit rechtlicher Prüfung ändern

---

## Checkliste: Vor dem Publish

```
□ Title ≤ 45 Zeichen
□ Description 150–160 Zeichen mit Zahl, Benefit, CTA, Jahr
□ URL-Slug kurz, mit Keyword, keine Umlaute
□ Min. 800 Wörter
□ Min. 3 H2-Überschriften
□ 2–3 interne Links im Text
□ "Weiterführende Artikel"-Sektion am Ende
□ Tags: 3–5 Stück
□ Keywords: 3–5 Stück
□ ShowToc: true, TocOpen: true
□ draft: false
□ author: "Oliver Laudan"
□ Keyword in ersten 100 Wörtern
□ Absätze max. 3–4 Sätze
□ Du-Ansprache
```
