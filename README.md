# Future Pulse Tech 🚀

**Dein Guide für KI-Kompetenz, Future Skills und digitale Transformation**

Built with Hugo + GitHub Pages | Live seit Dezember 2025

---

## 🎯 Live Site

👉 **Production:** [https://future-pulse.de](https://future-pulse.de)

👉 **GitHub Pages Fallback:** [https://oliverlaudan-ops.github.io/future-pulse-tech/](https://oliverlaudan-ops.github.io/future-pulse-tech/)

---

## 🛠️ Tech Stack

- **Static Site Generator:** [Hugo](https://gohugo.io/) Extended v0.134.2+
- **Theme:** [PaperMod](https://github.com/adityatelange/hugo-PaperMod) (aktiv maintained 2026)
- **Hosting:** GitHub Pages
- **CI/CD:** GitHub Actions (Auto-Deployment bei Push auf `main`)
- **Custom Domain:** future-pulse.de (DNS via Cloudflare)
- **SSL:** Let's Encrypt (automatisch via GitHub Pages)

---

## 📊 Repository Status (Stand März 2026)

| Metric | Status |
|--------|--------|
| **Live seit** | Dezember 2025 |
| **Blog-Artikel** | 10+ (aktiv wachsend) |
| **Letzte Updates** | März 2026 |
| **Sprache** | Deutsch |
| **Theme-Version** | PaperMod (latest stable) |
| **Custom Domain** | ✅ Live (future-pulse.de) |
| **HTTPS** | ✅ Aktiv |
| **Auto-Deployment** | ✅ GitHub Actions |

**Neueste Artikel:**
- OpenClaw auf Contabo VPS: Setup-Guide 2026 (02.03.2026)
- Agentic AI im Arbeitsalltag: 7 Praxis-Beispiele (23.02.2026)
- Agentic AI: Revolution oder Risiko 2026 (16.02.2026)

---

## 📏 Project Structure

```
future-pulse-tech/
├── .github/
│   └── workflows/
│       └── hugo.yml          # Auto-Deployment Workflow
├── content/
│   ├── _index.md          # Homepage
│   ├── about.md           # Über-Seite
│   ├── impressum.md       # Impressum (TMG-konform)
│   └── blog/
│       ├── _index.md       # Blog-Index
│       └── *.md            # Blog-Artikel (10+ aktiv)
├── static/
│   ├── images/          # Bilder & Assets
│   └── CNAME            # Custom Domain Config
├── themes/
│   └── PaperMod/          # Hugo Theme (Submodule)
├── hugo.toml              # Main Config (SEO, Navigation, etc.)
├── .gitignore
├── .gitmodules
└── README.md
```

---

## ✏️ Neuen Blog-Artikel erstellen

### Option 1: Via GitHub Web Interface (Einfach)

1. Gehe zu `content/blog/`
2. Klicke **"Add file" → "Create new file"**
3. Dateiname: `dein-artikel-titel.md`
4. Füge Hugo Front Matter hinzu:

```markdown
---
title: "Dein Artikel-Titel: Benefit/Hook"
date: 2026-03-02
draft: false
author: "Oliver Laudan"
tags: ["KI-Kompetenz", "Future Skills"]
keywords: ["Hauptkeyword", "SEO-Begriff"]
description: "SEO-Description 150-160 Zeichen mit CTA"
ShowToc: true
TocOpen: true
---

## Einleitung

Dein Content hier...
```

5. **Commit changes** → GitHub Actions baut & deployt automatisch!

### Option 2: Lokal mit Hugo (Fortgeschritten)

```bash
# Repo klonen (mit Theme-Submodule)
git clone --recurse-submodules https://github.com/oliverlaudan-ops/future-pulse-tech.git
cd future-pulse-tech

# Neuen Artikel erstellen
hugo new blog/dein-artikel-titel.md

# Datei bearbeiten in content/blog/

# Lokal testen (mit Drafts)
hugo server -D
# http://localhost:1313

# Production-Build prüfen
hugo

# Committen & Pushen
git add .
git commit -m "Add: [Artikel-Titel]"
git push origin main
```

---

## 🚀 Deployment

**Automatisches Deployment** via GitHub Actions bei jedem Push auf `main`:

1. Du pushst Änderungen auf `main` Branch
2. GitHub Actions triggert `.github/workflows/hugo.yml`
3. Hugo baut statische Site (`hugo --minify`)
4. Deploy auf GitHub Pages (`gh-pages` Branch)
5. **Live in 2-3 Minuten** auf future-pulse.de

**Build-Status prüfen:**
- [Actions Tab](https://github.com/oliverlaudan-ops/future-pulse-tech/actions)
- Fehler? Check Workflow-Logs

---

## 🌐 Custom Domain Setup

**Aktueller Status:** `future-pulse.de` ist live und HTTPS-gesichert.

### Falls du eine neue Domain hinzufügen willst:

1. **GitHub Repository Settings:**
   - Gehe zu **Settings → Pages**
   - Custom Domain: `deine-domain.de`
   - **Enforce HTTPS** aktivieren

2. **DNS-Einträge bei Domain-Provider:**
   ```dns
   # A Records (für Apex Domain)
   A    @    185.199.108.153
   A    @    185.199.109.153
   A    @    185.199.110.153
   A    @    185.199.111.153
   
   # CNAME (für www-Subdomain)
   CNAME www  oliverlaudan-ops.github.io.
   ```

3. **CNAME-Datei in Repo:**
   - Erstelle `static/CNAME` mit Inhalt: `future-pulse.de`
   - Commit & Push

4. **DNS-Propagation warten:** 10 Minuten - 24 Stunden

---

## 📝 Content Guidelines

**Artikel-Struktur:**
- **800-1500 Wörter** (Sweet Spot für SEO)
- **3+ H2-Überschriften** mit Keywords
- **Du-Form & zugränglich** (kein Akademiker-Jargon)
- **Code-Blöcke** für Terminal-Befehle
- **Tabellen** für Vergleiche

**SEO-Checkliste:**
- Hauptkeyword in Titel (Position 1-3)
- Meta-Description 150-160 Zeichen
- Alt-Texte für Bilder
- 2-3 interne Links zu anderen Artikeln
- `ShowToc: true` für Inhaltsverzeichnis

**Bilder:**
- Speichere in `static/images/` oder nutze externe CDN-URLs
- Referenz im Markdown: `![Alt-Text](/images/datei.png)`
- **WebP bevorzugt** (<200 KB pro Bild)

**Drafts:**
- `draft: true` im Front Matter macht Artikel unsichtbar
- Lokal testen mit `hugo server -D`

---

## 👥 Team & Kontribution

**Autor:** Oliver Laudan ([GitHub](https://github.com/oliverlaudan-ops))

**E-Mail:** oliver.laudan@gmail.com

**Website:** [future-pulse.de](https://future-pulse.de)

Dies ist ein **Personal Blog**, aber Feedback & Vorschläge sind willkommen!

---

## 🔧 Wartung & Updates

**Theme-Updates (PaperMod):**
```bash
# Theme-Submodule aktualisieren
cd themes/PaperMod
git pull origin master
cd ../..
git add themes/PaperMod
git commit -m "Update PaperMod theme"
git push
```

**Hugo-Version updaten:**
- Ändere in `.github/workflows/hugo.yml`: `hugo-version: '0.XXX.X'`
- Teste lokal: `hugo version`

---

## 📜 Lizenz

**Content:** © 2026 Oliver Laudan (Alle Rechte vorbehalten)

**Theme:** MIT License ([PaperMod](https://github.com/adityatelange/hugo-PaperMod))

**Code-Beispiele in Artikeln:** MIT License (sofern nicht anders angegeben)

---

## 🔗 Links

- **Live Site:** [future-pulse.de](https://future-pulse.de)
- **GitHub Repo:** [oliverlaudan-ops/future-pulse-tech](https://github.com/oliverlaudan-ops/future-pulse-tech)
- **Hugo Docs:** [gohugo.io/documentation](https://gohugo.io/documentation/)
- **PaperMod Theme:** [adityatelange/hugo-PaperMod](https://github.com/adityatelange/hugo-PaperMod)
- **GitHub Pages Docs:** [docs.github.com/pages](https://docs.github.com/en/pages)

---

**Built with ❤️ by Oliver Laudan**

*Letzte Aktualisierung: März 2026*
