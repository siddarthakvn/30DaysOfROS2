#!/usr/bin/env bash
# Drop a box on the planned path three ways and keep each SUMMARY.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ROS_DOMAIN_ID=231
# shellcheck disable=SC1091
source "$ROOT/ros2_nodes/env.sh"
export ROS_DOMAIN_ID=231
cd "$ROOT"
mkdir -p "$ROOT/assets"

run_one() {
  local mode="$1"
  local log="$2"
  echo "=== $mode ==="
  python3 -u "$ROOT/ros2_nodes/drive.py" --ros-args -p "mode:=$mode" >"$log" 2>&1 &
  local pid=$!
  for _ in $(seq 1 40); do
    if grep -q "^READY " "$log" 2>/dev/null; then
      break
    fi
    sleep 0.25
  done
  echo "--- topic ---" | tee -a "$log"
  timeout -k 3 8 ros2 topic info /plan -v >>"$log" 2>&1 || true
  timeout -k 3 8 ros2 topic info /cmd_vel -v >>"$log" 2>&1 || true
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  grep "^SUMMARY " "$log" || echo "NO SUMMARY for $mode"
}

run_one blind "$ROOT/assets/A_blind.log"
run_one local "$ROOT/assets/B_local.log"
run_one replan "$ROOT/assets/C_replan.log"
echo "done"
