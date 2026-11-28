# Kontrollierter Runner: Offline-Implementierung, Produktionsgate geschlossen

Der vorgesehene Einstieg ist `scripts/editorial_runner.py`, nicht die historische
Admission-CLI `editorial_run_guard.py`. Letztere bleibt als kompatible Zeit-/Warnbibliothek
und Legacy-Testgegenstand bestehen; ihre eigene DB ist keine Produktionsautorität.
Keine Installation, Cron-/OpenClaw-/Matrixänderung, Freigabe, Credentials oder Publikation.

## Ausführbarer Ablauf

`Runner.start(head)` reserviert Termin UND singleton active-run in einer FULL-synchronen
SQLite-Transaktion. Das OS-flock schützt gleichzeitig lebende Prozesse über den ganzen
Runner-Aufruf; der persistente singleton schützt auch zwischen Aufrufen und nach SIGKILL.
Ein neuer Termin wartet nicht auf TTL: er wird verweigert. `advance(run)` liest zuerst
GitHub, schreibt vor jedem Effekt einen persistenten Intent, liest danach erneut GitHub.
Nur ein belegtes Deployment des exakten Mergecommits löscht active; der Termin bleibt
für immer verbraucht. Keine automatische Löschung und keine Wiederholung eines Intents.
`reconcile(run)` ist ausschließlich lesend gegenüber GitHub. Ein ausgebliebener Effekt
nach geschriebenem Intent bleibt konservativ blockiert: kein automatischer Retry, auch
wenn GitHub derzeit keinen PR zeigt. Betreiber müssen diesen Fall separat untersuchen;
es gibt bewusst keinen force-unlock/reset-Befehl.

Der kontrollierte Ablauf übernimmt einen vorbereiteten unveränderlichen Artikel-Head.
Research/Writer laufen nicht als Plugins in der privilegierten Runneridentität. Review,
CI und Inhaltsvalidierung bleiben verpflichtend; keine LLM-Freigabe ersetzt den Broker.

CLI: `start --head FULL_SHA`, danach `advance --run ID` bzw. `reconcile --run ID`.
Jeder CLI-Aufruf prüft erneut das Produktionsgate. Kein `--db`, Test-/Env-Bypass oder
Zeitstempeloverride. Der Offline-Testzugang ist eine Python-Library, keine sichere Grenze
gleicher OS-Identitäten. Verlust der Datenbank führt zu Verweigerung, nicht Neuanlage.
`initialize()` ist ausschließlich Offline-Provisionierung, kein CLI-/Runtimepfad.

Warnung: nicht blockierend ab 90 Minuten. Während `advance` läuft ein eigener read-only
Monitor (1 s Pollintervall), auch während Netzwerk-/Brokerwartezeit. Cron stdout ist
Rückfallkanal; fehlerhafte Benachrichtigungen wiederholen niemals Veröffentlichung.
Ein getöteter Prozess kann nicht selbst warnen: OpenClaw-Recovery/Überwachung muss den
persistenten Zustand später erneut lesen. Smartphoneintegration bleibt separat offen.
Später jobspezifisch `payload.timeoutSeconds=14400`, hier nicht installiert; weder diese
Zeit noch die Warnschwelle ist eine Guarddeadline. Keine TTL, Nachholung, Ersatzartikel.

## Nicht installierter Deploymentvertrag / zwingende Grenze

Produktiv muss ein Betreiber eine separate, unprivilegierte Serviceidentität einrichten;
der Redaktionsagent darf weder diese Identität noch deren Dateien/Code ändern können.
Root und dieselbe UID sind ausdrücklich KEINE geschützte Gegenseite.
Der vorliegende Root-Workspace ist KEINE solche Installation.

`/etc/future-pulse/runner.json` ist root-owned, ohne Gruppen-/Fremdschreibrecht, ebenso
alle Eltern. Pflichtfelder:

- `enabled: true`, `recovery_verified: true` erst nach tatsächlich verifiziertem
  OpenClaw-Recovery durch Betreiber, sonst Gate zu;
- `runner_uid` = nicht-root effektive UID, `editorial_uid` davon verschieden/nicht root;
- `machine_id` exakt aus `/etc/machine-id` des einzigen autorisierten Hosts;
- `directory`: kanonisches, exklusives lokales Journalverzeichnis, runner-owned,
  root-owned Eltern, keine symlinks oder Gruppen-/Fremdschreibrechte; bestehende
  `journal.sqlite` unter denselben Prüfungen;
- `code_directory`: root-owned installierter Code einschließlich beider Pythonmodule,
  keine schreibbaren Eltern; tatsächlicher Runner muss von genau dort stammen;
- `broker`: Unixsocket in root-owned Eltern, runner-owned ohne Gruppen-/Fremdschreibrecht;
- `repository: owner/repo`, `base: main` bestimmen das feste Veröffentlichungsziel.

