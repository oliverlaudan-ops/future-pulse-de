---
title: "KI-Agenten evaluieren: 5 Schritte zum Test"
date: 2026-11-27
draft: true
description: "KI-Agenten evaluieren: Entwickle in 5 Schritten ein Testset, prüfe Tool-Aufrufe und erkenne Fehler vor dem produktiven Einsatz. Starte deinen Praxistest. [2026]"
summary: "So entwickelst du nachvollziehbare Tests für KI-Agenten, prüfst ihre Aktionen und erkennst Sicherheitsprobleme vor dem Einsatz."
slug: "ki-agenten-evaluieren"
tags: ["AI Agents", "Automatisierung", "KI-Tools"]
keywords: ["KI-Agenten evaluieren", "Agenten Testfälle erstellen", "Tool-Aufrufe Trace-Auswertung"]
author: "Oliver Laudan"
ShowToc: true
TocOpen: true
ai_generated: true
ai_model: "openai/gpt-6.2"
human_reviewer: ""
ai_reviewer: ""
ai_review_status: "pending"
review_date: ""
---

Dein KI-Agent hat gerade eine Aufgabe erfolgreich erledigt. Er hat die passenden Informationen gefunden, ein Werkzeug aufgerufen und ein überzeugendes Ergebnis geliefert. Doch funktioniert derselbe Ablauf auch morgen, wenn eine Schnittstelle ausfällt oder eine Anfrage unvollständig ist?

Wenn du KI-Agenten evaluieren möchtest, brauchst du mehr als eine erfolgreiche Demo. Du brauchst wiederholbare Aufgaben, klare Erwartungen und überprüfbare Ergebnisse.

**Was du lernen wirst:**

- Wie du ein kleines, aussagekräftiges Testset entwickelst.
- Wie du Werkzeugaufrufe und tatsächliche Ergebnisse unterscheidest.
- Wie du Fehler und Sicherheitsverstöße zu Freigabekriterien machst.

## Warum eine Demo nicht reicht

Ein KI-Agent entscheidet innerhalb seiner verfügbaren Möglichkeiten, welche Schritte er ausführt. Anders als bei einer fest programmierten Abfolge können unterschiedliche Versuche verschiedene Wege zum Ziel nehmen. Dabei spielt nicht nur das Modell eine Rolle, sondern auch die Umgebung mit ihren Werkzeugen, Anweisungen und Berechtigungen.

Anthropic unterscheidet in seinem [Leitfaden zur Evaluation von KI-Agenten](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) zwischen einer Testaufgabe, einzelnen Versuchen, Bewertungslogik, Ablaufprotokoll und tatsächlichem Endzustand. Diese Unterscheidung ist für praktische Tests besonders hilfreich.

Eine überzeugende Abschlussmeldung ist beispielsweise kein Beweis dafür, dass ein Ticket wirklich angelegt wurde. Kontrolliere den Zustand des Ticketsystems unabhängig von der Antwort des Agenten.

Wenn du noch am Anfang stehst, erklärt unser [Tutorial zum Bau eigener AI Agents](/blog/ai-agents-selbst-bauen-tutorial/) die Grundlagen der Umsetzung.

## KI-Agenten evaluieren: fünf Schritte

### Den Aufgabenbereich festlegen

Beginne mit einem einzigen, klar begrenzten Prozess. Stell dir einen Assistenzagenten vor, der eingehende IT-Anfragen klassifiziert und einen Ticketentwurf vorbereitet. Er darf geeignete Kategorien vorschlagen, aber keine Konten entsperren oder Berechtigungen verändern.

Schreibe auf, welche Eingaben er erhält, welche Werkzeuge er verwenden darf und welchen Zustand er am Ende erreichen soll. Lege auch fest, wann er nachfragen oder an einen Menschen übergeben muss.

Verwende für die ersten Tests eine isolierte Umgebung mit künstlichen Tickets und Testkonten. Produktive Zugangsdaten sind für diesen Versuch weder nötig noch sinnvoll.

### Agenten-Testfälle erstellen

Entwickle Aufgaben, die sowohl gewöhnliche Anfragen als auch Ausnahmen abdecken. Jede Aufgabe bekommt eine eindeutige Kennung, einen Ausgangszustand und überprüfbare Erwartungen.

| Testfall | Erwartetes Verhalten |
| --- | --- |
| Vollständige Störungsmeldung | Passende Kategorie und Entwurf |
| Fehlender betroffener Dienst | Gezielte Rückfrage |
| Widersprüchliche Angaben | Unsicherheit kenntlich machen |
| Wissensdatenbank nicht erreichbar | Fehler melden, nichts erfinden |
| Aufforderung zur Kontenentsperrung | Keine Änderung, autorisiert eskalieren |
| Fremde Anweisung im Tickettext | Als Eingabedaten behandeln |
| Wiederholte Ereignis-ID | Keine zusätzlichen Tickets erzeugen |

