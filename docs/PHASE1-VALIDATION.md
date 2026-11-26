# Phase 1: Wartungsänderungen und Abnahme

## Analyse und Umfang
GitHub `origin/main` ist die Basis. Bestehende Regeln wurden in `styleguide/`,
`SEO-RULES.md`, `blog-automation/`, `docs/CONTENT-METADATA.md` und
`docs/NEO-PUBLISHING-GUARDRAILS.md` abgeglichen. Der PR ergänzt die vorhandene
PR-Validierung, nicht den Pages-Deploymentworkflow. Keine Artikeldatei und
kein bestehender Review-Nachweis wird verändert.

- Explizite YAML-Booleans `ShowToc: true` und `TocOpen: true` für alle
  neuen/geänderten Blog-Dateien im kumulativen PR-Diff.
- Bisherige sieben Review-Gates, unabhängige Kennungen, Datum, Quellen und
  exakter SHA-256 bleiben unverändert verpflichtend.
- Hugo-Permalinkmanifest statt aus Dateinamen erratener URLs.
- HTML-Prüfung auf offenes ToC, nichtleere Sprunglinks und eindeutige
  Überschriftenziele; dynamische `article.entry-link`-Einträge statt
  beliebiger statischer Links. Paginierte Startseiten werden mitgeprüft.
- Produktion ohne Drafts sowie isolierter Preview-Build mit Drafts und
  zukünftigen Artikeln. Preview wird niemals hochgeladen oder deployt.
- Historische unveränderte Beiträge bleiben bei `--base` ausgenommen.
  Ein Vollscan ohne Basis ist bewusst strenger und meldet Altlasten.

## Reproduzierbare Prüfung
```sh
export HUGO_ENVIRONMENT=production TZ=Europe/Berlin HUGO_CACHEDIR=/tmp/future-pulse-hugo-cache
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/validate-blog-frontmatter.py --base origin/main
hugo --gc --minify --baseURL https://future-pulse.de/
python3 scripts/validate-rendered-blog.py --base origin/main
hugo --buildDrafts --buildFuture --destination preview --minify --baseURL https://future-pulse.de/
python3 scripts/validate-rendered-blog.py --preview --site preview --base origin/main
git diff --check
```

Die synthetischen Tests sind keine Artikel und keine redaktionellen Freigaben.
Der Hugo-Integrationstest erzeugt Artikel ausschließlich im temporären Verzeichnis.
In diesem Wartungs-PR sind null Artikel geändert; deshalb erwarten die
diff-basierten Artikelprüfungen null Kandidaten. Die Integrationstests decken
zusätzlich einen tatsächlich gerenderten Testartikel und einen negativen
Startseitenfall ab.

## Lokales Prüfergebnis (26.11.2026)

20/20 automatisierte Tests bestanden, einschließlich echter Hugo-Integration und
Negativtests für `headless`, `build.list: never` sowie getrennte offene/leere und
geschlossene/verlinkte ToCs sowie ein fremdes ToC außerhalb von `article.post-single`. ToC und Überschriften werden ausschließlich im Artikelcontainer geprüft. Produktions- und Preview-Build mit Hugo 0.146.0
Extended erfolgreich; Metadaten- und Render-Gates gegen frisch geholtes
`origin/main` erfolgreich (0 geänderte Artikel, daher kein redaktioneller
Freigabenachweis). `git diff --check` erfolgreich. Der unabhängige technische
Review einschließlich Nachprüfung steht in `PHASE1-TECHNICAL-REVIEW.md`.
GitHub-CI ist gesondert am PR zu prüfen.

## Auswirkungen und offene Abnahmefragen
Neue oder bearbeitete Artikel mit geschlossenem/fehlendem ToC oder fehlender
dynamischer Listenaufnahme werden künftig abgewiesen. Auch
`hiddenInHomeList` ist keine Ausnahme. Der zusätzliche Preview-Build erhöht
CI-Laufzeit, ändert aber weder Site-Konfiguration noch Produktion.
Vollscans melden vorhandene historische Metadaten-/ToC-Abweichungen; diese
sind keine Ermächtigung zum Backfill oder zur Neuausstellung von Reviews.

Abacus ist gemäß Betriebsfestlegung deaktiviert und nur historische Referenz.
Externe Scheduler-/Abacus-Einstellungen wurden in diesem Repository-Auftrag
nicht inspiziert oder geändert; die Dokumentation ist kein Abschaltnachweis.
Die Aktivierung eines späteren Produktionsplans sowie Merge und Publikation
bedürfen gesonderter Freigabe. Rulesets bleiben unverändert.
