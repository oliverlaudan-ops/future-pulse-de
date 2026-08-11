# EU AI Act — Compliance Log (Anhang IV Vertiefung)

Dieses Dokument vertieft die in `/ki-policy/` und `docs/CONTENT-METADATA.md`
bereits öffentlich gemachten Angaben. Es erfüllt die Pflicht zur
technischen Dokumentation gemäß **Art. 12 EU AI Act** in Verbindung mit
**Anhang IV** und richtet sich in erster Linie an Aufsichtsbehörden
(Bundesnetzagentur) im Rahmen einer möglichen Audit-Anfrage.

Vertraulich, intern — wird im Repository mitgeführt, ist aber nicht
offen auf der Site verlinkt. Wer hier schaut, weiß, wonach er sucht.

Letzte Aktualisierung: **2026-08-11** durch J.A.R.V.I.S. auf Geheiß
von Oliver Laudan.

---

## 1. Systemcharakterisierung

| Punkt | Wert |
|---|---|
| Anbieter / Verantwortlicher | Oliver Laudan (Einzelperson), future-pulse.de, kontakt@future-pulse.de |
| Systemname | `future-pulse-de-publication` |
| Systemtyp | Inhalte-Erstellung mit KI-Unterstützung (Limited-Risk gem. Art. 50 EU AI Act) |
| Hauptaufgabe | Veröffentlichung deutscher, deutschsprachiger Tech-/KI-Blogartikel |
| Hochrisiko-Klassifikation gem. Anhang III | **nein** |
| Verbotene Praxis gem. Art. 5 | **nein** |
| Rollenbegriff gem. Art. 3 | Anbieter und Betreiber gleichzeitig (Ein-Personen-Blog) |
| Klassifikation gem. Art. 50 | unter „limited risk" mit Kennzeichnungspflicht |

---

## 2. Datenflüsse

```
           ┌──────────────────┐
           │ Quellen          │
           │ - Web-Recherche  │
           │ - Lese-/Hörnotizen│
           │ - Diskussionen   │
           └────────┬─────────┘
                    │  (manuell + KI-Recherche-Unterstützung)
                    ▼
           ┌──────────────────┐
           │ KI-Modell        │
           │ (Ollama Cloud,   │
           │  primär minimax-  │
           │  m3:cloud)       │
           └────────┬─────────┘
                    │  Rohtext (deutsch)
                    ▼
           ┌──────────────────┐
           │ Redaktions-      │
           │ pipeline         │
           │ - Fakt-Check     │
           │ - Gegenrecherche │
           │ - Überarbeitung  │
           │ - Genehmigung    │
           └────────┬─────────┘
                    │  Endtext + 4-Felder-Frontmatter
                    ▼
           ┌──────────────────┐
           │ Git / GitHub     │
           │ (PR-Review-Flow, │
           │  Force-Push auf  │
           │  main blockiert) │
           └────────┬─────────┘
                    │  Hugo-Build (CI)
                    ▼
           ┌──────────────────┐
           │ GitHub Pages /   │
           │ future-pulse.de  │
           └──────────────────┘
```

**Eingaben** (in das System):

- Manuell verfasste Gliederungen und Stoffsammlungen
- Rechercheergebnisse aus Websuche und Fachliteratur
- KI-generierte Textvorschläge aus Ollama-Cloud-Modellen (hauptsächlich `minimax-m3:cloud`)

**Ausgaben** (aus dem System):

- Hugo-Beiträge mit Frontmatter + Markdown-Body
- Statisches HTML auf `future-pulse.de`
- RSS-Feed mit Disclosure-Items (siehe `layouts/rss.xml`)
- PNG- / JPG-Cover-Bilder, referenziert aus externen CDNs (Leonardo.ai, SeeDream) oder Eigenbestand