Eine kopierte zweite Umgebung kann keine eigene DB wählen: CLI verwendet ausschließlich
die geschützte Richtlinie und verweigert andere machine-id. Das ist eine Single-host-
Beschränkung, kein verteilter Lock. VM-Klone mit duplizierter machine-id sowie root als
Angreifer sind nicht durch machine-id kryptografisch ausgeschlossen: Betreiber müssen
Klone/Identitäten und Mounts ausschließen; für feindliche Hosts ist ein zentraler Broker
mit Hostauthentisierung nötig. SQLite auf Netzlaufwerken wird nicht unterstützt.

**Implementiert, nicht installiert:** `scripts/editorial_broker.py` stellt den separaten
Brokerdienst samt echtem REST-Schreibadapter bereit. Tests verwenden ausschließlich
Doubles. Keine Credentials, Dienste oder GitHub-Schreibeffekte wurden eingerichtet.
Der Dienst erzwingt Peer-UID (SO_PEERCRED), rootgeschützte Policy, machine-id,
Recoveryfreigabe, separate Broker-/Runner-/Redaktions-UIDs, geschützten Code und
canonical Journalpfad. SQLite-Journal wird nur offline provisioniert: Lauf-/Termin-/Head-
Bindung, aktive Exklusivreservierung ohne TTL und Operationsintent vor jedem Effekt.
Nach unbestätigtem Effekt nur positive unabhängige Reconciliation, nie blindes Resenden.

Brokerpolicy `/etc/future-pulse/broker.json` benötigt enabled/recovery_verified=true,
broker_uid/runner_uid/editorial_uid (alle separat und nicht root), machine_id, directory,
code_directory, credential_file, socket, repository, base, source_branch, reviewers
(Operator-Allowlist unabhängiger GitHub-Logins), required_checks (name/app_id), ruleset_ids.
Der Betreiber provisioniert rootgeschützte Eltern, broker-owned Journalverzeichnis und
0600-Credentialdatei sowie einen socket-aktivierten Listener (FD 3, LISTEN_PID/LISTEN_FDS).
Der Socket ist runner-owned 0600 unter root-owned Eltern; der Broker kann diesen Pfad
nicht ersetzen. Keine automatische Journal-/Socket-Reparatur. Runnerpolicy verwendet
`broker` als Pfad desselben Sockets. Niemand aus Redaktions-/Runneridentität erhält
Brokerjournal-, Policy-, Code-, Credential- oder alternative GitHub-Schreibrechte.
Root/gleiche UID sind ausdrücklich KEINE Sicherheitsgrenze.

Der Broker prüft unabhängig PR-Repo/Base/Head, nicht-Draft, mergeable/clean,
Allowlist-Review zum exakten Head (nicht PR-Autor), keine Changes-Requested-Entscheidung,
alle konfigurierten Checknamen samt App-ID und Erfolg. Aktive anwendbare Rulesets müssen
ohne Bypass-Akteure gelten, Pull-Request-Review mit stale-dismissal/last-push approval und
strikte, appgebundene Required Checks enthalten. Merge benutzt PUT mit exakt `sha=head`.
Die serverseitigen Rulesets bleiben wesentlich gegen Änderungen zwischen Read und Write.
PR-Erstellung ist absichtlich Draft; der Redaktionsagent darf dies nicht eigenständig als
Reviewfreigabe behandeln. Reale GitHub-API-/Rulesetfähigkeit ist später separat abzunehmen.

`editorial_runner.py run --head SHA` hält den Prozesslock von Terminclaim durch den
rootkonfigurierten `workflow_command` bis Reconciliation/Publikation. Der Warnmonitor läuft
auch während dieses gesamten Workflows. Das Kommando ist ein vertrauenswürdiger
Orchestrator, kein Redaktionsagent mit Runner-UID: Research/Writer/Review müssen in der
separaten Redaktionsidentität ausgeführt werden. Der konkrete projektspezifische
Orchestrator ist Deploymentverdrahtung, nicht in diesem Repository implementiert.
Bei Absturz während Workflow bleibt `workflow_running` dauerhaft gesperrt; Reconciliation
verweigert Fortsetzung bis Operator externe Worker sicher gefenced und Zustand geprüft
hat. Keine automatische Freigabe, kein Recovery-Override in der CLI. `start` reserviert
nur; `advance` ist kein Aufruf für ungeschützte parallele redaktionelle Arbeit.

GitHubReadAdapter implementiert echte read-only REST-Abfragen (PRs inkl. Pagination,
Repo/Base/Head, merged+merge_commit_sha, github-pages Deployments+neuester success-Status).
Kein Netzaufruf wurde zur Abnahme ausgeführt; Transport wird gedoubelt. Private Repos
brauchen separat verwahrte read-only Credentials; die Produktionsverdrahtung verwendet
aktuell öffentliche Reads. Kein GitHub-Effektadapter kann read-only Evidence ersetzen.

