#!/usr/bin/env bash
# Porovnanie v1 → v2 fiktívneho obchodu jedným príkazom (bez API kľúča).
# Postaví ukážkové weby, spustí ich na localhoste, urobí oba audity a porovnávací report.
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
DATE=${DATE:-2026-10-18}   # pevný dátum → bajtovo rovnaké výstupy pri opakovaní

$PY sample/build_sites.py
$PY -m http.server 8761 -d sample/v1/site >/dev/null 2>&1 & V1=$!
$PY -m http.server 8762 -d sample/v2/site >/dev/null 2>&1 & V2=$!
trap 'kill $V1 $V2 2>/dev/null || true' EXIT
sleep 1

$PY audit.py --feed sample/v1/heureka.xml --site http://127.0.0.1:8761 --pages 100 \
  --enrichments sample/v1/enrichments.json --probes sample/v1/probes.json \
  --label v1 --date "$DATE" --out out/v1
$PY audit.py --feed sample/v2/heureka.xml --site http://127.0.0.1:8762 --pages 100 \
  --label v2 --date "$DATE" --out out/v2
$PY compare.py out/v1/audit.json out/v2/audit.json -o out/compare-v1-v2.md
