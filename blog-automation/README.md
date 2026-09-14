# Blog-Automation – Themen-Queue

Dieses Verzeichnis steuert die **automatische Blog-Artikel-Generierung** für [future-pulse.de](https://future-pulse.de).

## Aktive Datei: `topics.json`

`blog-automation/topics.json` ist die **aktive Themen-Queue**. Nur diese Datei wird vom Automatik-System gelesen und geschrieben.

> ⚠️ **Hinweis:** Die Datei `topics.legacy.json` im Repo-Root ist **veraltet/archiviert** und wird **nicht** mehr verwendet. Sie dient nur noch als historische Referenz und kann bei Bedarf gelöscht werden.

## Wer schreibt die Artikel?

Ein **Abacus AI Scheduled Task ("Blog Writer", Task-ID `149d51bb66`)** übernimmt die komplette Automation:

| Eigenschaft | Wert |
|-------------|------|
| **Frequenz** | 2× pro Woche |
| **Tage/Zeit** | Dienstag & Freitag, 09:00 Uhr (Europe/Berlin) |
| **Cron** | `0 9 * * 2,5` |
| **Ziel-Repo** | `oliverlaudan-ops/future-pulse-de` (Branch `main`) |

**Ablauf pro Lauf:**

1. Wählt ein Thema mit `status: "pending"` aus `topics.json`.
2. Prüft auf Duplikate (Slug + inhaltliche Überschneidung mit bestehenden Artikeln unter `content/blog/`).
3. Erstellt einen SEO-optimierten Artikel (ca. 800–1500 Wörter) nach `content/blog/{slug}/index.md`.
4. Committet und pusht direkt nach `main` (autonome Veröffentlichung, kein PR).

Maßgeblich für Stil und SEO sind [`../SEO-RULES.md`](../SEO-RULES.md) und die Vorlagen im Verzeichnis [`../styleguide/`](../styleguide/).

## Refill – wer füllt die Queue nach?

Das Nachfüllen ist **vollständig in den Scheduled Task integriert** (kein separater Agent mehr).

> Historisch hat der alte **OpenClaw-Agent** das Refill erledigt. OpenClaw ist abgeschaltet – die Logik lebt jetzt komplett im Abacus-Scheduled-Task.

Bei **jedem Lauf**:

- **Bereinigung:** Einträge mit `status: "completed"` oder `status: "skipped_duplicate"` werden aus `topics.json` entfernt.
- **Automatisches Nachfüllen:** Sinkt die Anzahl der `pending`-Themen **unter 4**, recherchiert der Task eigenständig neue KI-/Tech-Trends und füllt die Queue auf **mindestens 6** Themen auf (inkl. Duplikatprüfung + Schema-Validierung).
- **Protokoll:** `meta.lastRefill` wird auf den aktuellen Zeitpunkt gesetzt; die aktualisierte Datei wird nach `main` gepusht.

## Schema eines Themen-Objekts

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | String | Slug des Artikels (wird zum Verzeichnisnamen unter `content/blog/`) |
| `title` | String | Artikel-Titel |
| `keywords` | String[] | SEO-Keywords |
| `tags` | String[] | Blog-Tags |
| `wordCountTarget` | Number | Ziel-Wortanzahl |
| `angle` | String | Inhaltlicher Blickwinkel / Aufhänger |
| `researchFocus` | String[] | Recherche-Schwerpunkte für die Artikelerstellung |
| `status` | String | `pending` \| `completed` \| `skipped_duplicate` |

**Optionale Felder** (werden vom Task gesetzt):

- Bei `completed`: `completedAt` (ISO-Zeitstempel), `commit` (Commit-Hash)
- Bei `skipped_duplicate`: `skippedReason` (Begründung), `skippedAt` (ISO-Zeitstempel)

## Meta-Objekt

```json
"meta": {
  "version": "1.2",
  "created": "2026-05-29",
  "description": "Themen-Queue für automatische Blog-Artikel-Generierung",
  "schedule": {
    "frequency": "2x weekly",
    "days": ["Tuesday", "Friday"],
    "time": "09:00",
    "timezone": "Europe/Berlin"
  },
  "lastRefill": "2026-09-11T07:06:17.741029+00:00"
}
```

## Beispiel – ein Themen-Objekt

```json
{
  "id": "multi-agent-systeme-produktion-2026",
  "title": "Multi-Agent-Systeme 2026: Wenn ACP und A2A die KI-Automatisierung neu verschalten",
  "keywords": [
    "Multi-Agent System",
    "ACP Agent Communication Protocol",
    "A2A Protocol",
    "Agent Orchestration 2026",
    "MCP Multi-Agent"
  ],
  "tags": ["Multi-Agent", "Agent Orchestration", "MCP", "Automatisierung"],
  "wordCountTarget": 1000,
  "angle": "Warum 2026 das Jahr der Multi-Agent-Systeme in Produktion wird — Architektur-Vergleich (MCP, ACP, A2A), praktische Patterns und Fallstricke.",
  "researchFocus": [
    "Multi-Agent Orchestration 2026",
    "ACP vs A2A vs MCP Vergleich",
    "Agent Mesh Architecture Patterns"
  ],
  "status": "pending"
}
```
