#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# VulnMart Deployment Script
# WSL -> VPS
#
# WSL:
#   ~/vulnmart
#
# VPS:
#   /home/ctfadmin/vulnmart   (staging copy)
#   /opt/vulnmart             (production)
#
# IMPORTANT:
# - docker-compose.yml is NOT synced because WSL uses dev config.
# - VPS database is NOT overwritten.
# ============================================================

REMOTE_USER="ctfadmin"
REMOTE_HOST="103.55.37.141"

REMOTE_STAGING="/home/ctfadmin/vulnmart"
REMOTE_APP="/opt/vulnmart"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "        VulnMart Deployment"
echo "=========================================="
echo
echo "Local : $PROJECT_DIR"
echo "Remote: $REMOTE_HOST:$REMOTE_APP"
echo

# ------------------------------------------------------------
# 1. Check required commands
# ------------------------------------------------------------

command -v rsync >/dev/null 2>&1 || {
    echo "[ERROR] rsync tidak ditemukan."
    exit 1
}

command -v ssh >/dev/null 2>&1 || {
    echo "[ERROR] ssh tidak ditemukan."
    exit 1
}

echo "[1/5] Checking VPS connection..."

ssh -o ConnectTimeout=10 \
    "${REMOTE_USER}@${REMOTE_HOST}" \
    "echo '[OK] VPS reachable.'"

echo

# ------------------------------------------------------------
# 2. Sync source to VPS staging directory
# ------------------------------------------------------------

echo "[2/5] Syncing source ke VPS..."

rsync -avz --delete \
    --exclude '.venv/' \
    --exclude '.git/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude 'data/vulnmart.db' \
    --exclude 'docker-compose.yml' \
    --exclude 'deploy.sh' \
    "${PROJECT_DIR}/" \
    "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_STAGING}/"

echo "[OK] Source synced."
echo

# ------------------------------------------------------------
# 3. Copy source into production directory
# ------------------------------------------------------------

echo "[3/5] Updating production directory..."

ssh "${REMOTE_USER}@${REMOTE_HOST}" "
    sudo rsync -a --delete \
      --exclude 'data/vulnmart.db' \
      '${REMOTE_STAGING}/' \
      '${REMOTE_APP}/'
"

echo "[OK] Production source updated."
echo

# ------------------------------------------------------------
# 4. Build & restart VulnMart
# ------------------------------------------------------------

echo "[4/5] Building VulnMart image..."

ssh "${REMOTE_USER}@${REMOTE_HOST}" "
    cd '${REMOTE_APP}' &&
    docker compose build &&
    docker compose up -d
"

echo "[OK] VulnMart container updated."
echo

# ------------------------------------------------------------
# 5. Health check
# ------------------------------------------------------------

echo "[5/5] Running health check..."

ssh "${REMOTE_USER}@${REMOTE_HOST}" "
    echo '--- Container status ---'
    docker ps --filter 'name=^vulnmart\$' \
      --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

    echo
    echo '--- Backend health ---'
    docker exec vulnmart python -c \"
import urllib.request
response = urllib.request.urlopen(
    'http://127.0.0.1:8000/',
    timeout=5
)
print('HTTP', response.status)
\"
"

echo
echo "=========================================="
echo "       DEPLOYMENT SUCCESS"
echo "=========================================="
echo
echo "Live:"
echo "https://vulnmart.rootacademy.my.id"
echo
