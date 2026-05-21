# Google API Setup für Search Console & Analytics

**Ziel:** OpenClaw Agent (Viv) kann GSC & GA4 Daten abrufen für SEO-Monitoring

---

## 📋 Schritt 1: Google Cloud Project erstellen

1. Gehe zu: <https://console.cloud.google.com/>
2. Melde dich mit deinem Google-Konto an (das Zugriff auf GSC & GA4 hat)
3. Klicke oben auf **"Project auswählen"** → **"NEW PROJECT"**
4. Projektname: `future-pulse-monitoring` (oder ähnlich)
5. Klicke **"CREATE"** und warte bis das Projekt erstellt wird

---

## 📋 Schritt 2: APIs aktivieren

1. Im Google Cloud Dashboard: Menü → **"APIs & Dienste"** → **"Bibliothek"**
2. Suche nach **"Search Console API"**:
   - Klicken → **"Aktivieren"**
3. Suche nach **"Google Analytics Data API"**:
   - Klicken → **"Aktivieren"**

---

## 📋 Schritt 3: Service Account erstellen

1. Menü → **"IAM & Verwaltung"** → **"Dienstkonto"**
2. Klicke **"DIENSTKONTO ERSTELLEN"**
3. Details:
   - **Name:** `future-pulse-agent`
   - **ID:** Wird automatisch generiert (z.B. `future-pulse-agent@future-pulse-monitoring.iam.gserviceaccount.com`)
   - **Beschreibung:** "OpenClaw Agent für GSC & GA4 Monitoring"
4. Klicke **"ERSTELLEN UND FORTFAHREN"**
5. Rolle überspringen (nicht nötig) → **"FERTIG"**

---

## 📋 Schritt 4: JSON-Key erstellen

1. Klicke auf das neu erstellte Dienstkonto in der Liste
2. Tab **"SCHLÜSSEL"** → **"SCHLÜSSEL HINZUFÜGEN"** → **"Neuen Schlüssel erstellen"**
3. Typ: **JSON** auswählen
4. Klicke **"ERSTELLEN"**
5. **WICHTIG:** Die JSON-Datei wird automatisch heruntergeladen!
   - Dateiname: z.B. `future-pulse-monitoring-abc123xyz.json`
   - **Niemals commiten!** (kommt in `.gitignore`)

---

## 📋 Schritt 5: Google Search Console Zugriff geben

1. Gehe zu: <https://search.google.com/search-console>
2. Wähle deine Property: `https://future-pulse.de/`
3. Links: **Einstellungen** (Zahnrad) → **"Benutzer und Berechtigungen"**
4. Klicke **"BENUTZER HINZUFÜGEN"**
5. Gib die **Service Account E-Mail** ein:
   - Format: `future-pulse-agent@future-pulse-monitoring.iam.gserviceaccount.com`
6. Berechtigung: **"Eingeschränkt"** (nur Lesen!)
7. Klicke **"EINLADEN"**

---

## 📋 Schritt 6: Google Analytics 4 Zugriff geben

1. Gehe zu: <https://analytics.google.com/>
2. Wähle dein GA4 Property für future-pulse.de
3. Links unten: **Verwaltung** (Zahnrad)
4. Unter **"Property"** → **"Property-Zugriffsverwaltung"**
5. Klicke oben rechts **"+"** → **"Nutzer hinzufügen"**
6. Gib die **Service Account E-Mail** ein:
   - `future-pulse-agent@future-pulse-monitoring.iam.gserviceaccount.com`
7. Berechtigungen:
   - ✅ **"Viewer"** (nur Lesen)
   - ❌ KEINE Bearbeitungsrechte
8. Klicke **"HINZUFÜGEN"**

---

## 📋 Schritt 7: JSON-Key sicher speichern

1. Verschiebe die heruntergeladene JSON-Datei an einen sicheren Ort:
   ```bash
   mkdir -p /root/.openclaw/secrets/
   mv ~/Downloads/future-pulse-monitoring-*.json /root/.openclaw/secrets/google-service-account.json
   ```

2. Setze korrekte Berechtigungen:
   ```bash
   chmod 600 /root/.openclaw/secrets/google-service-account.json
   ```

3. Füge zu `.gitignore` hinzu (falls noch nicht vorhanden):
   ```bash
   echo "*.json" >> /root/.openclaw/secrets/.gitignore
   echo "secrets/" >> /root/.openclaw/workspace/.gitignore
   ```

---

## 📋 Schritt 8: Property-IDs notieren

Folgende Infos brauchen wir für die OpenClaw-Konfiguration:

| Info | Wo finden | Beispiel |
|------|-----------|----------|
| **GSC Property URL** | Search Console URL | `https://future-pulse.de/` |
| **GA4 Measurement ID** | GA4 → Verwaltung → Datenstream | `G-XXXXXXXXXX` |
| **GA4 Property ID** | GA4 → Verwaltung → Property-Einstellungen | `123456789` |
| **Service Account E-Mail** | Google Cloud → Dienstkonto | `future-pulse-agent@...iam.gserviceaccount.com` |
| **JSON-Key Pfad** | Lokaler Pfad | `/root/.openclaw/secrets/google-service-account.json` |

---

## ✅ Checkliste

- [ ] Google Cloud Project erstellt
- [ ] Search Console API aktiviert
- [ ] Google Analytics Data API aktiviert
- [ ] Service Account erstellt
- [ ] JSON-Key heruntergeladen
- [ ] GSC Zugriff für Service Account (eingeschränkt)
- [ ] GA4 Zugriff für Service Account (Viewer)
- [ ] JSON-Key sicher gespeichert (`/root/.openclaw/secrets/`)
- [ ] Property-IDs notiert

---

## 🚀 Nächste Schritte (sobald Setup fertig)

1. **Google Skill für OpenClaw erstellen** (oder bestehenden nutzen)
2. **API-Test** durchführen (GSC & GA4 Daten abrufen)
3. **Cron Jobs einrichten:**
   - Weekly SEO-Report (Montags 9:00)
   - Monthly Traffic Summary (1. des Monats)
   - Alert bei Ranking-Verlusten (>20% Drop)

---

**WICHTIG:** 
- JSON-Key **NIEMALS** ins Git-Repo committen!
- Service Account hat **NUR LESE-Zugriff** (Security First)
- Bei Fragen: Einfach im #agents Channel melden!

---

_Stand: 2026-05-18 | Erstellt für: future-pulse.de_
