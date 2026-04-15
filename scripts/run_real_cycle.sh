#!/usr/bin/env bash
set -euo pipefail
curl -sS -X POST "${MOORE_API_BASE:-http://localhost:8000}/run-cycle" | python -m json.tool
