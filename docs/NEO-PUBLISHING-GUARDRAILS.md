# NEO: GitHub-Veröffentlichungsregeln (23.11.2026)

NEO arbeitet für neue Future-Pulse-Beiträge ausschließlich über einen Feature-Branch und einen Pull Request. Keine direkten Pushes auf `main`, keine Force-Pushes, keine Änderungen am Ruleset, keine GitHub-Admin-Bypässe. Keine Berechtigungserweiterung, keine zusätzlichen kostenpflichtigen Dienste. Die produktive Zeitplanung und autonome Merge-Freigabe bleiben bis zur ausdrücklichen Betreiberfreigabe deaktiviert.

## Verbindliche Gates

1. Researcher recherchiert und dokumentiert Primärquellen. Writer erstellt den Artikel. Ein **unabhängiger** Reviewer prüft den exakten finalen Text nach der letzten Änderung und dokumentiert seine Befunde.
2. Neue Artikel enthalten korrekte KI-Metadaten. `human_reviewer` bleibt leer, solange kein Mensch geprüft hat. `ai_reviewer` benennt den tatsächlichen Reviewer. Keine erfundenen Freigaben.
3. Vor jedem Merge muss jeder neue oder geänderte KI-Artikel einen gültigen, unabhängigen, hashgebundenen Bericht besitzen, unabhängig von PR-/Hugo-Draft-Status. Der Bericht darf nach dem ersten Artikel-Commit nachgereicht werden; vorher bleibt CI rot. Nur für die tatsächliche Veröffentlichung bei vollständigem PASS: `draft: false`, `ai_review_status: passed`, echtes `review_date` und `reviews/<slug>.json` mit SHA-256 der finalen Artikeldatei. Keine Selbstfreigabe durch NEO oder den Writer.
4. GitHub-PR-Check `pr-validation` muss grün sein; bei Fehlern oder unklaren Befunden stoppen. Der Check validiert Metadaten, maschinenlesbaren Reviewer-Nachweis und Hugo-Build. Ein grüner Check beweist **nicht** die tatsächliche inhaltliche Richtigkeit und nicht die Urheberschaft des Reviewers.
5. Erst nach ausdrücklich aktivierter produktiver Veröffentlichungsberechtigung darf NEO einen nicht mehr als Draft markierten PR mergen. GitHub-Pages-Deployment nach Merge prüfen; erst nach erfolgreichem Deployment als veröffentlicht melden. GitHub löscht den Feature-Branch nach Merge automatisch.
6. NEO darf weder Validierungsskripte noch GitHub-Workflows, Branchschutz, KI-Policy oder Theme im regulären Artikelbetrieb verändern. Dafür ist ein gesondert genehmigter Wartungs-PR nötig.

## Testmodus

PR #18 bleibt Draft, `draft: true`, `ai_review_status: passed_draft_only`; kein Merge und keine Veröffentlichung. Der Test demonstriert ausdrücklich, dass jeder neue oder geänderte KI-Artikel ohne unabhängigen Reviewer-Nachweis vom Validator abgewiesen wird, auch als Draft. Ein technischer Draft-PASS ist keine Publikationsfreigabe.
