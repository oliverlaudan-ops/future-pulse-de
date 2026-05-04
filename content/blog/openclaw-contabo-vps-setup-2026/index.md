---
title: "OpenClaw auf Contabo VPS: Vollständiger Setup-Guide 2026 (MiniMax + Ollama)"
date: 2026-03-02
draft: false
description: "Schritt-für-Schritt: OpenClaw AI-Agent auf Contabo VPS deployen. Von der Installation über MiniMax Cloud bis Nginx SSL. Für Game Devs & Web Devs."
summary: "So richtest du OpenClaw – den mächtigsten Open-Source AI-Agenten – auf deinem Contabo VPS ein. Mit Terminal-Befehlen, RAM-Optimierung und Production-Ready Setup."
tags: ["AI-Agents", "VPS", "DevOps", "OpenClaw", "Contabo"]
keywords: ["OpenClaw VPS Setup", "Contabo AI Agent", "MiniMax Cloud", "Ollama VPS", "AI Agent Deployment"]
author: "Oliver Laudan"
ShowToc: true
TocOpen: true
cover:
    image: "https://user-gen-media-assets.s3.amazonaws.com/seedream_images/3e0324ac-a549-4bdd-8ec8-b6ca39740321.png"
    alt: "OpenClaw AI Agent Deployment on VPS - Terminal and Server Infrastructure"
    caption: "OpenClaw auf Contabo VPS: Von der Installation bis Production-Ready"
---

Heute richte ich **OpenClaw** – den mächtigsten Open-Source AI-Agenten – auf meinem Contabo VPS ein. Von der Installation bis zum Production-Setup: Der komplette Weg mit kopierbaren Terminal-Befehlen.

OpenClaw erreicht 80,2% auf SWE-Bench (Claude-Niveau) und läuft komplett selbstgehostet. Du lernst, wie du ihn mit **MiniMax Cloud** (kostenlos) oder **Ollama** (lokal) betreibst – optimiert für VPS-Umgebungen mit 8–16 GB RAM.

## Was du lernen wirst

In diesem Tutorial zeige ich dir:
- ✅ VPS-Vorbereitung für OpenClaw (Node.js, Dependencies)
- ✅ OpenClaw Installation mit npm (latest version)
- ✅ MiniMax Cloud Integration (Free Tier, sofort produktiv)
- ✅ Nginx + SSL-Setup für sicheren Zugriff
- ✅ RAM-Optimierung & häufige Fehler beheben

**Voraussetzungen:** 
- Contabo VPS (S oder M) mit Ubuntu 22.04+
- Root-Zugriff via SSH
- Domain für SSL (optional, aber empfohlen)

**Geschätzte Dauer:** 30–45 Minuten

**Schwierigkeitsgrad:** Fortgeschritten (Erfahrung mit Linux-Terminal hilfreich)

---

## Warum OpenClaw auf VPS?

**Lokale Setups** stoßen schnell an Grenzen: Laptop schläft ein, lokale Firewall blockiert Webhooks, oder du willst remote auf den Agenten zugreifen. Ein VPS löst das – mit diesen Vorteilen:

- **24/7 Verfügbarkeit** für autonome Tasks
- **Skalierbare Ressourcen** (RAM-Upgrade ohne Neuinstall)
- **Öffentlicher Zugriff** via Domain (z.B. `agent.future-pulse.de`)
- **Kosteneffizienz** (Contabo VPS S: ~€6/Monat)

**Beispiel:**
> Du entwickelst ein Indie-Game und willst, dass OpenClaw nachts automatisch Dokumentation generiert oder Bug-Reports analysiert – ohne dass dein Rechner läuft.

---

## Schritt 1: VPS vorbereiten

### Was du tust:
Node.js und grundlegende Dependencies installieren.

### So geht's:

```bash
# System aktualisieren
apt update && apt upgrade -y

# Node.js 22+ installieren (über NodeSource)
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs

# Version prüfen
node -v  # Sollte v22.x.x anzeigen
npm -v
```

**💡 Tipp:** OpenClaw benötigt Node.js 22 oder höher. Die Ubuntu-Standardversion ist oft zu alt.

**⚠️ Häufiger Fehler:** Node.js < 22 → Installation schlägt fehl. Immer die aktuelle LTS-Version nutzen.

---

## Schritt 2: OpenClaw installieren

### Was du tust:
OpenClaw global via npm installieren und Health-Check durchführen.

### So geht's:

```bash
# OpenClaw global installieren
npm i -g openclaw@latest

# Automatische Diagnose & Fixes
openclaw doctor --repair
```

**Beispiel-Output:**
```
✓ Node.js version OK (v22.22.2)
✓ Workspace erstellt
✓ Config validiert
✓ Plugins geladen
```

**💡 Tipp:** `openclaw doctor --repair` zeigt und behebt häufige Probleme wie fehlende Dependencies oder veraltete Configs.

**⚠️ Häufiger Fehler:** Permission-Probleme bei npm → `npm config set prefix ~/.npm-global` und PATH anpassen.

