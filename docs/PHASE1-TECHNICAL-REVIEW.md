# Phase 1 – unabhängiger technischer Nachreview

**Stand:** 26.11.2026. **Basis:** `origin/main` gegen den aktuellen uncommitted Arbeitsstand in `/root/projects/future-pulse-phase1`, einschließlich neuer Dateien. **Urteil:** Die technischen Findings des vorigen Nachreviews sind behoben. Aus technischer Sicht **Freigabe zur Vorbereitung einer Wartungs-PR**, ausdrücklich **keine Merge-, Deployment-, Artikel- oder Publikationsfreigabe**. In diesem Review wurde ausschließlich dieses Dokument geändert; kein Commit, Push oder PR.

## Nachprüfung der Findings

| Befund | Ergebnis |
|---|---|
| Manifest-Fail-open bei `headless` und `build.list: never` | Behoben: ausgewählte Markdown-Pfade müssen in `hugo list all` als `blog`/`page` erscheinen. Die Negativtests bestehen. Zusätzlich wurde ein `headless`-Artikel in einem temporären Git-Repository über den tatsächlichen `--base`-PR-Diff geprüft: Exit 1 mit `missing from Hugo all manifest`. |
| Offenes ToC mit eigenen Sprunglinks | Behoben: Links werden nur aus offenen `details.toc` gesammelt; ein offenes leeres ToC kann nicht durch ein geschlossenes verlinktes ToC kaschiert werden. Negativtest besteht. |
| Fremdes ToC / Überschriften außerhalb des Artikels | Behoben: Parser begrenzt ToC und Überschriften auf `article.post-single`. `test_foreign_toc_rejected` weist ein fremdes ToC und HTML ohne Artikelcontainer zurück. Die aktuelle `single.html`-Vorlage rendert das reguläre ToC im Artikel. |
| Build-/Validator-Umgebung | Behoben: Beide Hugo-Builds **und** beide Render-Validator-Schritte in `.github/workflows/pr-validation.yml` setzen `HUGO_ENVIRONMENT=production`, `TZ=Europe/Berlin` und `HUGO_CACHEDIR`. |
| MCP-Keywords | Behoben: Der sechste Reserveeintrag verwendet nun `MCP Sicherheit`, `MCP Autorisierung` und `MCP Token-Sicherheit`, passend zu Titel, Recherchefokus und Themenstrategie. |
| Abacus-Dokumentation | `THEMENSTRATEGIE.md` und `PHASE1-VALIDATION.md` unterscheiden Betriebsfestlegung und nicht geprüften externen Zustand. Die übrigen Betriebsdokumente formulieren die Deaktivierung kategorisch; das ist eine Vorgabe, **kein** unabhängiger Nachweis der externen Task-Konfiguration. |

## Gesamtdiff und Checks

- Geprüft wurden Workflow, beide Validatoren, Tests, Themenreserve, Betriebs-/Strategie-/Validierungsdokumente sowie README, SEO- und Styleguide-Änderungen gegen `origin/main`. Keine neuen technischen Blocker gefunden. Bestehende Artikel und Review-Nachweise bleiben unverändert.
- `python3 -m unittest discover -s tests -p 'test_*.py' -v`: **20/20 bestanden**, einschließlich Hugo-Integration und Negativfällen. Hugo **v0.146.0 extended**.
- `python3 -m json.tool blog-automation/topics.json`, `git diff --check origin/main` und Frontmatter-Gate gegen `origin/main`: bestanden.
- Produktionsbuild und isolierter Preview-Build: Exit 0, jeweils **464 Seiten und 22 Paginator-Seiten**. Beide Render-Gates: Exit 0. Die diff-basierten Artikel-Gates fanden **0 geänderte Blogartikel**; daher ist dies kein End-to-End-Nachweis eines realen PR-Artikels.
- Zusätzlich temporärer PR-Diff-Negativtest für einen `headless`-Artikel: erwartete Ablehnung bestätigt. Dieses Test-Repository lag außerhalb des Arbeitsbaums.
- GitHub-CI am künftigen PR, redaktioneller Review sowie externe Abacus-/Scheduler-Einstellungen wurden nicht geprüft. Preview wird nicht hochgeladen; aus dem lokalen Build folgt keine Produktionsfreigabe.

**Empfehlung:** Wartungs-PR kann zur CI- und Betreiberprüfung vorbereitet werden. Vor jedem Merge die GitHub-CI und die organisatorischen Freigaben gesondert prüfen; Phase 1 autorisiert weder Merge noch Veröffentlichung.
