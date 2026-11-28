> Historischer Befund / Legacy-Guard. Durch die Offline-Runner-Implementierung teilweise superseded; aktueller Stand und verbleibende Produktionsblocker: [NEO-CONTROLLED-RUNNER.md](NEO-CONTROLLED-RUNNER.md). Die damaligen Befunde bleiben als Historie erhalten. Matrix ist kein geplanter Kanal mehr.

# Abschlussprüfung Implementierungsetappe 1 – PR #21

Stand 28.11.2026. Geprüfter Implementierungscommit: `f645d395cc511165f69523aa326e1c56a5702e7f`.
Die nachfolgenden Dokumentationsänderungen ändern keinen ausführbaren Code.

## Urteil

**Nicht bereit zur abschließenden Merge-Freigabe gegen die angeforderten Sicherheitskriterien.**
Als vorbereitender lokaler Admission-Guard ist der Code brauchbar; die vollständige
Sicherheitsimplementierung der angefragten Etappe ist damit nicht nachgewiesen.
Eine dokumentierte spätere Integrationspflicht ist kein implementierter Mechanismus.
Die positive vorherige Änderungsprüfung betraf Zeitfenster/Warnung und vorhandene Tests,
nicht die vollständige Absicherung des gesamten Redaktionsprozesses.

Prüfgrundlage: aktueller PR-Diff, Guard, Tests, NEO-CRON-RUNTIME-GUARD.md,
NEO-PUBLISHING-GUARDRAILS.md und die ausdrücklich im Abschlussauftrag genannten Kriterien.
Der vollständige Wortlaut eines separaten ursprünglichen Implementierungsauftrags
konnte über die verfügbare Erinnerung/Sessionsuche nicht vollständig rekonstruiert werden;
eine darüber hinausgehende lückenlose ursprüngliche Anforderungsliste wird nicht behauptet.
Schon die ausdrücklich benannten Kriterien verhindern eine positive Gesamtabnahme.

## Implementiert und getestet

- Persistentes SQLite-Journal mit Datum als Primärschlüssel, eindeutiger Run-ID,
  WAL, synchronous=FULL und atomarem INSERT: gleicher Termin in derselben DB
  kann nicht zweimal beansprucht werden. Wiederöffnen der DB und sechs parallele
  Threads mit getrennten Verbindungen sind getestet.
- Di/Fr Europe/Berlin, erstmalige Zulassung [09:00:00,10:00:00), Winter-/Sommerzeit
  und Mikrosekundengrenzen; kein Claim nach Fensterschluss.
- Zustandsübergänge ohne erneute Zeitfensterprüfung, keine Guard-Gesamtlaufzeit,
  keine TTL-Löschung. Fortsetzung bis deployed auch sieben Tage später ist getestet.
- Ab 90 Minuten nicht blockierende Warnung für aktive Zustände; status/transition
  geben JSON und stderr bei Exitcode 0 aus. Warnschwelle und unveränderte Reservierung getestet.
- Verbotene/doppelte lokale Übergänge werden abgewiesen; blocked/deployed sind terminal.

Belege: scripts/editorial_run_guard.py, insbesondere slot_for, connect, claim,
transition, runtime_warnings und main; tests/test_editorial_run_guard.py.
Diese Aussagen gelten für den lokalen Guard, nicht für externe Publikation.

## Offene Mechanismen und notwendige Integrationsnachweise

1. **Exklusive Gesamtlaufsperre fehlt.** BEGIN IMMEDIATE endet nach INSERT/UPDATE,
   nicht nach dem Redaktionslauf. Zwei verschiedene Termine können gleichzeitig
   claimed bleiben. Keine laufübergreifende Ownership/Fencing-Instanz vorhanden.
2. **Prozessabbruch/Wiederanlauf nur teilweise abgedeckt.** Ein gespeicherter Claim
   bleibt nach normalem DB-Schließen bestehen; dies ist kein Kill-/Gateway-Neustart-Test.
   Crash vor/nach PR, Merge und Deployment sowie unklare externe Antworten fehlen.
   Menschliche Reconciliation ist dokumentiert, aber nicht ausführbar integriert.
3. **Keine GitHub-Reconciliation.** transition prüft lokale Zustandsfolge und
   nichtleere PR/SHA-Werte, nicht deren Echtheit, Zugehörigkeit oder externe Existenz.
   PR/SHA können beim Merge überschrieben werden. CI/Review/Head/Pages werden
   vom Guard weder abgefragt noch kryptografisch verifiziert.