---

## Schritt 3: OpenClaw Gateway starten

### Was du tust:
Das Gateway ist das Herzstück von OpenClaw – es verwaltet Agents, Tools und Verbindungen.

### So geht's:

```bash
# Gateway als systemd-Service starten (empfohlen)
openclaw gateway start

# Status prüfen
openclaw gateway status
```

**Output bei erfolgreichem Start:**
```
Runtime: running (pid 12345, state active)
Connectivity probe: ok
Listening: 127.0.0.1:18789
```

**Standard-Port:** 18789 (loopback, nur lokal erreichbar)

**💡 Tipp:** Das Gateway läuft im Hintergrund als systemd-Service und startet automatisch nach einem Reboot.

**⚠️ Häufiger Fehler:** Port 18789 bereits belegt → `openclaw gateway stop` dann neu starten.

---

## Schritt 4: MiniMax Cloud konfigurieren

### Was du tust:
OpenClaw auf **MiniMax Cloud** (kostenlos, 1–5M Tokens/Monat) umstellen statt lokales Ollama. Spart RAM und ist sofort produktiv.

### So geht's:

1. **API-Key besorgen:** Unter [MiniMax Cloud Console](https://www.minimaxi.com/) registrieren und API-Key erstellen.

2. **Config anpassen:** Die OpenClaw-Config liegt unter `~/.openclaw/openclaw.json`:

```bash
# Editor öffnen
nano ~/.openclaw/openclaw.json
```

3. **Modell-Konfiguration** im `models`-Abschnitt hinzufügen:

```json
{
  "models": {
    "providers": {
      "minimax": {
        "api": "minimax",
        "apiKey": "DEIN_API_KEY_HIER",
        "baseUrl": "https://api.minimaxi.com/v1",
        "models": [
          {
            "id": "minimax-m2.5:cloud",
            "contextWindow": 262144,
            "cost": {"input": 0, "output": 0}
          }
        ]
      }
    }
  }
}
```

4. **Gateway neu starten:**

```bash
openclaw gateway restart
```

**Warum MiniMax?**
- **Free Tier:** 1–5M Tokens/Monat (reicht für 50–100 komplexe Tasks)
- **SWE-Bench:** 80,2% (vergleichbar mit Claude 3.5 Sonnet)
- **Kosten danach:** €0,30–1,20/Million Tokens
- **Kein RAM-Verbrauch** auf deinem VPS

**💡 Tipp:** Für 100% self-hosted → weiter zu Schritt 6 (Ollama-Setup).

**⚠️ Häufiger Fehler:** API-Key falsch eingetragen → Config mit `openclaw doctor` validieren.

---

## Schritt 5: Nginx + SSL einrichten

### Was du tust:
Reverse Proxy mit SSL, damit OpenClaw über `https://agent.future-pulse.de` erreichbar ist.

### So geht's:

```bash
# Nginx & Certbot installieren
apt update && apt install nginx certbot python3-certbot-nginx -y

# SSL-Zertifikat generieren (ersetze Domain)
certbot --nginx -d agent.future-pulse.de

# Nginx Config für OpenClaw
cat > /etc/nginx/sites-available/openclaw <<EOF
server {
    listen 80;
    server_name agent.future-pulse.de;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name agent.future-pulse.de;

    ssl_certificate /etc/letsencrypt/live/agent.future-pulse.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/agent.future-pulse.de/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:18789;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket Support für OpenClaw
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Symlink erstellen & Nginx neuladen
ln -s /etc/nginx/sites-available/openclaw /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

**💡 Tipp:** Port **18789** ist OpenClaws Standard-Gateway-Port. Nicht 3000 verwenden!

**⚠️ Häufiger Fehler:** Firewall blockiert Port 80/443 → `ufw allow 'Nginx Full' && ufw reload`.

---

## Schritt 6 (Optional): Ollama für lokale Modelle

### Was du tust:
Statt MiniMax Cloud kannst du Ollama für lokale KI-Modelle nutzen – komplett offline und datenschutzkonform.

### So geht's:

```bash
# Ollama installieren
curl -fsSL https://ollama.com/install.sh | sh

# Modell herunterladen (klein: gemma2:2b, mittel: llama3.1:8b)
ollama pull gemma2:2b

# Ollama als Service starten
systemctl enable ollama && systemctl start ollama

# Status prüfen
ollama list
```

**Empfohlene Modelle für VPS:**

| Modell | RAM | Speed | Qualität |
|--------|-----|-------|----------|
| `gemma2:2b` | 2 GB | ~40 tok/s | Gut für einfache Tasks |
| `llama3.1:8b` | 8 GB | ~15 tok/s | Sehr gut, Allrounder |
| `mixtral:8x7b` | 24 GB | ~8 tok/s | Exzellent, RAM-intensiv |

**OpenClaw mit Ollama verbinden:**

In `~/.openclaw/openclaw.json` den Ollama-Provider konfigurieren:

```json
{
  "models": {
    "providers": {
      "ollama": {
        "api": "ollama",
        "baseUrl": "http://127.0.0.1:11434",
        "models": [
          {
            "id": "gemma2:2b",
            "contextWindow": 8192
          }
        ]
      }
    }
  }
}
```

**💡 Tipp:** Für Production mit Ollama → mindestens 16 GB RAM einplanen.

**⚠️ Häufiger Fehler:** Zu großes Modell für verfügbaren RAM → VPS crasht. Lieber klein anfangen.

---

## Häufige Probleme & Lösungen

| Problem | Ursache | Lösung |
|---------|---------|--------|
| **RAM voll (10+ GB)** | Ollama lädt zu große Modelle | Kleineres Modell (z.B. `gemma2:2b`) oder MiniMax Cloud nutzen |
| **Gateway Port 18789 belegt** | OpenClaw läuft bereits | `openclaw gateway stop` dann `openclaw gateway start` |
| **API Error (MiniMax)** | API-Key fehlt/ungültig | Key in `openclaw.json` prüfen, `openclaw doctor` ausführen |
| **Nginx 502 Bad Gateway** | OpenClaw Gateway läuft nicht | `openclaw gateway status` prüfen, ggf. neu starten |
| **WebSocket disconnect** | Nginx Config fehlt Upgrade-Header | Proxy-Config um `proxy_set_header Upgrade` erweitern |

---

## Performance-Benchmarks (Contabo VPS)

**VPS S (8 vCPU, 16 GB RAM):**
- **Gemma2:2b** (Ollama lokal): ~40 Tokens/Sekunde
- **Llama3.1:8b** (Ollama lokal): ~15 Tokens/Sekunde
- **MiniMax Cloud**: ~80 Tokens/Sekunde (API-Latenz ~200ms)

**VPS M (10 vCPU, 24 GB RAM):**
- **Llama3.1:8b**: ~25 Tokens/Sekunde
- **Mixtral 8x7B**: ~8 Tokens/Sekunde (RAM-intensiv)

**Empfehlung:** Für Production → MiniMax Cloud (schneller, kostenlos bis 5M Tokens). Für Datenschutz-kritische Projekte → Ollama lokal mit Gemma2:2b.

---

## Nächste Schritte

**Glückwunsch!** 🎉 Du hast OpenClaw auf deinem VPS produktiv am Laufen.

**Was du erreicht hast:**
1. ✅ VPS mit Node.js 22 vorbereitet
2. ✅ OpenClaw installiert und Gateway gestartet
3. ✅ MiniMax Cloud oder Ollama integriert
4. ✅ SSL-gesicherten Zugriff via Nginx eingerichtet

**Wie geht's weiter?**
- **Discord/Telegram-Integration** für Chat-Befehle
- **Cron-Jobs** für automatisierte Tasks (z.B. tägliche Health-Checks)
- **Grafana Monitoring** für OpenClaw-Metrics aufsetzen

---

**💬 Läuft OpenClaw bei dir?**

Welches Modell nutzt du – MiniMax Cloud oder Ollama lokal? Teile deine Erfahrungen in den Kommentaren!

## Meta Description
Richte OpenClaw auf deinem Contabo VPS ein – mit MiniMax Cloud (kostenlos) oder Ollama. Der komplette Setup-Guide mit Terminal-Befehlen.

## FAQ

**Brauche ich zwingend einen VPS oder reicht ein lokaler Rechner?**
Ein lokaler Rechner reicht für Experimente, aber ein VPS bietet 24/7-Verfügbarkeit, Remote-Zugriff und kein Laptop, der in den Ruhezustand geht.

**Was kostet MiniMax Cloud – gibt es ein kostenloses Kontingent?**
Ja, das Free Tier umfasst 1–5 Millionen Tokens pro Monat – ausreichend für 50–100 komplexe Aufgaben. Danach fallen ca. €0,30–1,20 pro Million Tokens an.

**Welche VPS-Konfiguration empfiehlst du?**
Für die meisten Anwender reicht Contabo VPS S (8 vCPU, 16 GB RAM). Wer mit lokalen Ollama-Modellen wie Llama3.1:8b oder Mixtral arbeiten will, sollte VPS M (24 GB RAM) wählen.

**Kann ich OpenClaw mit Docker betreiben?**
OpenClaw kann mit Docker betrieben werden, läuft aber auch nativ als systemd-Service. Die Docker-Variante ist nützlich für isolierte Umgebungen oder wenn du mehrere OpenClaw-Instanzen parallel betreiben willst.

**📌 Weiterführende Ressourcen:**
- [OpenClaw GitHub Repo](https://github.com/openclaw/openclaw)
- [OpenClaw Dokumentation](https://docs.openclaw.ai)
- [MiniMax Cloud API Docs](https://www.minimaxi.com/document/guides/chat-v2)
- [Contabo VPS Preise](https://contabo.com/en/vps/)
- [Ollama Modell-Bibliothek](https://ollama.com/library)
