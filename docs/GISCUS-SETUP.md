# 📋 Giscus Kommentar-System - Setup-Anleitung

**Stand:** 19. Januar 2026  
**Status:** ⚠️ WICHTIG - Category-ID muss noch angepasst werden!

---

## 🔴 Was du noch tun musst:

### Schritt 1: GitHub Discussions aktivieren

1. **Gehe zu:** https://github.com/oliverlaudan-ops/future-pulse-de/settings
2. **Scrolle runter zu "Features"**
3. **Aktiviere:** ☑️ **Discussions**
4. **Fertig!**

---

### Schritt 2: Richtige Category-ID holen

Die aktuelle `data-category-id` in `comments.html` ist ein **Platzhalter**!

**So holst du die ECHTE ID:**

1. **Gehe zu:** https://giscus.app
2. **Fülle aus:**
   - **Repository:** `oliverlaudan-ops/future-pulse-de`
   - **Page ↔️ Discussions Mapping:** Wähle `pathname` (bereits richtig)
   - **Discussion Category:** Wähle `Announcements` (oder erstelle "Blog Comments")
   
3. **Scroll runter** - Du siehst generierten Code:
   ```html
   data-category-id="DIC_kwDOQ7ETsM4XXXXXX"
   ```

4. **Kopiere diese ID** (beginnt mit `DIC_`)

5. **Ersetze in `layouts/partials/comments.html`** diese Zeile:
   ```html
   data-category-id="DIC_kwDOQ7ETsM4ClRKQ"
   ```
   mit deiner echten ID

---

### Schritt 3: Datei aktualisieren

**Option A: Via GitHub Web Interface**
1. Gehe zu: https://github.com/oliverlaudan-ops/future-pulse-de/blob/main/layouts/partials/comments.html
2. Klicke auf "Edit" (Stift-Symbol)
3. Ersetze die `data-category-id` Zeile
4. Commit mit Message: "Fix: Update Giscus Category-ID"

**Option B: Via Git (lokal)**
```bash
# Datei bearbeiten
vim layouts/partials/comments.html
# Oder mit deinem bevorzugten Editor

# Commit & Push
git add layouts/partials/comments.html
git commit -m "Fix: Update Giscus Category-ID"
git push origin main
```

---

## ✅ Was bereits funktioniert:

- ✅ `comments = true` in hugo.toml
- ✅ Giscus-Script eingebunden
- ✅ `data-repo` korrekt
- ✅ `data-repo-id` korrekt
- ✅ Deutsche Sprache (`data-lang="de"`)
- ✅ Dark/Light Mode Auto-Switch
- ✅ Lazy Loading
- ✅ Reactions aktiviert
- ✅ **`data-emit-metadata="0"`** korrigiert
- ✅ Verbessertes Layout mit Styling

---

## 🎯 Nach dem Update testen:

1. **Baue die Seite neu:**
   ```bash
   hugo server -D
   ```

2. **Öffne einen Blog-Artikel**
3. **Scroll runter** - Du solltest das Giscus-Widget sehen
4. **Teste Kommentar** (benötigt GitHub-Login)

---

## 🔧 Fehlerbehebung

**Problem:** Kommentare erscheinen nicht  
**Lösung:**
- Prüfe: Discussions aktiviert?
- Prüfe: Category-ID korrekt?
- Leere Browser-Cache
- Prüfe Browser-Konsole (F12) auf Fehler

**Problem:** "Unable to find category"  
**Lösung:**
- Category-ID ist falsch
- Gehe zu giscus.app und hole neue ID

**Problem:** Kommentare werden nicht geladen  
**Lösung:**
- Prüfe: Repository ist öffentlich?
- Prüfe: Giscus App hat Zugriff auf Repo?
- Installiere Giscus App: https://github.com/apps/giscus

---

## 📚 Weitere Anpassungen (Optional)

### Eigene Discussion Category erstellen

1. Gehe zu: https://github.com/oliverlaudan-ops/future-pulse-de/discussions/categories
2. Klicke: "New category"
3. Name: "Blog Comments"
4. Description: "Kommentare zu Blog-Artikeln"
5. Format: "Announcement" (empfohlen)
6. Speichern
7. Neue Category-ID von giscus.app holen

### Theme anpassen

In `comments.html` kannst du das Theme ändern:

```html
data-theme="preferred_color_scheme"  <!-- Auto Dark/Light -->
data-theme="light"                   <!-- Immer Hell -->
data-theme="dark"                    <!-- Immer Dunkel -->
data-theme="transparent_dark"        <!-- Transparent Dunkel -->
```

### Position ändern

```html
data-input-position="top"    <!-- Eingabefeld oben -->
data-input-position="bottom" <!-- Eingabefeld unten (Standard) -->
```

---

## 📦 Was wurde korrigiert?

### Vorher (Fehler):
```html
data-category-id="1"          ❌ Platzhalter
data-emit-metadata="1"        ❌ Nicht empfohlen
<div id="comments">           ❌ Kein Styling
```

### Nachher (Korrigiert):
```html
data-category-id="DIC_kwDOQ7ETsM4ClRKQ"  ⚠️ Muss noch ersetzt werden!
data-emit-metadata="0"                    ✅ Korrigiert
<div id="comments" style="...">           ✅ Mit Styling
```

---

## 📞 Kontakt

Bei Problemen: kontakt@future-pulse.de

---

**✨ Viel Erfolg, Oliver!**

---

## 🔗 Nützliche Links

- Giscus Konfiguration: https://giscus.app
- Giscus GitHub: https://github.com/giscus/giscus
- Giscus Dokumentation: https://github.com/giscus/giscus/blob/main/ADVANCED-USAGE.md
- Hugo PaperMod Docs: https://github.com/adityatelange/hugo-PaperMod/wiki
