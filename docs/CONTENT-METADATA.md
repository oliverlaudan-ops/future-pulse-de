# Content-Metadata-Schema

Dieses Schema erfüllt die Transparenz- und Kennzeichnungspflichten gemäß **Art. 50 EU AI Act** (gültig ab 2. August 2026) für KI-generierte oder KI-unterstützte Inhalte auf `future-pulse.de`.

Alle Blog-Posts unter `content/blog/**/index.md` kennzeichnen die tatsächliche Erstellung und Prüfung im YAML-Frontmatter. Historische menschliche Reviews bleiben unverändert; neue KI-Reviews werden separat ausgewiesen:

| Feld | Typ | Werte | Zweck |
|---|---|---|---|
| `ai_generated` | bool | `true` / `false` | Kennzeichnet, ob der Beitrag vollständig oder in wesentlichen Teilen KI-gestützt erstellt wurde. `false` nur, wenn der Beitrag von Hand und ohne KI-Hilfe geschrieben wurde. |
| `ai_model` | string | z.B. `minimax-m3:cloud`, `kimi-k2.5:cloud`, `human-only` | Name + Version des Modells, das für Recherche, Gliederung oder Textgenerierung eingesetzt wurde. Bei `ai_generated: false`: `human-only`. |
| `human_reviewer` | string | Name oder leer | Nur eine tatsächlich erfolgte menschliche Prüfung. Bei reinem KI-Review leer lassen. |
| `ai_reviewer` | string | z. B. `openai/gpt-6-sol` | Identität des unabhängigen KI-Reviewers, falls eingesetzt. |
| `ai_review_status` | string | `passed`, `failed`, `pending`, `passed_draft_only` | Ergebnis der KI-Prüfung; nur `passed` erlaubt die KI-basierte Publikationsfreigabe. |
| `review_date` | date | `YYYY-MM-DD` oder leer | Datum der tatsächlich abgeschlossenen menschlichen oder KI-Prüfung. |

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

## KI-Schlussprüfung und Publikationsgate (Beschluss vom 23.11.2026)

Eine dokumentierte, unabhängige KI-Schlussprüfung reicht für reguläre neue Future-Pulse-Artikel aus; eine zusätzliche menschliche Freigabe ist nicht erforderlich. Der Writer darf nicht sein eigener finaler Reviewer sein. Eine Freigabe erfordert überprüfte Primärquellen, korrekte Tatsachen, verständlichen deutschen Text, SEO- und Duplikatprüfung, gültige interne Links, vollständige Metadaten und einen erfolgreichen Hugo-Build. Der Reviewer muss `ai_review_status: passed` nach Abschluss aller Gates ausdrücklich bestätigen; bei ungeklärten oder kritischen Befunden gilt `failed` bzw. `pending`, und es darf kein Merge stattfinden. Maximal zwei redaktionelle Korrekturrunden. Alle Prüfergebnisse müssen im PR nachvollziehbar dokumentiert sein. Für jeden zur Veröffentlichung vorgesehenen KI-geprüften Beitrag (`draft: false`) muss eine maschinenlesbare Prüfnachweisdatei `reviews/<slug>.json` vorliegen. Sie enthält den SHA-256-Hash der **exakten Artikelfassung**, Writer- und unabhängige Reviewer-Kennung, Prüfdatum, Quellen-URLs, ausführliche Befunde und bestandene Gates (`primary_sources`, `factual_accuracy`, `seo`, `duplicate_check`, `internal_links`, `metadata`, `readability`). Die CI vergleicht diese Angaben und führt zusätzlich den Hugo-Build aus. Eine Textänderung nach dem Review macht den Hash ungültig und erfordert eine neue Prüfung. **Einschränkung:** Die CI kann die Konsistenz des Nachweises prüfen, aber nicht kryptografisch beweisen, welcher Agent den Bericht tatsächlich erstellt hat oder ob Quellen inhaltlich korrekt beurteilt wurden. NEO darf diese Nachweise nicht selbst fälschen oder Reviewer-Aufgaben übernehmen.

Ein erfolgreicher Draft-Test (`passed_draft_only`) ist **keine** Publikationsfreigabe. Der Veröffentlichungsworkflow erfolgt über einen eigenen Branch und Pull Request. Der Merge nach `main` ist erst nach allen Gates und innerhalb des freigegebenen Veröffentlichungsplans erlaubt. Keine Admin-Bypässe oder Force-Pushes. Bestehende Inhalte und fremde Projekte bleiben außerhalb des automatisierten Schreibbereichs. `human_reviewer` darf niemals einen KI-Agenten oder einen nicht beteiligten Menschen nennen.

Beispiel für einen nach allen Gates KI-geprüften Beitrag:

```yaml
ai_generated: true
ai_model: "openai/gpt-6-luna"
human_reviewer: ""
ai_reviewer: "openai/gpt-6-sol"
ai_review_status: passed
review_date: 2026-11-23
```

## Pflegeprozess

1. Jeder neue Beitrag enthält `ai_generated`, `ai_model`, `human_reviewer`, `ai_reviewer`, `ai_review_status` und `review_date` bereits im Entwurf. Ein Review-Datum wird erst nach abgeschlossener Prüfung gesetzt.
2. Bei Aktualisierungen bestehender Beiträge werden nur tatsächlich erfolgte Reviews mit korrektem Reviewer-Typ und Datum dokumentiert. Historische Felder werden nicht rückwirkend umgedeutet.
3. Der Footer und RSS unterscheiden ausdrücklich menschliche und KI-Prüfung; ein fehlendes Review wird nicht als bestanden ausgegeben.

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
