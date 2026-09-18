#!/usr/bin/env bash
# Investigation A — Full warehouse delivery (no cancel) → SUCCEEDED
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck disable=SC1091
source ./env.sh

DISTANCE_M="${DISTANCE_M:-10.0}"

echo "=== Investigation A: full delivery distance_m=${DISTANCE_M} ==="
echo "Terminal 1 must already be running:"
echo "  ros2 run day05_delivery_bringup delivery_server --ros-args -p allow_cancel:=true"
echo

ros2 run day05_delivery_bringup delivery_client --ros-args \
  -p distance_m:="${DISTANCE_M}" \
  -p cancel_after_sec:=-1.0
