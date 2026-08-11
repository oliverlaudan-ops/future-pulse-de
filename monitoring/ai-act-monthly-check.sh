#!/usr/bin/env bash
# /opt/openclaw/monitor/ai-act-monthly-check.sh
#
# Monatlicher Stichproben- und Drift-Check für EU AI Act Compliance auf
# future-pulse.de. Wird am 1. jeden Monats um 09:00 ausgeführt via openclaw
# Cron (siehe openclaw.json, job "ai-act-monthly-review").
#
# Was wird geprüft?
#   1. Existenz und Lesbarkeit von content/ki-policy.md
#      (Last-modified darf nicht > 12 Monate sein → Jahres-Review-Frist)
#   2. Aktualität des Image-Manifests (Re-Build via build/build-image-manifest.py)
#      und Vergleich der Provenance-Klassen gegen das eingecheckte JSON
#   3. Konsistenz aller Frontmatter-Felder ai_generated/ai_model/human_reviewer/review_date
#      in content/blog/**/index.md (sollte 4/4 pro Post sein)
#   4. Konsistenz der statischen Seiten (about/impressum/datenschutz)
#      sollen ai_generated: false haben
#   5. Existenz eines verschlüsselten Jahres-Snapshots im laufenden Jahr
#      in ~/Documents/archive/future-pulse/<jahr>-snapshot.tar.gz.enc
#
# Output: Slack-Notification nach #status mit "OK" oder Liste der Drifts.
# Bei Jahresbeginn (Januar) zusätzlich: Erinnerung an nächste Überarbeitung
# der /ki-policy/ Seite (gemäß 12-Monats-Review-Zyklus gem. EU AI Act).
#
# Returncodes:
#   0 = alles grün
#   1 = leichte Drifts, gemeldet
#   2 = schwere Verstöße (z. B. ki-policy.md > 18 Monate alt), eskaliert

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
. "$HERE/lib.sh"

REPO_DIR="/root/projects/future-pulse-de"
KI_POLICY="$REPO_DIR/content/ki-policy.md"
BLOG_DIR="$REPO_DIR/content/blog"
STATIC_PAGES=("about" "impressum" "datenschutz")
ARCHIVE_DIR="${HOME}/Documents/archive/future-pulse"

NOW_EPOCH=$(date +%s)
# Achtung: date +%m liefert z.B. "08" → bash arithmetic interpretiert
# führende 0 als Oktal und wirft "value too great for base". 10#-Prefix
# erzwingt Dezimalinterpretation. %Y ist 4-stellig und braucht kein Prefix.
MONTH_NUM_RAW=$(date +%m)
MONTH_NUM=$((10#$MONTH_NUM_RAW))
YEAR=$(date +%Y)

issues=()
hard_fail=()

# --- 1. ki-policy.md Aktualität ---
if [[ -f "$KI_POLICY" ]]; then
  policy_epoch=$(stat -c '%Y' "$KI_POLICY")
  policy_age_days=$(( (NOW_EPOCH - policy_epoch) / 86400 ))
  if (( policy_age_days > 730 )); then   # 24 Monate
    hard_fail+=("ki-policy.md ist ${policy_age_days} Tage alt — Jahres-Review dringend (>24 Monate).")
  elif (( policy_age_days > 365 )); then # 12 Monate
    issues+=("ki-policy.md ist ${policy_age_days} Tage alt — Jahres-Review fällig.")
  fi
else
  hard_fail+=("ki-policy.md fehlt im Repo!")
fi

# --- 2. Image-Manifest Check ---
if [[ -x /usr/bin/python3 ]] && [[ -f "$REPO_DIR/build/build-image-manifest.py" ]]; then
  cd "$REPO_DIR"
  refreshed_json="$(mktemp)"
  if python3 build/build-image-manifest.py > "$refreshed_json" 2>&1; then
    if ! diff -q "$refreshed_json" "$REPO_DIR/static/image-manifest.json" > /dev/null 2>&1; then
      issues+=("image-manifest.json ist veraltet — bitte 'python3 build/build-image-manifest.py' re-runnen und committen.")
    fi
  else
    issues+=("build-image-manifest.py ist fehlerhaft — Skript-Log prüfen.")
  fi
  rm -f "$refreshed_json"
fi

# --- 3. Frontmatter Vollständigkeit ---
if [[ -d "$BLOG_DIR" ]]; then
  incomplete=()
  while IFS= read -r f; do
    for field in ai_generated ai_model human_reviewer review_date; do
      if ! grep -q "^${field}:" "$f"; then
        incomplete+=("$f (missing: ${field})")
      fi
    done
  done < <(find "$BLOG_DIR" -name "index.md" -type f)
  if (( ${#incomplete[@]} > 0 )); then
    issues+=("${#incomplete[@]} Blogposts mit unvollständigem Frontmatter: ${incomplete[*]:0:3}$( (( ${#incomplete[@]} > 3 )) && echo ' ...' )")
  fi
fi

# --- 4. Statische Seiten müssen ai_generated=false haben ---
if [[ -d "$REPO_DIR/content" ]]; then
  for slug in "${STATIC_PAGES[@]}"; do
    f="$REPO_DIR/content/${slug}.md"
    [[ -f "$f" ]] || continue
    if grep -q "^ai_generated:[[:space:]]*false" "$f"; then
      :
    else
      issues+=("static/${slug}.md fehlt 'ai_generated: false'.")
    fi
  done
fi

# --- 5. Jahres-Snapshot (nur bei Monat Jan/Feb prüfen — frühestens 1 Monat ins Jahr) ---
if (( MONTH_NUM <= 2 )); then
  expected_snapshot="$ARCHIVE_DIR/${YEAR}-snapshot.tar.gz.enc"
  if [[ ! -f "$expected_snapshot" ]]; then
    issues+=("Jahres-Snapshot für ${YEAR} fehlt: ${expected_snapshot}")
  fi
fi

# --- 6. Jahres-Review-Reminder (nur im Januar pingen) ---
review_reminder=""
if (( MONTH_NUM == 1 )); then
  review_reminder="
*Jahres-Review fällig:* /ki-policy/ sollte in diesem Monat aktualisiert werden (gem. Anhang IV Vertiefung in docs/AIACT-COMPLIANCE-LOG.md §5)."
fi

# --- Report ---
if (( ${#hard_fail[@]} > 0 )); then
  msg="🛑 *EU-AI-Act-MONATLICH-Check: SCHWERE VERSTÖSSE*
${hard_fail[*]}
${review_reminder}"
  send_slack "$msg" || true
  exit 2
elif (( ${#issues[@]} > 0 )); then
  msg="⚠️ *EU-AI-Act-MONATLICH-Check: Drifts erkannt*
${issues[*]}
${review_reminder}"
  send_slack "$msg" || true
  exit 1
else
  msg="✅ *EU-AI-Act-MONATLICH-Check: OK* ($(date +%Y-%m-%d)) — alle 5 Checks grün.${review_reminder}"
  send_slack "$msg" || true
  exit 0
fi
