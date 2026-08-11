# Content-Metadata-Schema

Dieses Schema erfüllt die Transparenz- und Kennzeichnungspflichten gemäß **Art. 50 EU AI Act** (gültig ab 2. August 2026) für KI-generierte oder KI-unterstützte Inhalte auf `future-pulse.de`.

Alle Blog-Posts unter `content/blog/**/index.md` tragen die folgenden vier Felder im YAML-Frontmatter. Pflichtfelder (Stand August 2026):

| Feld | Typ | Werte | Zweck |
|---|---|---|---|
| `ai_generated` | bool | `true` / `false` | Kennzeichnet, ob der Beitrag vollständig oder in wesentlichen Teilen KI-gestützt erstellt wurde. `false` nur, wenn der Beitrag von Hand und ohne KI-Hilfe geschrieben wurde. |
| `ai_model` | string | z.B. `minimax-m3:cloud`, `kimi-k2.5:cloud`, `human-only` | Name + Version des Modells, das für Recherche, Gliederung oder Textgenerierung eingesetzt wurde. Bei `ai_generated: false`: `human-only`. |
| `human_reviewer` | string | `Oliver Laudan` / anderer Name | Person, die den Beitrag redaktionell geprüft, Fakten gegengeprüft und freigegeben hat. |
| `review_date` | date | `YYYY-MM-DD` | Datum der letzten redaktionellen Prüfung. Bei Aktualisierungen mit neuem Review wird das Datum aktualisiert (zusammen mit `human_reviewer`). |

Wahlfelder (optional, abhängig vom Beitrag):

| Feld | Typ | Zweck |
|---|---|---|
| `human_research` | bool | `true`, wenn die Recherche (Quellen, Studien, Daten) von Hand gemacht wurde und die KI nur beim Schreiben half. Erlaubt differenziertere Aussagen als pauschales `ai_generated`. |
| `human_edit` | bool | `true`, wenn der Beitrag komplett KI-entworfen, aber von Hand überarbeitet wurde (Paraphrasen, Struktur, Gegenargumente). Häufige Variante. |
| `c2pa_image` | bool | `true`, wenn Bilder im Beitrag C2PA-Manifest-Metadaten tragen (Proof-of-Origin). Aktuell noch nicht gepflegt. |

## Beispiele

Vollständig von Hand geschrieben (selten bei Blogposts, aber möglich bei Gastbeiträgen oder persönlichen Notizen):

```yaml
---
ai_generated: false
ai_model: human-only
human_reviewer: Oliver Laudan
review_date: 2026-08-11
---
```

KI-gestützt, von Hand redaktionell geprüft (typischer future-pulse-Beitrag):

```yaml
---
ai_generated: true
ai_model: minimax-m3:cloud
human_reviewer: Oliver Laudan
review_date: 2026-08-11
---
```

## Pflegeprozess

1. Jeder neue Beitrag enthält die vier Pflichtfelder bereits im Entwurf. Der `blog-writer`-Cron-Prompt erzeugt das Frontmatter seit 2026-08-11 automatisch korrekt.
2. Bei Aktualisierungen eines bestehenden Beitrags: `review_date` wird auf das Datum der letzten manuellen Prüfung gesetzt, `human_reviewer` ggf. aktualisiert.
3. Der Footer im Theme rendert die vier Felder automatisch am Ende jedes Beitrags, sodass Leser:innen die Kennzeichnung direkt sehen (Art. 50 Abs. 1).

## Backfill-Historie

| Datum | Beitrag | Aktion |
|---|---|---|
| 2026-08-11 | alle bestehenden Posts | Bulk-Backfill mit `ai_generated: true` + aktuellstem Modell + `human_reviewer: Oliver Laudan` + `review_date: 2026-08-11`. |

## Referenz

- EU AI Act, **Art. 50** — Pflichten zur Kennzeichnung von KI-generierten Inhalten
- EU AI Act, **Art. 50 Abs. 4** — technische Dokumentation / Nachvollziehbarkeit
- EU AI Act, **Art. 12** + **Anhang IV** — Aufbewahrungspflicht 6 Jahre
- Impressum & Datenschutz: siehe `/impressum/` und `/datenschutz/` auf der Live-Site
- AI-Policy: siehe `/ki-policy/` auf der Live-Site