4. **Keine externe Exactly-once-Garantie.** Einmaliger Claim und Verbot doppelter
   Journaleinträge verhindern allein weder einen zweiten externen Merge noch
   Wiederholung nach unklarer GitHub-Antwort. Idempotente externe Operationskette fehlt.
5. **Getrennte Umgebungen nicht koordiniert.** Derselbe Slot lässt sich in zwei
   separaten DB-Dateien erfolgreich claimen; --db/Umgebungsvariable erlauben das.
   Gemeinsamer autoritativer Zustand und verifizierte Runner-Identität fehlen.
   connect legt bei fehlender DB eine neue an; Verlust oder falsche Auswahl des
   Journals wird daher nicht als Recovery-Blocker erkannt.
   SQLite-WAL auf beliebigem Netzlaufwerk ist keine belegte verteilte Lösung.
6. **Kein technisch geschlossenes Produktionsgate.** Es gibt kein standardmäßig
   false gesetztes, vom Agenten nicht umgehbares Gate vor GitHub-Seiteneffekten.
   Guard ist nicht verpflichtend angebunden. Deaktivierter Cron, Draft-PR und
   Promptverbote sind keine ausreichende technische Durchsetzung bei manuellem
   Start oder alternativen Berechtigungen.
7. **Warnzustellung und 240-Minuten-Timeoutpfad fehlen im Runner.** Der Guard
   erzeugt Warnungen bei Aufruf; er plant keine selbsttätige 90-Minuten-Zustellung.
   Timeout-Reconciliation und Halten einer Gesamtlaufsperre müssen integriert werden.

Punkte 2–7 enthalten bewusst spätere Runner-Aufgaben; sie sind derzeit nicht
wirksam und dürfen nicht als vollständig implementiert/testbar abgenommen werden.
Insbesondere die fehlende Gesamtlaufsperre ist nicht nur eine Aufrufverdrahtung.

## Reproduzierte Gegenproben (nur temporäre Datenbanken)

- claim Freitag 27.11.2026 und Dienstag 01.12.2026 in derselben DB:
  **zwei aktive claimed-Einträge**.
- claim desselben Freitagsslots in zwei getrennten DB-Dateien:
  **beide erfolgreich**.
- pr_open mit PR 1/SHA abc, danach merged mit PR 999/SHA unverified und deployed:
  **lokal erfolgreich ohne GitHub-Aufruf**.

Dies demonstriert Implementierungsgrenzen, keine produktiven Aktionen.

## Testvollständigkeit

Unabhängiger Review bestätigt die nachstehenden Codebefunde sowie 28/28 Tests,
Frontmatter-Gate, Hugo-Produktions-/Preview-Build und beide Render-Validatoren.
Diff-basierte Artikelprüfungen fanden 0 geänderte Artikel; kein Publikationsnachweis.
Der Review bezog sich auf den Implementierungscommit f645d39, nicht auf die neue Doku.

28 Repository-Tests bestehen; davon **8 Guard-Tests**. Übrige Tests prüfen
Artikel-/Review-/Render-Gates, nicht die vollständige Redaktionsorchestrierung.
Vorhandene Tests decken Zeitgrenzen, lokale Persistenz/Parallelität, lokale
Zustandsfolge und Warnverhalten ab.

Für vollständige Sicherheitsabnahme fehlen mindestens:
- echte konkurrierende Prozesse und exklusive Gesamtlaufsperre über verschiedene Termine;
- getrennte Hosts/isolierte DBs: koordinierte Verweigerung statt Doppelzulassung;
- harter Prozessabbruch und Wiederanlauf vor/nach jedem externen Seiteneffekt;
- GitHub-Reconciliation mit bereits vorhandenem PR/Merge/Deployment und unklaren Antworten;
- Abweisung fehlender/falscher Produktionsfreigabe auch bei manuellem Start;
- Nachweis, dass alternative GitHub-Pfade die Gates nicht umgehen können;
- Timeout nach 240 Minuten: keine Sperrfreigabe/Neuzulassung/Ersatzpublikation;
- echte Warnzustellung bei lang wartenden Kindläufen/CI nach 90 Minuten.

Bestehende grüne CI ersetzt diese fehlenden Tests nicht.
240-Minuten-Konfiguration: siehe NEO-RUNTIME-TIMEOUT-AUDIT.md.

## Grenzen dieser Prüfung

Keine Codekorrekturen, Produktionskonfiguration, Cron-Prompt-Anwendung,
Cron-Aktivierung, Merge, Artikelpublikation oder Produktionsfreigabe.
Der PR bleibt Draft. Die offenen Sicherheitsanforderungen benötigen eine
separat autorisierte Implementierung und anschließende erneute Prüfung.
