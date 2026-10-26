#!/usr/bin/env bash
# Plan from A to B three ways and keep each SUMMARY.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ROS_DOMAIN_ID=230
# shellcheck disable=SC1091
source "$ROOT/ros2_nodes/env.sh"
export ROS_DOMAIN_ID=230
cd "$ROOT"
mkdir -p "$ROOT/assets"

run_one() {
  local mode="$1"
  local log="$2"
  echo "=== $mode ==="
  python3 -u "$ROOT/ros2_nodes/planner.py" --ros-args -p "mode:=$mode" >"$log" 2>&1 &
  local pid=$!
  for _ in $(seq 1 40); do
    if grep -q "^READY " "$log" 2>/dev/null; then
      break
    fi
    sleep 0.25
  done
  echo "--- topic ---" | tee -a "$log"
  timeout -k 3 8 ros2 topic info /plan -v >>"$log" 2>&1 || true
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  grep "^SUMMARY " "$log" || echo "NO SUMMARY for $mode"
}

run_one line "$ROOT/assets/A_line.log"
run_one dijkstra "$ROOT/assets/B_dijkstra.log"
run_one astar "$ROOT/assets/C_astar.log"
echo "done"
