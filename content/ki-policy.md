---
title: "KI-Policy: Unser Umgang mit künstlicher Intelligenz"
date: 2026-08-11
draft: false
description: "Wie wir auf future-pulse.de KI einsetzen, was wir kennzeichnen, was wir aufbewahren — Selbstauskunft nach EU AI Act Art. 4, 50 und 12."
summary: "Transparenz über KI-Einsatz, Kennzeichnung von KI-generierten Inhalten und Aufbewahrungspflichten — die drei Säulen unserer KI-Compliance auf future-pulse.de."
keywords: ["KI Policy", "EU AI Act", "Art. 50 Kennzeichnung", "Art. 4 KI-Kompetenz", "Art. 12 Aufbewahrung", "KI Transparenz"]
author: "Oliver Laudan"
---

# KI-Policy: Unser Umgang mit künstlicher Intelligenz

Diese Seite ist unsere offizielle Selbstauskunft zum Einsatz von KI auf `future-pulse.de`. Sie erfüllt drei Pflichten aus dem **EU AI Act** (in Kraft seit 1. August 2024, Geltungsbeginn für die meisten Bestimmungen seit 2. August 2026):

- **Art. 4** — KI-Kompetenz von Betreibern und Betroffenen
- **Art. 50** — Transparenz- und Kennzeichnungspflichten für KI-generierte Inhalte
- **Art. 12 i.V.m. Anhang IV** — Aufbewahrungspflicht für technische Dokumentation

Stand: 11. August 2026. Bei wesentlichen Änderungen wird das Datum oben aktualisiert.

---

## 1. Wer schreibt hier? (Art. 4 – KI-Kompetenz)

