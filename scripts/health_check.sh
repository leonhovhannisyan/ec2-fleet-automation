#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INV_FILE="${ROOT_DIR}/ansible/inventory/generated.ini"

if [[ ! -f "${INV_FILE}" ]]; then
  echo "Inventory not found: ${INV_FILE}"
  echo "Run: ./scripts/generate_inventory.py"
  exit 1
fi

IP="$(awk '/ansible_host=/{print $2}' "${INV_FILE}" | head -n1 | cut -d= -f2)"
USER="$(awk -F= '/^ansible_user=/{print $2}' "${INV_FILE}" | head -n1)"

echo "Target: ${USER}@${IP}"

echo "[1/3] Ping..."
ping -c 1 -W 2 "${IP}" >/dev/null && echo "OK"

echo "[2/3] SSH..."
ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=5 "${USER}@${IP}" "echo OK" >/dev/null && echo "OK"

echo "[3/3] HTTP..."
curl -fsS "http://${IP}" >/dev/null && echo "OK"

echo "All checks passed."