**Trainingsdaten**: Wir trainieren keine eigenen Modelle auf Nutzereingaben. Die in den Posts enthaltenen Schreibanregungen werden *nicht* zum Training benutzt; Eingaben in Ollama-Cloud-Modelle gehen an deren Backend (Provider-Verantwortung, dokumentiert auf deren AI-Act-Compliance-Seiten).

---

## 3. Modell-Registratur

| Modell | Anbieter | Anwendungsbereich | EU-Repräsentation | Eingeführt |
|---|---|---|---|---|
| `minimax-m3:cloud` | MiniMax (Ollama Cloud) | Recherche-Unterstützung, Gliederung, Rohtext-Generierung | Provider-Compliance gem. EU AI Act | 2025-06-01 |
| `kimi-k2.5:cloud` | Moonshot (Ollama Cloud) | Fallback-Modell für Englisch-/Vergleichs-Runs | Provider-Compliance | 2025-10-12 |
| `kimi-k2.7-code:cloud` | Moonshot (Ollama Cloud) | Coding-Agent (`/opt/agent-genesis`, codeline-intern) — nicht im Blog-Output | Provider-Compliance | 2026-01-04 |

Modellwechsel werden in dieser Tabelle mit Datum dokumentiert. Abkündigungen dokumentieren wir 30 Tage vor Wirksamkeit mit Review-Anlass.

