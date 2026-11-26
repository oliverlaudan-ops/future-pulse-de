# Redaktionsbetrieb Phase 1

## Geltungsbereich und Regelhierarchie

Dieses Dokument regelt den operativen Ablauf für neue redaktionelle Beiträge in Phase 1. Es aktiviert weder einen Veröffentlichungsprozess noch produktive Zeitplanung. Es ersetzt keine fachlichen Vorgaben: Bei Stil, Format und SEO gelten vorrangig [`../styleguide/00-ARTIKEL-VORLAGE-AKTUELL.md`](../styleguide/00-ARTIKEL-VORLAGE-AKTUELL.md), [`../styleguide/01-content-styleguide-hauptdokument.md`](../styleguide/01-content-styleguide-hauptdokument.md), [`../styleguide/08-seo-checkliste-detailliert.md`](../styleguide/08-seo-checkliste-detailliert.md) und [`../SEO-RULES.md`](../SEO-RULES.md). Für Metadaten, unabhängige Review-Nachweise, SHA-256 und CI gelten [`CONTENT-METADATA.md`](CONTENT-METADATA.md) und [`NEO-PUBLISHING-GUARDRAILS.md`](NEO-PUBLISHING-GUARDRAILS.md); diese maßgeblichen Dateien enthalten die einzelnen Gates, die hier nicht dupliziert werden.

Bei Konflikten gilt: (1) Schutz- und CI-Gates in den genannten Review-/Guardrail-Dokumenten, (2) konkrete SEO-Regeln und aktuelle Styleguides/Vorlage, (3) dieser Betriebsplan, (4) allgemeine oder historische Anleitungen. Widersprüchliche historische Dokumente sind keine aktive Ermächtigung.

## Rollen und Ablauf

NEO arbeitet als unabhängiger redaktioneller Workflow: Recherche mit dokumentierten Primärquellen, Artikelentwurf nach den maßgeblichen Styleguides, unabhängiges Review durch eine andere Instanz und nachvollziehbare PR-/CI-Prüfung. NEO bzw. der Writer darf nicht das eigene Review erteilen oder Review-Nachweise fingieren. Die genauen Metadaten-, Review-, Hash- und CI-Anforderungen stehen ausschließlich in den oben verlinkten Gates.

Beiträge werden ausschließlich in einem Feature-Branch und PR vorbereitet. Agenten dürfen nicht direkt nach `main` pushen oder mergen. Auch ein technischer CI-PASS oder ein Draft-Review ist keine Publikationsfreigabe. **Phase 1 umfasst keine Veröffentlichung:** kein Merge nach `main`, kein Deployment und keine produktive Veröffentlichung durch Agenten. Eine spätere Freigabe erfordert eine ausdrückliche Betreiberentscheidung und eine aktualisierte Betriebsregel.

## Zeitplanung und Themenqueue

Produktive Zeitplanung (Cron, Scheduled Tasks oder vergleichbare Ausführung) ist **nicht aktiviert**. Es gibt keinen produktiven automatischen Artikel- oder Refill-Lauf. Die Datei `blog-automation/topics.json` enthält die redaktionell geprüfte Themenreserve; Strategie und Archiventscheidungen stehen in [THEMENSTRATEGIE.md](THEMENSTRATEGIE.md). Ihre Inhalte und deaktivierten Schedule-Metadaten aktivieren für sich allein keinen Lauf.

## Historische Systeme und Anleitungen

Abacus AI ist vollständig deaktiviert. Verweise auf Abacus, den Scheduled Task, autonome Commits/Pushes oder dessen Refill-Ablauf sind ausschließlich historische Dokumentation und dürfen nicht als aktuelle Betriebsanleitung verstanden werden. Auch frühere direkte Push-/Deployment-Schritte in allgemeinen README-Anleitungen gelten nicht für den Agentenbetrieb. Maßgeblich für Agenten ist dieser Plan zusammen mit den verlinkten Style-, SEO-, Review- und CI-Regeln.