`future-pulse.de` ist ein **Ein-Personen-Blog** von [Oliver Laudan](https://www.linkedin.com/in/oliver-laudan) (Kontakt: `kontakt@future-pulse.de`).

**KI-Kompetenz im Sinne von Art. 4 EU AI Act:**

- Tägliche, dokumentierte Arbeit mit KI-Tools seit 2023 (LLM-Prompting, Embedding-Modelle, Agent-Frameworks).
- Mehrjährige Berufserfahrung im IT-Support mit Schwerpunkt Telefonie-/ServiceNow-Plattformen; Schwerpunktverlagerung auf KI-Kompetenz und Future Skills seit Anfang 2025.
- Kontinuierliche Weiterbildung durch: (a) eigene Blogartikel auf `future-pulse.de`, (b) aktive Mitarbeit an Open-Source-Projekten wie `learning-german` und `prompt-factory-v2`, (c) experimentelle Projekte (Crows Federation, Idle Games). Eine Sammlung veröffentlichter Projekte findet sich auf [github.com/oliverlaudan-ops](https://github.com/oliverlaudan-ops).
- Praktische Erfahrung mit lokalem Modellbetrieb (Ollama, llama.cpp) und Cloud-KI (Ollama Cloud, OpenAI, Anthropic, Google) — inkl. deren Grenzen, Halluzinationsverhalten, Bias-Risiken und Kostenstrukturen.

Diese Kompetenz wird auf die Inhalte dieser Site angewendet: Recherche, technische Validierung und finale inhaltliche Prüfung liegen bei Oliver Laudan. KI ist Werkzeug, nicht Autor.

---

## 2. Was wir kennzeichnen — und was nicht (Art. 50 EU AI Act)

**Wir kennzeichnen jeden Blog-Beitrag, der mithilfe von KI erstellt wurde, direkt am Artikel selbst.** Die Kennzeichnung erscheint als Box am Ende jedes Beitrags (zwischen Fließtext und Footer). Sie enthält die vier Pflichtangaben:

1. **Modellname** — z. B. `minimax-m3:cloud`, `kimi-k2.5:cloud`, `claude-opus-46`
2. **Wer hat geprüft?** — Name des/der redaktionell prüfenden Person
3. **Wann geprüft?** — Datum der letzten inhaltlichen Prüfung
4. **Status** — vollständig KI-generiert / KI-gestützt / menschlich verfasst

Diese Felder sind Bestandteil des Hugo-Frontmatter und werden vom Theme automatisch gerendert. Die technische Doku dazu liegt unter [`docs/CONTENT-METADATA.md`](https://github.com/oliverlaudan-ops/future-pulse-de/blob/main/docs/CONTENT-METADATA.md).

**Wir kennzeichnen nicht als KI-Inhalt:**

- Reine Quellenangaben / Zitate aus Fachliteratur, Studien und Pressemitteilungen
- Code-Beispiele und technische Konfigurationsanleitungen, sofern sie aus offiziellen Dokumentationen der jeweiligen Anbieter stammen und manuell kuratiert sind
- Gastbeiträge und Interviews (diese sind in der Regel explizit namentlich gekennzeichnet)
- Reine Linklisten/Verzeichnisse ohne redaktionelle Eigenleistung

**Eingeschränkte Aussage zur maschinenlesbaren Kennzeichnung (C2PA / IPTC AI-Disclosure):**

Wir prüfen die Integration von C2PA-Manifest-Metadaten in unsere Bildpipeline. Bis zur Einführung gilt: Cover-Bilder, die KI-generiert sind, werden im Alt-Text und in der Bildunterschrift als „KI-generiert" markiert. Bilder von lizenzierten Stock-Anbietern (z. B. Leonardo.ai, Adobe Stock) tragen dort die Provenienz-Metadaten.

---

## 3. Was wir aufbewahren (Art. 12 i.V.m. Anhang IV)

**Aufbewahrungsfrist: 6 Jahre ab Veröffentlichung** jedes Beitrags.

**Was wird aufbewahrt:**

| Dokumenttyp | Speicherort | Zweck |
|---|---|---|
| Hugo-Quelldateien mit vollständigem Frontmatter (inkl. Modellname, Reviewer, Review-Datum) | GitHub: `oliverlaudan-ops/future-pulse-de` (privater Branching-Workflow) | Nachweis der redaktionellen Verantwortung |
| GitHub Actions Build- und Deploy-Logs | GitHub Actions Standard-Aufbewahrung (90 Tage Standard, manuelle Export-Option) | Nachweis der Veröffentlichungstermine |
| Redaktionelle Review-Kommentare und Korrekturen | `git log`-History auf demselben Repo | Nachvollziehbarkeit jeder Änderung |
| E-Mail-Korrespondenz mit Korrekturen oder Beanstandungen | E-Mail-Archiv (Passwort-Manager + IMAP-Backup) | Nachweis von Leser-Feedback und Korrekturen |

**Aufbewahrungssystem im Sinne von Art. 11 (Versionsverwaltung):**

- Git-Repository mit Commit-History (SHA-Hashes)
- Branch-Protection auf `main` (keine Force-Pushes, Review via PR)
- GitHub Actions Workflow `.github/workflows/hugo.yml` mit Pinning auf `actions/checkout@v4` und `peaceiris/actions-hugo@v3` für reproduzierbare Builds
- Manuelle Export-Snapshots mindestens **einmal jährlich** in einen verschlüsselten lokalen Archiv-Ordner (`~/Documents/archive/future-pulse/<jahr>-snapshot.tar.gz.enc`)

Auf Anfrage einer Aufsichtsbehörde (z. B. Bundesnetzagentur) kann aus dem Git-Repository, den Action-Logs und dem Jahres-Snapshot ein vollständiges Audit-Paket erstellt werden.

---

## 4. Was wir **nicht** auf `future-pulse.de` einsetzen (selbstauskunft gemäß Art. 50 Abs. 1)

- **Keine biometrische Identifizierung** von Leserinnen und Lesern.
- **Keine Emotionserkennung** (z. B. Webcam-Affektanalyse).
- **Kein Social Scoring** von Leserinnen und Lesern.
- **Keine Hochrisiko-KI-Systeme** im Sinne von Anhang III.
- **Keine GPT-/Chat-Bots mit Eingaben von Minderjährigen** als Hauptzielgruppe. Der Blog richtet sich an ein erwachsenes Fachpublikum.

Wir nutzen **Google Analytics 4** ausschließlich in der anonymisierten Variante (`anonymize_ip: true`, `respectDoNotTrack: true`), mit aktiver Cookie-Einwilligung (DSGVO / TDDDG § 25). Siehe [Datenschutzerklärung](/datenschutz/).

---

## 5. GPAI-Integratoren (Art. 53)

Wir betreiben zwei kleinere Open-Source-Anwendungen, die als GPAI-Integratoren gelten könnten:

- **prompt-factory-v2** — Live auf `prompts.future-pulse.de`. Repository: [`oliverlaudan-ops/prompt-factory-v2`](https://github.com/oliverlaudan-ops/prompt-factory-v2). Eigene Compliance-Doku im Repo.
- **learning-german** — Vite/TS-Single-Page-App für Vokabeltraining. Repository: [`oliverlaudan-ops/learning-german`](https://github.com/oliverlaudan-ops/learning-german). Trainiert nicht auf Nutzereingaben; Client-seitiges Lernen im Browser ohne Telemetrie.

Beide Anwendungen sind **eigenständige Repositories** und werden dort separat dokumentiert (jeweils mit eigener KI-/Datenschutz-Policy). Diese `KI-Policy`-Seite gilt ausschließlich für `future-pulse.de`.

---

## 6. Änderungshistorie

| Datum | Änderung |
|---|---|
| 2026-08-11 | Erste Veröffentlichung dieser Seite. Vorangegangen war ein internes Audit gegen den ab 2. August 2026 vollständig anwendbaren EU AI Act. |

---

## 7. Fragen, Beanstandungen, Korrekturen

Wir freuen uns über Hinweise — Korrekturen, Fakt-Checks und Beanstandungen nehmen wir ernst. Bitte per E-Mail an **kontakt@future-pulse.de** oder über [LinkedIn](https://linkedin.com/in/oliver-laudan).

Bei rechtlichen Beschwerden richten wir uns nach den Vorgaben des Digitale-Dienste-Gesetzes (DDG) und der DSGVO.
