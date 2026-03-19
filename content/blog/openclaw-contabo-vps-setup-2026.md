---
title: "OpenClaw auf Contabo VPS: Vollständiger Setup-Guide 2026 (MiniMax + Ollama)"
date: 2026-03-02
draft: false
description: "Schritt-für-Schritt: OpenClaw AI-Agent auf Contabo VPS deployen. Von Docker-Cleanup über MiniMax Cloud bis Nginx SSL. Für Game Devs & Web Devs."
summary: "So richtest du OpenClaw – den mächtigsten Open-Source AI-Agenten – auf deinem Contabo VPS ein. Mit Terminal-Befehlen, RAM-Optimierung und Production-Ready Setup."
tags: ["AI-Agents", "VPS", "DevOps", "OpenClaw", "Contabo"]
keywords: ["OpenClaw VPS Setup", "Contabo AI Agent", "MiniMax Cloud", "Ollama VPS", "AI Agent Deployment"]
author: "Oliver Laudan"
ShowToc: true
TocOpen: true
cover:
    image: "https://user-gen-media-assets.s3.amazonaws.com/seedream_images/3e0324ac-a549-4bdd-8ec8-b6ca39740321.png"
    alt: "OpenClaw AI Agent Deployment on VPS - Terminal and Server Infrastructure"
    caption: "OpenClaw auf Contabo VPS: Von Docker-Cleanup bis Production-Ready"
---

Heute richte ich **OpenClaw** – den mächtigsten Open-Source AI-Agenten – auf meinem Contabo VPS ein. Von RAM-Krisen bis Tool-Calling: Der komplette Weg mit kopierbaren Terminal-Befehlen[cite:9].

OpenClaw erreicht 80,2% auf SWE-Bench (Claude-Niveau) und läuft komplett selbstgehostet. Du lernst, wie du ihn mit **MiniMax Cloud** (kostenlos) oder **Ollama** (lokal) betreibst – optimiert für VPS-Umgebungen mit 8–16 GB RAM[cite:9].

## Was du lernen wirst

In diesem Tutorial zeige ich dir:
- ✅ Clean Docker + VPS-Vorbereitung für OpenClaw
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

**Lokale Setups** stoßen schnell an Grenzen: Laptop schläft ein, lokale Firewall blockiert Webhooks, oder du willst remote auf den Agenten zugreifen[cite:9]. Ein VPS löst das – mit diesen Vorteilen:

- **24/7 Verfügbarkeit** für autonome Tasks
- **Skalierbare Ressourcen** (RAM-Upgrade ohne Neuinstall)
- **Öffentlicher Zugriff** via Domain (z.B. `agent.future-pulse.tech`)
- **Kosteneffizienz** (Contabo VPS S: ~€6/Monat)

**Beispiel:**
> Du entwickelst ein Indie-Game und willst, dass OpenClaw nachts automatisch Dokumentation generiert oder Bug-Reports analysiert – ohne dass dein Rechner läuft[cite:9].

---

## Schritt 1: Clean Docker + VPS

### Was du tust:
Alte Docker-Container und Volumes löschen, um Speicherplatz freizugeben und Konflikte zu vermeiden.

### So geht's:

```bash
# Docker komplett aufräumen (ACHTUNG: Löscht ALLE Container/Volumes)
docker system prune -a --volumes -f

# OpenClaw-Verzeichnis löschen (falls vorhanden)
rm -rf /opt/openclaw
```

**💡 Tipp:** Prüfe vorher mit `docker ps -a`, ob wichtige Container laufen. Der Befehl ist destruktiv[cite:9]!

**⚠️ Häufiger Fehler:** Vergessen, alte Volumes zu löschen → neue Installation greift auf alte Configs zu → merkwürdige Fehler[cite:9].

---

## Schritt 2: OpenClaw installieren

### Was du tust:
OpenClaw global via npm installieren und Health-Check durchführen.

### So geht's:

```bash
# Node.js 18+ muss installiert sein (prüfen mit: node -v)
npm i -g openclaw@latest

# Automatische Diagnose & Fixes
openclaw doctor --fix
```

**Beispiel-Output:**
```
✓ Node.js version OK (v20.11.0)
✓ Docker installed
✓ Ports 3000, 8080 available
✓ RAM: 16 GB (recommended: 8+ GB)
```

**💡 Tipp:** `openclaw doctor` zeigt fehlende Dependencies (z.B. Docker). Folge den Anweisungen zur Installation[cite:9].

**⚠️ Häufiger Fehler:** Node.js < 18 → Update via `nvm install 20`[cite:9].

---

## Schritt 3: MiniMax Cloud konfigurieren

### Was du tust:
OpenClaw auf **MiniMax Cloud** (kostenlos, 1–5M Tokens/Monat) umstellen statt lokales Ollama. Spart RAM und ist sofort produktiv[cite:9].

### So geht's:

```bash
# Primäres Modell auf MiniMax Cloud setzen
openclaw config set agents.defaults.model.primary '{
  "provider": "minimax-cloud",
  "model": "minimax-m2.5:cloud"
}'

# OpenClaw neu starten
openclaw restart
```

**Warum MiniMax?**
- **Free Tier:** 1–5M Tokens/Monat (reicht für 50–100 komplexe Tasks)[cite:9]
- **SWE-Bench:** 80,2% (vergleichbar mit Claude 3.5 Sonnet)[cite:9]
- **Kosten danach:** €0,30–1,20/Million Tokens[cite:9]

**💡 Tipp:** Für 100% self-hosted → weiter zu Schritt 6 (Ollama-Setup)[cite:9].

