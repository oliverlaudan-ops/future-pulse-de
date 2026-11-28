# Verbindlicher Implementierungsauftrag – Etappe 1

Dieser Auftrag gilt für den Feature-Branch von PR #21, future-pulse-de,
feat/neo-cron-runtime-guards. Er ist die dauerhafte Arbeitsgrundlage für
nachfolgende Sessions/Agenten. Er ist keine Produktions- oder Merge-Freigabe.
Die frühere Abschlussprüfung wird akzeptiert; ihre Lücken sind zu implementieren.

## Projektentscheidungen
- Matrix entfällt vollständig als Future-Pulse-Benachrichtigungskanal.
  Bestehende Matrix-Installation nicht ändern.
- Später native OpenClaw-Smartphone-App verwenden; tatsächliche Unterstützung
  und zuverlässige Zustellung erst in späterer Integration nachweisen.
- Bis dahin Cron-Rückmeldung als Rückfallmechanismus vorsehen.
- OpenClaw-Recovery bleibt zwingende Voraussetzung der Produktionsfreigabe.

## Verbindliche Implementierung
1. Exklusive Sperre über den gesamten Redaktionslauf, nicht nur DB-Transaktionen.
2. Persistente Crash-/Wiederanlaufzustände.
3. Verifizierbare GitHub-Reconciliation vorhandener PRs, Merges und Deployments.
4. Schutz gegen mehrfache externe Veröffentlichungsaktionen.
5. Schutz paralleler getrennter Umgebungen; alternativ technisch erzwungener,
   dokumentierter einzelner autorisierter Ausführungshost.
6. Standardmäßig geschlossenes Produktionsgate; Freigabegrundlage darf vom
   Redaktionsagenten nicht eigenständig veränderbar sein.
7. Verpflichtende Schutzintegration in den vorgesehenen Runner; keine produktive Installation.

## Zeit-/Laufzeitregeln
Di/Fr regulär 09:00 Europe/Berlin. Erstzulassung [09:00:00,10:00:00);
zugelassene Läufe dürfen danach weiterarbeiten. Nicht blockierende Warnung
ab 90 Minuten. Später jobspezifisch payload.timeoutSeconds=14400 (240 Minuten),
keine globale OpenClaw-Änderung. Keine pauschale Guard-Gesamtlaufzeit.
Keine zeitbasierte Freigabe belegter Sperren, automatische Nachholung oder
Ersatzveröffentlichung. Langsame Agenten/CI allein sind kein Abbruchgrund.
Timeout hebt weder Terminreservierung noch Sperre auf und erzeugt keinen Ersatzartikel.

## Verpflichtende Abnahmetests (jeweils konkreter technischer Nachweis)
A01 Gleichzeitige und manuelle Parallelstarts.
A02 Parallele Ausführungsversuche aus getrennten Umgebungen.
A03 Prozessabbruch nach Terminregistrierung.
A04 Prozessabbruch unmittelbar vor und nach PR-Erstellung.
A05 Prozessabbruch unmittelbar vor und nach Merge.
A06 Bereits erfolgter Merge ohne lokale Abschlussbestätigung.
A07 Unklarer/nicht erreichbarer GitHub-Zustand.
A08 90-Minuten-Warnschwelle ohne Abbruch.
A09 Simulierter Runtime-Timeout mit sicherer Zustandsbehandlung.
A10 Fehlende/ungültige Produktionsfreigabe.
A11 Versuch der Produktionsgate-Umgehung.
A12 Fehlgeschlagene Benachrichtigung ohne erneute Veröffentlichung.

Externe Seiteneffekte ausschließlich durch Test-Doubles oder isolierte Testumgebungen.
Zusätzlich bestehende Zeit-, Persistenz-, Review-, CI- und sonstige Sicherheitsanforderungen
bewahren. Ein grüner CI-Status allein ist keine Gesamtabnahme.

## Arbeitsweise und Grenzen
Coder und unabhängigen Reviewer einsetzen; notwendige Korrekturschleifen durchführen.
Technische Blocker konkret dokumentieren und geeignete Lösungsoptionen vorlegen.
Ausschließlich Feature-Branch PR #21 ändern. Keine produktiven Runtime-Änderungen,
Cron-Aktivierung, main-Änderungen, OpenClaw-/Matrix-Reparatur oder Artikelpublikation.
Kein Merge ohne gesonderte Freigabe. Produktionssperre bleibt bestehen.