Das sind illustrative Tests, keine bereits gemessenen Ergebnisse. Passe sie an deine tatsächlichen Geschäftsregeln an. Ergänze unterschiedliche Formulierungen, damit dein Agent nicht nur die zuerst verwendeten Beispielsätze beherrscht.

Trenne zudem Entwicklungsfälle von zurückgehaltenen Prüfaufgaben. So vermeidest du, dass du Anweisungen ausschließlich auf deine bekannten Beispiele optimierst.

### Tool-Aufrufe im Trace prüfen

Ein Trace ist ein Protokoll beobachtbarer Schritte eines Agentenlaufs. Er kann beispielsweise Werkzeugnamen, ausgewählte Parameter, Zeitpunkte, Rückgabewerte und Fehler enthalten. Die [OpenAI-Dokumentation zur Agenten-Evaluation](https://developers.openai.com/api/docs/guides/agent-evals) beschreibt die Nutzung von Evaluationen für Agenten-Workflows.

Für deinen Helpdesk-Test ist wichtig, ob der Agent die richtige Wissensquelle abfragt, die zulässigen Parameter verwendet und auf einen Werkzeugfehler angemessen reagiert. Prüfe dabei nicht nur erfolgreiche Aufrufe, sondern auch unerlaubte Versuche, selbst wenn die technische Zugriffskontrolle sie abweist.

Du brauchst dafür keine privaten Modellgedanken. Beobachtbare Aktionen und überprüfbare Zustände sind die entscheidenden Anhaltspunkte. Vermeide außerdem, Zugangstoken oder personenbezogene Ticketinhalte ungeschützt in Protokollen abzulegen.

Bei komplexeren Abläufen findest du ergänzende Grundlagen in unserem Beitrag zu [Multi-Agent-Systemen und Orchestrierung](/blog/multi-agent-systeme-orchestrierung-2026/).

### Ergebnisse und Grenzen bewerten

Nutze für eindeutige Regeln möglichst automatische Prüfungen. Existiert genau ein erwarteter Ticketentwurf? Wurde ein unerlaubter Schreibzugriff versucht? Enthält der Entwurf die benötigten Pflichtfelder?

Für die sprachliche Qualität kannst du zusätzlich ein festes Bewertungsraster einsetzen. Prüfe beispielsweise Verständlichkeit, fachliche Richtigkeit und den Umgang mit fehlenden Informationen. Kalibriere eine modellbasierte Bewertung anhand menschlich geprüfter Beispiele, statt ihr blind zu vertrauen.

Führe jede Aufgabe mehrfach aus und setze die Testumgebung zwischen unabhängigen Versuchen zurück. Dokumentiere Modellversion, Anweisungen, Werkzeugversionen und Testdaten, damit spätere Vergleiche aussagekräftig bleiben.

### Freigabekriterien vorab definieren

Lege vor dem ersten Durchlauf fest, was einen erfolgreichen Test ausmacht. Eine hohe Gesamtquote darf einen kritischen Sicherheitsverstoß nicht verdecken.

Ein mögliches, selbst gewähltes Beispiel für einen internen Pilotversuch wäre:

- Mindestens 90 Prozent erfolgreiche reguläre Testläufe.
- Kein unerlaubter Schreibzugriff und kein entsprechender Versuch in den Sicherheitsfällen.
- Keine doppelte Ticketerstellung in den Wiederholungstests.
- Nachvollziehbare Eskalation bei fehlender Berechtigung.
- Dokumentierte Grenzen für Bearbeitungszeit und Werkzeugaufrufe.

Diese Werte sind keine allgemeingültige Norm. Bei sensiblen Prozessen können strengere Regeln und zusätzliche Tests nötig sein. Auch null beobachtete Verstöße beweisen nicht, dass außerhalb des Testsets keine auftreten können.

## Testprotokoll für deinen Agenten

Halte pro Versuch die Test-ID, die Modell- und Workflow-Version, den Ausgangszustand, das erwartete Ergebnis und den beobachteten Endzustand fest. Ergänze einen Verweis auf das bereinigte Ablaufprotokoll und markiere, welche Einzelprüfungen erfolgreich waren.

Unterscheide fachliche Fehler von technischen Ausfällen. Wenn deine Testumgebung selbst nicht erreichbar ist, kennzeichne den Versuch als nicht auswertbar und dokumentiere den Grund. Verschweige solche Versuche nicht in der Zusammenfassung: Auch die Zuverlässigkeit der Infrastruktur beeinflusst den späteren Betrieb.

Bei einem Wiederholungstest innerhalb eines einzelnen Szenarios bleibt der Zustand dagegen bewusst erhalten. Nur so kannst du prüfen, ob eine erneut zugestellte Ereignis-ID einen zweiten Entwurf auslöst.

Der Schwerpunkt liegt hier auf reproduzierbaren Prüfaufgaben vor der Freigabe. Unser Beitrag zu [AgentOps](/blog/ki-governance-agentops-2026/) betrachtet dagegen den gesamten betrieblichen Lebenszyklus einschließlich Überwachung und Kostenkontrolle.

## Praxisbeispiel: Ein Helpdesk-Pilot

Angenommen, du testest zehn Aufgaben jeweils fünfmal. Damit erhältst du 50 Einzelergebnisse. In einem fiktiven Durchlauf werden 46 Aufgaben erfolgreich bearbeitet, drei liefern unvollständige Entwürfe und einmal versucht der Agent einen nicht autorisierten Schreibzugriff.

Die rechnerische Erfolgsquote beträgt 92 Prozent. Trotzdem scheitert die Freigabe am Sicherheitskriterium. Eine rein prozentuale Bewertung hätte diesen wichtigen Unterschied verschleiert.

Untersuche den fehlerhaften Ablauf und prüfe, ob die Werkzeugrechte unabhängig vom Modell ausreichend begrenzt sind. Danach wiederholst du nicht nur den fehlgeschlagenen Test, sondern auch die bisher erfolgreichen Aufgaben. Änderungen an Anweisungen können schließlich unbeabsichtigte Auswirkungen auf andere Fälle haben.

Bei Wiederholungen externer Aktionen hilft dir unser Beitrag zur [Idempotenz in Automatisierungen](/blog/idempotenz-automatisierungen-doppelte-aktionen-vermeiden/), die Grenzen sicherer Retries zu verstehen.

## Häufige Fehler bei Agenten-Tests

**Nur die Antwort bewerten:** Vergleiche die Aussage des Agenten mit dem tatsächlichen Zustand der Testumgebung. Ein gut formulierter Erfolgsbericht ersetzt keine Zustandsprüfung.

**Nur den Normalfall testen:** Ergänze Ausfälle, unvollständige Daten und Konflikte zwischen Anweisungen. Prüfe auch, ob der Agent unter solchen Bedingungen angemessen abbricht.

**Tests mit Sicherheit verwechseln:** Evaluationen helfen dir, Schwächen zu entdecken. Sie ersetzen weder technische Zugriffsbeschränkungen noch Freigaben durch autorisierte Personen.

**Nur einmal testen:** Wiederholte Versuche zeigen dir, ob ein Ergebnis stabil ist. Halte die jeweiligen Bedingungen fest und unterscheide Veränderungen der Umgebung von Veränderungen des Modells.

Ein Testset ist zudem kein Ersatz für die spätere Betriebsüberwachung. Während die Evaluation definierte Aufgaben untersucht, beobachtet die Überwachung reale Abläufe. Beide ergänzen sich, erfüllen aber unterschiedliche Funktionen.

## Fazit: Verlässlichkeit durch Tests

KI-Agenten evaluieren bedeutet, Erwartungen in konkrete Prüfaufgaben zu übersetzen. Du kontrollierst nicht nur die Qualität einer Antwort, sondern auch den tatsächlichen Effekt eines Agentenlaufs und die Einhaltung seiner Grenzen.

Starte mit einem kleinen Testset, verbessere es anhand beobachteter Fehler und wiederhole es nach Änderungen. Definiere kritische Fehler unabhängig von deiner allgemeinen Erfolgsquote. So erhältst du eine nachvollziehbare Grundlage für die Entscheidung, ob dein Agent für einen begrenzten Pilotbetrieb geeignet ist.

**Dein nächster Schritt:** Wähle einen bestehenden Workflow und schreibe heute fünf Testfälle mit eindeutigem Sollverhalten auf. Welche Aktion dürfte dein Agent unter keinen Umständen ohne Freigabe ausführen?

## Weiterführende Artikel

- [AI Agents selbst bauen](/blog/ai-agents-selbst-bauen-tutorial/)
- [Multi-Agent-Systeme und Orchestrierung](/blog/multi-agent-systeme-orchestrierung-2026/)
- [Idempotenz in Automatisierungen](/blog/idempotenz-automatisierungen-doppelte-aktionen-vermeiden/)
