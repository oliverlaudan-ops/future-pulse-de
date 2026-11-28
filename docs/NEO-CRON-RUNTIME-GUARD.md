# Future Pulse: technische Cron-Laufzeitsperre (Vorbereitung, nicht produktiv)

`scripts/editorial_run_guard.py` ist ein **fail-closed** Admission-Gate für die geplanten OpenClaw-Läufe. Der vorhandene Cron bleibt deaktiviert. Das Skript wird noch nicht von NEO oder GitHub Actions aufgerufen und erteilt keine Merge- oder Publikationsberechtigung.

## Zeit und Einmaligkeit

- Regulärer Start Dienstag/Freitag 09:00 Uhr; erstmalige Zulassung ab 09:00:00 einschließlich bis 10:00:00 ausschließlich, `Europe/Berlin`; kein Nachholen.
- `claim` erzeugt atomar einen einmaligen Datensatz pro lokalem Datum. SQLite `BEGIN IMMEDIATE`, eindeutiger Slot-Schlüssel, WAL und `synchronous=FULL` verhindern parallele oder wiederholte Claims.
- Das Startfenster wird ausschließlich bei `claim` geprüft. Ein gültig gestarteter Lauf darf nach 10:00 weiterarbeiten und bei erfüllten übrigen Freigabebedingungen veröffentlicht werden. Keine pauschale harte Gesamtlaufzeitbegrenzung im Guard.
- Ab 90 Minuten seit `claimed_at` liefern `status` und `transition` für aktive Läufe eine nicht blockierende Betriebswarnung (JSON `warnings`, zusätzlich stderr; Exitcode bleibt 0). Langsame Agenten, umfangreiche Recherche, zusätzliche Reviews und verzögerte CI/Deployments sind allein keine Abbruchgründe.
- Der Guard ist kein Hintergrunddienst: Der spätere kontrollierte Runner muss `status` regelmäßig und spätestens nach 90 Minuten aufrufen und Warnungen zustellen, auch während er auf Kinder/CI wartet. Diese Integration ist noch offen; hier wird kein Timer/Cron aktiviert. Wiederholte Warnungen darf der Runner anhand Run-ID und Warncode deduplizieren.
- Reservierungen haben keine TTL. Auch Tage später bleiben Claims verbraucht; Zeitablauf gibt weder eine exklusive Laufzeitsperre frei noch erlaubt er einen Ersatzartikel. Eine zusätzliche laufübergreifende exklusive Runner-Sperre ist weiterhin Integrationsvoraussetzung; SQLite-Sperren schützen nur atomare DB-Operationen.
- Eine unterbrochene Ausführung wird **nicht automatisch wieder aufgenommen**. Nach einem Crash muss ein Mensch anhand GitHub PR/Commit/Pages den Zustand abgleichen. Auch ein fehlgeschlagenes Deployment führt niemals zu einem zweiten Artikel.
- Zustandsfolge: `claimed → pr_open → merged → deployed`, optional `blocked`. Die Zustände sind **Journaleinträge**, keine Bestätigung der tatsächlichen GitHub-Ereignisse. Ein späterer Runner muss PR, Commit, CI, Review und Deployment unabhängig prüfen, bevor er den jeweiligen Übergang setzt.

## Bedienung (nur nach gesonderter Freigabe und Integration)

```bash
python3 scripts/editorial_run_guard.py claim
python3 scripts/editorial_run_guard.py status --run-id RUN_ID
python3 scripts/editorial_run_guard.py transition --run-id RUN_ID --to pr_open --pr-number 123 --commit-sha FULL_SHA
```

Datenbankstandard: `/root/.openclaw/state/future-pulse-runs.sqlite`, überschreibbar durch `FUTURE_PULSE_RUN_DB` oder `--db`. Der Zustand muss dauerhaft gespeichert, gesichert und ausschließlich durch den kontrollierten Runner verwaltet werden. Für Tests immer `--db` mit einem temporären Pfad verwenden.

## Noch ausstehende Integration und Sicherheitsgrenzen

