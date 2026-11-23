# Reviewgate: technischer Test 23.11.2026

Ausgangspunkt: PR #18, Head 865489b52d2661f58ca0223a07581d38a2f4f705.

Lokale Befehle:

- `python3 -m unittest discover -s tests -v`: 13 Tests bestanden.
- `python3 scripts/validate-blog-frontmatter.py --base origin/main`: ein echter Artikel mit vorhandenem unabhängigen Draft-Nachweis bestanden.
- `git diff --check`: bestanden.
- `hugo --destination /tmp/future-pulse-validator-hugo --buildDrafts --noBuildLock`: Exit 0, 464 Seiten, Hugo 0.146.0 extended.

| Fall | Erwartung und Ergebnis |
|---|---|
| Fehlender Bericht, auch Draft | FAIL |
| Ungültiges JSON / JSON-Liste / falscher Hash | FAIL |
| Vollständiger hashgebundener Bericht | PASS |
| Artikel nach Review verändert | FAIL |
| Writer und Reviewer identisch (auch Großschreibung/Leerraum) | FAIL |
| Fehlender Reviewer trotz human_reviewer | FAIL |
| Fehlendes Hugo-draft-Feld | Keine Ausnahme |
| Nicht-Draft mit passendem passed-Bericht und Datum | PASS |
| Offenes Gate / ungültiges Datum | FAIL |
| Bericht in separatem Folgecommit | Zunächst FAIL, danach PASS |
| Anschließender Commit entfernt alle KI-Metadaten | FAIL |

Die Testberichte sind synthetische Fixtures und keine echten Freigaben. Die Artikeldatei und ihr vorhandener realer Draft-Bericht wurden nicht verändert. Ein Code-Reviewer (openai/gpt-6-sol) identifizierte die Herkunftsflag-Umgehung und Bundle-Namenskollision; beides wurde korrigiert. Keine kryptografische Identitätsprüfung wird behauptet. Die nach dem Push beobachteten Actions-Ergebnisse sind separat im Abschlussbericht aufgeführt.

Keine Veröffentlichung: Draft-PASS bleibt von Publikations-PASS getrennt. Keine Ruleset-/Berechtigungsänderungen; ohne aktivierte Required Checks erzwingt dieser Workflow allein kein GitHub-Mergeverbot.
