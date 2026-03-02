# ðŸ“š Future Pulse Tech - Content Styleguide

**Version:** 1.0  
**Erstellungsdatum:** 16. Januar 2026  
**Autor:** Oliver Laudan & Charlotte (AI Assistant)

---

## ðŸ“‹ Ãœbersicht

Dieser Styleguide definiert alle Standards fÃ¼r Blog-Artikel auf **Future Pulse Tech**. Hier findest du:

- âœ… TonalitÃ¤t & Sprachrichtlinien
- âœ… SEO-Best Practices
- âœ… Formatierungsregeln
- âœ… Artikel-LÃ¤ngen & Strukturen

---

## ðŸŽ¯ Mission Statement

**Future Pulse Tech** vermittelt **KI-Kompetenz** und **Future Skills** auf zugÃ¤ngliche, praktische Art. Unsere Inhalte sind:

- ðŸŽ“ **Lehrreich** - Vermitteln echtes Wissen
- ðŸ’¡ **Praxisnah** - Sofort umsetzbare Tipps
- ðŸš€ **Zukunftsorientiert** - Trends & Entwicklungen
- â¤ï¸ **Menschlich** - PersÃ¶nlich & nahbar

---

## âœï¸ TonalitÃ¤t & Sprache

### Grundregeln

| Element | Regel | âŒ Falsch | âœ… Richtig |
|---------|-------|-----------|------------|
| **Ansprache** | Du-Form | "Man sollte KI nutzen" | "Du solltest KI nutzen" |
| **Ton** | Professionell & zugÃ¤nglich | "Die Implementierung von AI-Tools erfordert..." | "Um KI-Tools zu nutzen, brauchst du..." |
| **SatzlÃ¤nge** | 10-20 WÃ¶rter | SÃ¤tze mit 40+ WÃ¶rtern | Mix aus kurzen (5-10) und mittleren SÃ¤tzen |
| **Fachbegriffe** | ErklÃ¤ren | "Nutze LLMs fÃ¼r NLP" | "Large Language Models (LLMs) helfen bei Textverarbeitung" |
| **Emojis** | Sparsam (2-3 pro Abschnitt) | ðŸŽ‰ðŸš€âœ¨ðŸ’¡ðŸ”¥â¤ï¸ | ðŸŽ¯ Wichtig: ... |

### Schreibstil

**DO:**
- âœ… Aktive Sprache: "Du lernst" statt "Es wird gelernt"
- âœ… Konkrete Beispiele geben
- âœ… PersÃ¶nliche Anekdoten teilen
- âœ… Fragen stellen, um Engagement zu fÃ¶rdern
- âœ… Klare Handlungsanweisungen

**DON'T:**
- âŒ Buzzwords ohne ErklÃ¤rung
- âŒ Passive Sprache
- âŒ Zu lange SchachtelsÃ¤tze
- âŒ Akademischer Jargon
- âŒ Inhalte ohne Mehrwert

---

## ðŸ“ Strukturierung

### Ãœberschriften-Hierarchie

```markdown
# H1 - Nur Artikel-Titel (automatisch)
## H2 - Hauptabschnitte (min. 3 pro Artikel)
### H3 - Unterpunkte
#### H4 - Selten nÃ¶tig
```

**Regeln:**
- H2-Ãœberschriften: **max. 6 WÃ¶rter**, aussagekrÃ¤ftig
- Keywords natÃ¼rlich einbauen
- Nicht nummerieren (Hugo generiert Inhaltsverzeichnis)

### AbsÃ¤tze

- **Max. 3-4 SÃ¤tze** pro Absatz
- **Leerzeile** zwischen AbsÃ¤tzen
- **Mix:** Kurze + mittlere AbsÃ¤tze abwechseln

### Listen

**Wann nutzen:**
- AufzÃ¤hlungen (Bullet Points `- `)
- Schritte (Numbered Lists `1. `)
- Vergleiche

