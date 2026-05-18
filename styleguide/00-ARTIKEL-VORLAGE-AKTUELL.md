# 📝 Artikel-Vorlage für neue Blog-Posts

**Stand:** 2026-05-18 | **Verwendet:** SEO-RULES.md + Styleguide zusammengeführt

---

## ✅ Frontmatter-Template (PFLICHT)

```yaml
---
title: "Keyword-optimierter Titel (max. 45 Zeichen!)"
date: 2026-MM-DD
draft: false
description: "150-160 Zeichen. Hauptkeyword in ersten 120 Zeichen. Mit Zahl, Benefit, CTA und [2026]."
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

## 📏 SEO-Regeln (Kurzfassung)

| Feld | Regel | Beispiel |
|------|-------|----------|
| **Title** | Max. 45 Zeichen (wegen `\| Future Pulse` Suffix) | ✅ "ChatGPT Prompts: 10 Vorlagen für 2026" (39) |
| **Description** | 150-160 Zeichen, Zahl + Benefit + CTA + [2026] | ✅ "7 No-Code-Plattformen für KI-Agenten... [2026]" |
| **URL-Slug** | Kurz, Keyword, keine Umlaute | ✅ `/blog/chatgpt-prompts-anfaenger/` |
| **Content** | Min. 800 Wörter, 3+ H2s, Du-Ansprache | |
| **Interne Links** | 2-3 im Text + "Weiterführende Artikel" am Ende | |

---

## 📐 Artikel-Struktur

```markdown
## Einleitung: Hook den Leser!

Starte mit einer **Frage**, einem **Problem** oder einer **überraschenden Aussage**.

**Was du lernen wirst:**
- ✅ [Lernziel 1]
- ✅ [Lernziel 2]
- ✅ [Lernziel 3]

---

## Hauptteil: Problem + Lösung

### 🔍 Das Problem

Beschreibe das Problem deiner Zielgruppe konkret.

---

### ✅ Die Lösung

Biete **actionable Steps** oder ein **Framework**.

---

## Praxis-Beispiel

**Szenario:** [Konkretes Beispiel]
**Vorher:** [Negatives Ergebnis]
**Nachher:** [Positives Ergebnis]
**Learnings:** [Was können Leser mitnehmen?]

---

## Häufige Fehler vermeiden

❌ **Fehler 1:** [Beschreibung]
✅ **Lösung:** [Wie man es richtig macht]

---

## Fazit: Key Takeaway

**Das Wichtigste in Kürze:**
- ✅ Hauptpunkt 1
- ✅ Hauptpunkt 2
- ✅ Hauptpunkt 3

---

**💬 Deine Meinung?**

[Konkrete Frage an die Community]

**📌 Weiterführende Artikel:**

- [Verwandter Artikel 1](/blog/slug-1/)
- [Verwandter Artikel 2](/blog/slug-2/)
- [Verwandter Artikel 3](/blog/slug-3/)

**🎯 Willst du regelmäßig Updates zu KI-Kompetenz & Future Skills?**  
Abonniere den **Future Pulse Newsletter** – wöchentlich praxisnahe Insights, keine Marketing-Floskeln.

[→ Zum Newsletter](https://future-pulse.de/newsletter/)
```

---

## ✅ Checkliste vor dem Publish

```
□ Title ≤ 45 Zeichen (wegen "| Future Pulse" Suffix)
□ Description 150-160 Zeichen mit Zahl, Benefit, CTA, Jahr [2026]
□ URL-Slug kurz, mit Keyword, keine Umlaute
□ Min. 800 Wörter Qualitätscontent
□ Min. 3 H2-Überschriften
□ 2-3 interne Links im Fließtext
□ "Weiterführende Artikel"-Sektion am Ende
□ Tags: 3-5 Stück (bestehende wiederverwenden)
□ Keywords: 3-5 Stück
□ ShowToc: true, TocOpen: true
□ draft: false
□ author: "Oliver Laudan"
□ Keyword in ersten 100 Wörtern
□ Absätze max. 3-4 Sätze
□ Du-Ansprache durchgehend
```

---

## 🏷️ Bestehende Tags (wiederverwenden)

ChatGPT, Prompt Engineering, KI-Tools, KI-Trends, Productivity, KI-Modelle, Automatisierung, No-Code, AI Agents, Claude AI, OpenAI, Gemini, GPT-5, Ollama, Lokale KI, Privacy

---

## 🚫 Konfiguration NICHT ändern

- `hugo.toml` → Site-Title muss `Future Pulse` bleiben
- `static/robots.txt` → Custom robots.txt mit Bot-Blocks
- `enableRobotsTXT = false` → Muss false bleiben
- `.github/workflows/hugo.yml` → baseURL muss `https://future-pulse.de/` sein
- `layouts/partials/extend_footer.html` → Cookie Consent Banner
- `layouts/partials/google_analytics.html` → GA lädt nur nach Consent
- `layouts/partials/footer.html` → Nicht ändern!
- Impressum und Datenschutzerklärung → Nur mit rechtlicher Prüfung ändern

---

**Vollständige Regeln:** Siehe `SEO-RULES.md` im Root des Repos.