## Reproduzierbare Abnahmematrix

`python3 -m unittest discover -s tests -q`

| Nachweis | Test in test_editorial_runner.py |
|---|---|
| A01 lebender Konkurrenzprozess/manuell + anderer Termin nach Reopen | test_A01_parallel_manual_and_different_slot |
| A02 getrennte DB-Umgebung kann CLI-Ziel nicht wählen | test_A02_A10_A11_gate_bypass |
| A03 SIGKILL nach durable claim, active überlebt | test_A03_A09_kill_after_claim_and_timeout |
| A04 SIGKILL vor/nach PR mit persistentem fake remote | test_A04_before_pr / test_A04_after_pr |
| A05 SIGKILL vor/nach Merge mit persistentem fake remote | test_A05_before_merge / test_A05_A06_after_merge_reconciliation |
| A06 remote Merge ohne lokale Bestätigung, Deployment belegt | test_A05_A06_after_merge_reconciliation |
| A07 unerreichbar: keine Intents/Effekte, active bleibt | test_A07_ambiguous_remote |
| A08 89/90 Minuten/7 Tage ohne Abbruch | test_A08_warning_no_abort |
| A09 harter Timeout-Surrogat SIGKILL + 14400 s, kein Ersatz | test_A03_A09_kill_after_claim_and_timeout |
| A10 fehlende/unsichere Policy | test_A02_A10_A11_gate_bypass |
| A11 CLI --db und Env können Produktionsgate nicht öffnen | test_A02_A10_A11_gate_bypass |
| A12 Notification wirft, kein zweiter Effekt | test_A12_notice_failure_no_republish |
| Reale read-only Adapterlogik, PR/Head/Merge/Deployment | test_read_adapter_evidence |
| Host/UID/Recovery/Code-Policy deterministisch verweigert | test_policy_identity_host_recovery_and_code_location |
| Verschwundener bekannter PR blockiert Merge | test_recorded_pr_disappears_no_merge |
| Fehlendes Journal nicht neu erzeugen | test_missing_db_not_recreated |

50 Repositorytests bestehen (14 Runner- und 8 Broker-Tests). SIGKILL ist ein echter Subprozesskill,
nicht normales Connection-Schließen. Fake-Remote liegt in separater Datei außerhalb der
Runnertransaktion und bleibt nach Prozessende bestehen. Bestehende Zeit-/DST-/Review-/
Render-/CI-Sicherheitstests bleiben unverändert.

## Ergänzende Broker-Abnahmebelege

`tests/test_editorial_broker.py`:

| Nachweis | Test |
|---|---|
| A01/A02/Brokerzustand zweite Umgebung und zweiter Prozesslock | test_peer_credentials_and_second_environment |
| A02/A11 echte andere Prozess-UID über Unixsocket, kein Claim/Effekt | test_real_other_identity_socket_denied |
| A04/A05/A06/A09 SIGKILL und subprocess-Timeout vor/nach PR/Merge, persistentes Fake-Remote | test_crash_and_timeout_intents |
| A10 fehlendes Journal wird nicht neu angelegt | test_missing_journal_closed |
| unabhängige Review-/Check-/Draft-/Ruleset-Negativbelege | test_independent_review_checks_draft_rulesets |
| atomare exakte Head-Vorbedingung im Schreibadapter | test_exact_head_write_precondition |
| exakter Marker und nochmalige Detailprüfung | test_marker_substring_and_changed_detail |
| Workflow-Crash kann nicht über reconcile übergangen werden | test_uncertain_editorial_workflow_cannot_be_reconciled |

Der echte UID-Test senkt ausschließlich die Identität eines Testkindes auf numerische UID
65534; ohne Root-Testprozess wird er ausdrücklich übersprungen. Keine Konten/Hostrechte
werden angelegt. Zweite Umgebung wird am gemeinsamen Brokerjournal blockiert, keine
Behauptung einer verteilten SQLite-Sperre. Policy-/Hosttests bleiben zusätzlich vorhanden.
A09 nutzt verkürzten echten subprocess-Timeout, keine vierstündige Testlaufzeit.

Dies ist Offline-Codeevidenz, keine installierte Produktionsabnahme. Weiter offen:
Operatorprovisionierung und Socketaktivierung, tatsächliche isolierte Workflowverdrahtung,
OS-/Credential-Custody-Audit, verifiziertes OpenClaw-Recovery, reale unabhängige Review-/
Ruleset-/GitHub-Pages-End-to-end-Abnahme und Cron-Warnzustellung. Der Broker ist nun
implementiert; diese verbleibenden Installations-/Integrationsgates sind keine Behauptung,
dass der Dienst bereits betrieben wird. Produktionssperre bleibt bestehen.