**Beispiel:**
```markdown
**Die 3 wichtigsten Schritte:**
1. **Schritt 1:** Konkrete Handlung
2. **Schritt 2:** Konkrete Handlung
3. **Schritt 3:** Konkrete Handlung
```

### Code-BlÃ¶cke

FÃ¼r technische Beispiele, Prompts, Befehle:

````markdown
```python
def hello_world():
    print("Hello Future Pulse!")
```
````

### Zitate

FÃ¼r wichtige Aussagen:

```markdown
> "KI-Kompetenz ist die wichtigste Future Skill 2026."
```

### Tabellen

FÃ¼r Vergleiche, Vor/Nachher:

```markdown
| Feature | Tool A | Tool B |
|---------|--------|--------|
| Preis   | 10â‚¬    | 20â‚¬    |
| Speed   | âš¡âš¡âš¡    | âš¡âš¡     |
```

---

## ðŸ“ Artikel-LÃ¤ngen

| Typ | Wortanzahl | Lesezeit | Verwendung |
|-----|------------|----------|------------|
| **Quick Tip** | 300-600 | 2-3 Min | Schnelle Hacks, News |
| **Standard** | 800-1500 | 5-8 Min | **Empfohlen** fÃ¼r meiste Artikel |
| **Deep Dive** | 1500-3000 | 10-15 Min | Umfassende Guides |

**Empfehlung:** **800-1500 WÃ¶rter** = Sweet Spot fÃ¼r SEO & Lesbarkeit

---

## ðŸ”‘ SEO-Best Practices

### Keyword-Platzierung

1. **Titel:** Hauptkeyword Position 1-3
2. **Meta-Description:** Hauptkeyword in ersten 120 Zeichen
3. **H2-Ãœberschriften:** 2-3 Keywords natÃ¼rlich einbauen
4. **Erster Absatz:** Hauptkeyword in ersten 100 WÃ¶rtern
5. **Alt-Texte:** Keywords in Bildbeschreibungen

### Keyword-Dichte

- âœ… **1-2%** des Hauptkeywords (bei 1000 WÃ¶rtern = 10-20x)
- âœ… **Synonyme nutzen:** "KI", "KÃ¼nstliche Intelligenz", "AI"
- âŒ **Keyword-Stuffing vermeiden**

### Meta-Description Formel

```
[Hauptkeyword] + [Benefit] + [CTA] = 150-160 Zeichen

Beispiel:
"Erfahre, wie du KI-Kompetenz entwickelst und ChatGPT souverÃ¤n nutzt. 
Praktische Tipps fÃ¼r AI Literacy 2026. Jetzt lesen!"
```

### Title-Tag Formel

```
[Hauptkeyword]: [Sprechender Titel] (max 60 Zeichen)

Beispiel:
"KI-Kompetenz: Dein praktischer Guide fÃ¼r AI Literacy"
```

---

## âœ… Checkliste vor VerÃ¶ffentlichung

### SEO
- [ ] Hauptkeyword im Titel (Position 1-3)
- [ ] Meta-Description 150-160 Zeichen
- [ ] Min. 3 H2-Ãœberschriften
- [ ] Keywords natÃ¼rlich eingebunden (1-2%)
- [ ] Alt-Texte fÃ¼r Bilder
- [ ] 2-3 interne Links
- [ ] 1-2 externe Links (hochwertige Quellen)

### Lesbarkeit
- [ ] AbsÃ¤tze max. 3-4 SÃ¤tze
- [ ] Mix kurzer & mittlerer SÃ¤tze
- [ ] Min. 1 Liste pro Artikel
- [ ] CTA am Ende
- [ ] `ShowToc: true` aktiviert

### Format
- [ ] `draft: false`
- [ ] Datum `YYYY-MM-DD`
- [ ] 3-5 Tags
- [ ] 3-5 Keywords
- [ ] Author-Feld

---

## ðŸ“ž Kontakt

**Fragen?** kontakt@future-pulse.tech

---

**Version History:**
- v1.0 (16.01.2026): Initial Release
