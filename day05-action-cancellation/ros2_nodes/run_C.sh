#!/usr/bin/env bash
# Investigation C — STOP against reject-cancel server → still SUCCEEDED
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck disable=SC1091
source ./env.sh

DISTANCE_M="${DISTANCE_M:-10.0}"
CANCEL_AFTER_SEC="${CANCEL_AFTER_SEC:-2.0}"

echo "=== Investigation C: STOP after ${CANCEL_AFTER_SEC}s (allow_cancel=false) ==="
echo "Terminal 1 must already be running WITH reject-cancel policy:"
echo "  ros2 run day05_delivery_bringup delivery_server --ros-args -p allow_cancel:=false"
echo

ros2 run day05_delivery_bringup delivery_client --ros-args \
  -p distance_m:="${DISTANCE_M}" \
  -p cancel_after_sec:="${CANCEL_AFTER_SEC}"