**Auditierbarkeit pro Beitrag**: das Frontmatter-Feld `ai_model` zeigt exakt, welches Modell für den jeweiligen Beitrag eingesetzt wurde. Eine globale Auswertung („wie viele Beiträge wurden mit Modell X erstellt?") ist per `grep` möglich:

```bash
grep -l '^ai_model: *"minimax-m3:cloud"$' content/blog/*/index.md | wc -l
```

---

## 4. Kennzeichnungssystem (Art. 50)

Drei-Schicht-Disclosure:

1. **Pro Beitrag**: automatisches Box-Element via `layouts/partials/ki-disclosure.html` (eingebunden über `extend_post_content.html`), gefüttert aus den 4 Frontmatter-Feldern.
2. **Im Feed**: `layouts/rss.xml` prependet jeder Description einen `[KI-generiert / Manuell erstellt]`-Tag und pinnt einen Channel-weiten Disclaimer-Item.
3. **Site-weit**: `content/ki-policy.md` als zentrale Selbstdokumentation, verlinkt aus dem Hauptmenü, aus dem Footer jedes Artikels und aus dem RSS-Channel-Item.

Stichproben-Tests werden jeden Ersten des Monats via Cron ausgeführt — siehe `/opt/openclaw/monitor/ai-act-monthly-check.sh` (separater Service, folgt mit diesem PR).

---

## 5. Aufbewahrungssystem (Art. 12 + Anhang IV)

**Aufbewahrungsfrist: 6 Jahre** ab Veröffentlichungsdatum jedes Beitrags.

| Artefakt | Speicherort | Aufbewahrungsdauer | Sicherheitsmechanismus |
|---|---|---|---|
| Hugo-Quelldateien (inkl. Frontmatter + Modellname) | GitHub: `oliverlaudan-ops/future-pulse-de` | unbefristet (durch Branch-Protection) | Force-Push auf `main` blockiert; PR-Review via 2-Augen-Prinzip |
| GitHub Actions Build- und Deploy-Logs | GitHub Actions, `pages` Workflow | bis zu 90 Tage Standard, 1 Jahr mit Retentions-Add-On (kostenpflichtig) | SHA-Pin auf `actions/checkout@v4` + `peaceiris/actions-hugo@v3` für Reproduzierbarkeit |
| Git-Commit-History | GitHub + lokaler Mirror `~/projects/future-pulse-de/` | unbefristet | SHA-Chain verifizierbar |
| Bild-Asset-Manifest | `static/image-manifest.json` (committed) | unbefristet | deterministische Hash-Bildung; Schema-Versionsfelder |
| Redaktionelle Korrektur-Mails | E-Mail-Archiv (IMAP-Backup + Passwort-Manager) | bis zu 10 Jahre | Korrektur-E-Mails werden in einen `corrections/YYYY/`-Ordner gespiegelt |
| Jahres-Snapshot (verschlüsselt) | `~/Documents/archive/future-pulse/<jahr>-snapshot.tar.gz.enc` | unbefristet | AES-256, GnuPG symmetric, Passphrase nur offline im Passwort-Manager |

**Auf Anfrage einer Aufsichtsbehörde**:

1. Aktueller GitHub-Repo-ZIP + Git-History als Bundle (`git bundle create compliance-$(date).bundle --all`).
2. Export des `image-manifest.json` mit Zeitstempel.
3. Snapshot-Datei des laufenden Jahrs + Vorjahre (Passphrase wird separat übergeben).
4. Aktuelle Version von `content/ki-policy.md` und `docs/CONTENT-METADATA.md` mit Build-Log.

Lieferung des Audit-Bundles erfolgt innerhalb von 30 Tagen (gesetzliche Frist gem. Art. 21 Abs. 5 für vergleichbare Auskunftsverfahren).

---

## 6. Menschliche Aufsicht (Art. 14)

Wir sind Limited-Risk — Art. 14 (menschliche Aufsicht) ist nur für Hochrisiko-Systeme strikt. Trotzdem wenden wir äquivalente Praktiken an:

- **Pre-Publish**: jeder Beitrag wird von Oliver Laudan persönlich inhaltlich gegenrecherchiert, Fakten gegengeprüft, KI-typische Stilblüten geglättet.
- **Post-Publish**: Kontaktweg über `kontakt@future-pulse.de`, LinkedIn oder direkt in den Kommentaren. Beanstandungen werden im Git-Repo dokumentiert (`git log`, Commit-Message mit `Korrektur:`-Prefix).
- **Modell-Lockdown**: bei systematischen Fehlern in einem Modell wird das Modell für 30 Tage vom Blog ausgesetzt; der Befund wird im Modell-Registratur dokumentiert.

---

## 7. Accountability & Meldewege

- Datenschutz-Vorfälle (Art. 26): über die bekannten DSGVO-Wege (`kontakt@future-pulse.de`, Bundesnetzagentur).
- Modell-Diskriminierungs- oder Schadensfälle: direkte Meldung an den Provider (Ollama Cloud Compliance-Form) + ggf. an die zuständige nationale Behörde.
- Interne Eskalation: jeder vom Menschen erkannte KI-Fehler wird im gleichen Commit korrigiert, in dem der Beitrag selbst korrigiert wird — beide Commit-Messages verlinken aufeinander.

---

## 8. Risiko-Assessment

| Risiko | Eintrittswahrscheinlichkeit | Mitigation |
|---|---|---|
| KI-Halluzination (faktisch falsche Aussage) | mittel | Post-Publish-Review + öffentliche Korrektur-Pflicht auf LinkedIn/Kommentaren |
| Bielastisches Bias durch Modell-Auswahl | gering | Modell-Wechsel dokumentiert; manuelles Sampling gegenprüft |
| DSGVO-Verstoß durch Drittinhalte | gering | Bild-Manifest maschinenlesbar; Stockfotos nur von Lizenzpartnern mit DSGVO-konformer Datenquelle |
| C2PA-Insuffizienz (Bild-Provenance nicht maschinenlesbar) | real | dokumentiert in `/ki-policy` §2; Image-Manifest als ehrliche Übergangslösung |
| Compliance-Drift bei Modell-Wechsel | mittel | Modell-Registratur (Abschnitt 3) + monatlicher Cron-Check |

---

## 9. Änderungshistorie

| Datum | Version | Änderung |
|---|---|---|
| 2026-08-11 | 1.0.0 | Erstausgabe im Zuge der PR #11 + #12 Compliance-Pushs |