1. Einen **nicht vom Agenten umgehbaren** Runner vor die Agenten- und GitHub-Aktionen schalten. Ein Prompt allein genügt nicht. Insbesondere darf der Agent weder den Gate-Code noch die DB verändern oder alternative GitHub-Zugänge zum Merge nutzen.
2. GitHub-Berechtigungen begrenzen; Merge nur nach serverseitiger Prüfung von PR-Head, Required Checks und vorhandenen Review-Gates. Der Status `merged` darf erst nach verifiziertem GitHub-Merge gesetzt werden.
3. Der Runner muss eindeutige Run-ID, Slot, PR und Commit über alle Schritte hinweg korrelieren. Crash-Reconciliation und Deployment-Verifikation müssen als eigenständige Schritte implementiert und getestet werden.
4. Integrationstest mit isoliertem OpenClaw-Cron, unabhängiger Reviewer-Prüfung, CI, GitHub Pages und Matrix-Zustellung.
5. Ausdrückliche menschliche Produktionsfreigabe. Bis dahin Cron deaktiviert, keine Artikelpublikation.

**Wichtig:** Das Gate verhindert doppelte *Claims*, nicht eigenständig doppelte GitHub-Merges durch andere Prozesse oder Berechtigungen. Die tatsächliche Durchsetzung erfordert die unter Punkt 1–3 genannte Integration.


## Notwendige Cron-Prompt-Änderung (nur dokumentiert, nicht angewendet)

Im bestehenden deaktivierten Cron „Future Pulse · Redaktion (gesperrt)“ ausschließlich den Absatz
`ZEIT UND IDEMPOTENZ` ersetzen. Alle anderen Absätze, insbesondere Produktionssperre,
Review-/CI-/Deployment-Nachweise und Betriebszustandsprüfung bleiben unverändert:

> ZEIT UND IDEMPOTENZ: Regulär Dienstag/Freitag 09:00 Europe/Berlin, maximal ein Artikel je regulärem Termin. Datum/Uhrzeit live feststellen; erstmalige Zulassung ausschließlich 09:00:00 einschließlich bis 10:00:00 ausschließlich, keine Nachholung außerhalb dieses Fensters. Das Startfenster gilt nur für die erstmalige Zulassung, nicht für Fortsetzung, Review, CI, Deployment oder Veröffentlichung eines ordnungsgemäß gestarteten Laufs. Ein solcher Lauf darf danach weiterarbeiten und bei erfüllten übrigen Freigabebedingungen veröffentlicht werden. Keine pauschale harte Gesamtlaufzeitbegrenzung durch den Editorial Run Guard; ab 90 Minuten Gesamtlaufzeit eine nicht blockierende Betriebswarnung ausgeben. Langsame Agenten, umfangreiche Recherche, zusätzliche Reviews und verzögerte CI-/Deployment-Prozesse allein sind keine Abbruchgründe. Wiederholten Termin und parallele Läufe anhand technisch erzwungener persistenter Termin-/Laufzustände und exklusiver Laufzeitsperre ausschließen. Exklusive Sperren niemals allein durch Zeitablauf freigeben. Fehlen diese Mechanismen oder ist ihr Zustand unklar, keine weiteren zustandsändernden Aktionen ausführen und sichere Reconciliation anhand Run-ID, PR, Commit, CI und Deployment durchführen; bei Prozessabbruch keine automatische Neuzulassung. Sprachmodellprüfungen ersetzen keine technischen Sperren. Neustarts dürfen keine Aktionen wiederholen; keine automatischen Ersatzveröffentlichungen, auch nicht bei Deploymentfehler.

`schedule` bleibt `0 9 * * 2,5`, Zeitzone `Europe/Berlin`; kein zusätzlicher Nachholjob.
Diese Dokumentation ändert weder gespeicherten Prompt noch Runtime-Konfiguration oder Aktivierungszustand.
Timeout-Befunde und Empfehlungen: [Runtime-Prüfung](NEO-RUNTIME-TIMEOUT-AUDIT.md).