**⚠️ Häufiger Fehler:** API-Key vergessen → `openclaw config set minimax.api_key YOUR_KEY`[cite:9].

---

## Schritt 4: Nginx + SSL einrichten

### Was du tuts:
Reverse Proxy mit SSL, damit OpenClaw über `https://agent.future-pulse.tech` erreichbar ist[cite:9].

### So geht's:

```bash
# Nginx & Certbot installieren
apt update && apt install nginx certbot python3-certbot-nginx -y

# SSL-Zertifikat generieren (ersetze Domain)
certbot --nginx -d agent.future-pulse.tech

# Nginx Config für OpenClaw
cat > /etc/nginx/sites-available/openclaw <<EOF
server {
    listen 80;
    server_name agent.future-pulse.tech;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name agent.future-pulse.tech;

    ssl_certificate /etc/letsencrypt/live/agent.future-pulse.tech/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/agent.future-pulse.tech/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Symlink erstellen & Nginx neuladen
ln -s /etc/nginx/sites-available/openclaw /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

**💡 Tipp:** Port 3000 ist OpenClaws Default-Gateway-Port. Überprüfe mit `openclaw gateway start`[cite:9].

**⚠️ Häufiger Fehler:** Firewall blockiert Port 80/443 → `ufw allow 'Nginx Full'`[cite:9].

---

## Häufige Probleme & Lösungen

| Problem | Ursache | Lösung |
|---------|---------|--------|
| **RAM voll (10+ GB)** | Ollama lädt zu große Modelle | `ollama list` → kleineres Modell (z.B. `gemma2:2b`) oder MiniMax Cloud nutzen[cite:9] |
| **Tools Error** | Tool-Calling nicht unterstützt | `openclaw config set agents.tools.enabled false`[cite:9] |
| **Context 8192 < 16k** | Modell-Default zu klein | MiniMax Cloud oder `OLLAMA_NUM_CTX=32768`[cite:9] |
| **Gateway Port 3000 belegt** | OpenClaw läuft bereits | `openclaw gateway start` dann `openclaw serve start`[cite:9] |

---

## Performance-Benchmarks (Contabo VPS)

**VPS S (8 vCPU, 16 GB RAM):**
- **Gemma2:2b** (Ollama lokal): ~40 Tokens/Sekunde
- **Llama3.1:8b** (Ollama lokal): ~15 Tokens/Sekunde
- **MiniMax Cloud**: ~80 Tokens/Sekunde (API-Latenz ~200ms)[cite:9]

**VPS M (10 vCPU, 24 GB RAM):**
- **Llama3.1:8b**: ~25 Tokens/Sekunde
- **Mixtral 8x7B**: ~8 Tokens/Sekunde (RAM-intensiv)[cite:9]

**Empfehlung:** Für Production → MiniMax Cloud (schneller, kostenlos bis 5M Tokens). Für Datenschutz-kritische Projekte → Ollama lokal mit Gemma2:2b[cite:9].

---

## Nächste Schritte

**Glückwunsch!** 🎉 Du hast OpenClaw auf deinem VPS produktiv am Laufen.

**Was du erreicht hast:**
1. ✅ Clean VPS-Umgebung vorbereitet
2. ✅ OpenClaw mit npm installiert
3. ✅ MiniMax Cloud integriert (Free Tier)
4. ✅ SSL-gesicherten Zugriff via Nginx eingerichtet

**Wie geht's weiter?**
- **Contabo RAM-Upgrade** (Live Migration ohne Downtime)[cite:9]
- **Pterodactyl Game Panel** für `dungeon.future-pulse.tech` deployen[cite:9]
- **Grafana Monitoring** für OpenClaw-Metrics aufsetzen[cite:9]

---

**💬 Läuft OpenClaw bei dir?**

Welches Modell nutzt du – MiniMax Cloud oder Ollama lokal? Teile deine Erfahrungen in den Kommentaren[cite:9]!

## Meta Description
Richte OpenClaw auf deinem Contabo VPS ein – mit MiniMax Cloud (kostenlos) oder Ollama. Der komplette Setup-Guide mit Terminal-Befehlen.

## FAQ

**Brauche ich zwingend einen VPS oder reicht ein lokaler Rechner?**
Ein lokaler Rechner reicht für Experimente, aber ein VPS bietet 24/7-Verfügbarkeit, Remote-Zugriff und kein Laptop, das in den Ruhezustand geht.

**Was kostet MiniMax Cloud – gibt es ein kostenloses Kontingent?**
Ja, das Free Tier umfasst 1–5 Millionen Tokens pro Monat – ausreichend für 50–100 komplexe Aufgaben. Danach fallen ca. €0,30–1,20 pro Million Tokens an.

**Welche VPS-Konfiguration empfiehlst du?**
Für die meisten Anwender reicht Contabo VPS S (8 vCPU, 16 GB RAM). Wer mit lokalen Ollama-Modellen wie Llama3.1:8b oder Mixtral arbeiten will, sollte VPS M (24 GB RAM) wählen.

**Ich habe bereits Docker-Container laufen – kann ich OpenClaw trotzdem installieren?**
Ja, OpenClaw nutzt Docker nicht zwingend. Stelle aber sicher, dass genügend RAM verfügbar ist und der Port 3000 nicht von anderen Diensten belegt wird.

**📌 Weiterführende Ressourcen:**
- [OpenClaw GitHub Repo](https://github.com/openclaw/openclaw)
- [MiniMax Cloud API Docs](https://www.minimaxi.com/document/guides/chat-v2)
- [Contabo VPS Preise](https://contabo.com/en/vps/)
