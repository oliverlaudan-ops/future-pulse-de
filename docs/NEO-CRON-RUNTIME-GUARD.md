# Future Pulse: technische Cron-Laufzeitsperre (Vorbereitung, nicht produktiv)

`scripts/editorial_run_guard.py` ist ein **fail-closed** Admission-Gate für die geplanten OpenClaw-Läufe. Der vorhandene Cron bleibt deaktiviert. Das Skript wird noch nicht von NEO oder GitHub Actions aufgerufen und erteilt keine Merge- oder Publikationsberechtigung.

## Zeit und Einmaligkeit

- Dienstag/Freitag, 09:00:00 bis einschließlich 09:05:00 Uhr, `Europe/Berlin`; kein Nachholen.
- `claim` erzeugt atomar einen einmaligen Datensatz pro lokalem Datum. SQLite `BEGIN IMMEDIATE`, eindeutiger Slot-Schlüssel, WAL und `synchronous=FULL` verhindern parallele oder wiederholte Claims.
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
