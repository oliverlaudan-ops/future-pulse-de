# Future Pulse: Runtime-Timeout-Prüfung (2026-11-28)

Nur lesend geprüft; keine produktiven Runtime-Konfigurationen geändert. Installiert: OpenClaw 2026.11.10.

## Befunde und Quellen

- Gespeicherter Cron „Future Pulse · Redaktion (gesperrt)“: deaktiviert, `0 9 * * 2,5`, `Europe/Berlin`, isolierter `agentTurn`; `payload.timeoutSeconds` fehlt. Verifiziert mit Automations list/get einschließlich deaktivierter Jobs.
- **Konkreter Konflikt:** Der installierte Scheduler verwendet ohne Job-Override für `agentTurn` **3.600 Sekunden (60 Minuten)** Sicherheitslimit, also schon vor der 90-Minuten-Warnung. Quelle: `dist/service-BsZQ3nRe.mjs`, `AGENT_TURN_SAFETY_TIMEOUT_MS=36e5`, `resolveCronJobTimeoutMs`. Für command/script ist der Default 600 Sekunden; das ist nicht der aktuelle Redaktionspfad. Explizites Job-Timeout 0 liefert dort kein Scheduler-Zeitlimit.
- Agenten: `agents.defaults.timeoutSeconds` nicht gesetzt; installierter Default **172.800 Sekunden (48 Stunden)**. Quelle: `dist/timeout-B3hylhqM.mjs`, `resolveAgentTimeoutMs`. 0 wird auf den technisch maximalen Timerwert abgebildet, nicht auf eine Publikationsfreigabe. Der isolierte Cron-Agent übernimmt `payload.timeoutSeconds` als Override: `dist/isolated-agent-0ytwxWOq.mjs`. Scheduler- und Agentenlimit sind getrennte Schichten.
- Subagenten: `agents.defaults.subagents.runTimeoutSeconds` nicht gesetzt; Resolver-Default **0** (kein explizites Kindlauf-Deadline-Limit). Quelle: `dist/subagent-spawn-plan-I_dyNt2s.mjs`, `resolveConfiguredSubagentRunTimeoutSeconds`; `dist/subagent-run-liveness-CRCDHPXH.mjs`. Ein explizites `sessions_spawn.runTimeoutSeconds` überschreibt den Default und bleibt bei nativen Fortsetzungen erhalten (Tool-Schema). Übergeordnete Runtime-/Providergrenzen bleiben möglich.
- Shell-Tools: `exec.timeoutSeconds=0` kann das Prozesslimit deaktivieren; ohne Angabe gilt gegebenenfalls ein Default. `tools.exec.timeoutSec` nicht gesetzt; effektiver Shell-Default für alle Ausführungshosts hier nicht abschließend nachgewiesen. Separater CLI-Pfad `agent-exec` hat 600 Sekunden Default (`dist/agent-exec-B2zAx9Sf.mjs`); nicht mit dem Cron-Agenten gleichsetzen.
- Web-Tool-Basisdefault **30 Sekunden** pro Request (`dist/web-shared-CPCN-uc2.mjs`); `tools.web.fetch.timeoutSeconds` und `tools.web.search.timeoutSeconds` nicht gesetzt. Einzelne Provider/Browser/MCP-/Netzwerkaufrufe können eigene Limits haben; eine vollständige externe Providerinventur wurde nicht durchgeführt.
- Wartezeiten sind nicht gleich Laufzeitlimits: `subagents.wait`-Timeout beendet den Kindlauf nicht; `process.poll` wartet maximal 30 Sekunden pro Aufruf; `exec.yieldMs` gibt nur einen Prozesshandle zurück. Diese Toolverträge verlangen korrekte Fortsetzung, nicht Neuanlage des Artikels.
- Guard: SQLite-Lock-Wartezeit **15 Sekunden**, keine Gesamtlaufzeitgrenze (`scripts/editorial_run_guard.py`). DB-Lock-Fehler dürfen keine Reservierungen löschen.
- Repository-CI: `.github/workflows/pr-validation.yml` und `hugo.yml` separat berücksichtigen. Beide Workflows setzen kein explizites Job-Timeout; Pages verwendet `cancel-in-progress: false`. Ein fehlendes Workflow-Timeout bedeutet nicht unbegrenzte externe GitHub-Laufzeit; CI-/Pages-Plattformlimits und Warteschlangen sind außerhalb des Guards.

Quellen sind der installierte lokale Code unter `/usr/lib/node_modules/openclaw/dist/` (Build-Dateinamen versionsabhängig), selektiv gelesene Konfigurationsfelder aus `~/.openclaw/openclaw.json`, Automations get sowie die aktuellen Toolverträge. Keine Geheimnisse oder vollständige Hostkonfiguration werden hier gespeichert. Nicht gesetzte Werte belegen nur diese geprüfte Quelle, nicht das Fehlen aller möglichen Overrides.

## Empfehlungen – nicht angewendet

1. Vor späterer Produktionsfreigabe den **jobspezifischen** 60-Minuten-Konflikt beheben; bevorzugt explizites `payload.timeoutSeconds: 0` für diesen redaktionellen Orchestrator nach gesonderter Freigabe und isoliertem Test des tatsächlichen Runtimepfads. Keine globale Timeout-Aufweitung nötig. Technische Timer-/Providergrenzen bleiben zu berücksichtigen; langlebige Prozesse benötigen persistente, reconciliierbare Fortsetzung.
2. Kindläufe nicht mit kurzen pauschalen Deadlines starten; explizite Overrides prüfen. Lange Recherche/Reviews müssen auch jenseits 90 Minuten möglich sein. Die Betriebswarnung ist kein Kill-Signal.
3. Einzelne Netzwerkaufrufe weiter begrenzen, begrenzte lesende Wiederholungen zulassen; lange CI-/Deployment-Warteprozesse mit geeignetem Prozesslimit oder persistenter Fortsetzung ausführen. Weder Warte-Timeout noch langsamer Fortschritt rechtfertigen Abbruch oder Ersatzpublikation.
4. Timeout/Prozessabbruch immer als potenziell unklaren externen Zustand behandeln: Run-ID/PR/Head/Merge/Deployment abgleichen, Sperren halten und nötigenfalls menschliche Reconciliation verlangen. Kein automatisches Freigeben nach TTL.
5. Vor Aktivierung E2E-Test mit Lauf >90 Minuten, wartendem Subagenten und verzögerter CI, Warnzustellung und simuliertem Crash durchführen. Die Guard-Unit-Tests ersetzen diesen noch offenen Integrationstest nicht.

Keine Produktionsfreigabe, keine Cron-Aktivierung, keine Änderung des gespeicherten Cron-Prompts.
