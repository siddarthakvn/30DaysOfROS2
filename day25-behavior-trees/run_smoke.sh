#!/usr/bin/env bash
# Run the knot, the state machine, and the tree. Keep each SUMMARY.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ROS_DOMAIN_ID=229
# shellcheck disable=SC1091
source "$ROOT/ros2_nodes/env.sh"
export ROS_DOMAIN_ID=229
cd "$ROOT"
mkdir -p "$ROOT/assets"

run_one() {
  local mode="$1"
  local log="$2"
  echo "=== $mode ==="
  python3 -u "$ROOT/ros2_nodes/tick.py" --ros-args -p "mode:=$mode" >"$log" 2>&1 &
  local pid=$!
  for _ in $(seq 1 40); do
    if grep -q "^READY " "$log" 2>/dev/null; then
      break
    fi
    sleep 0.25
  done
  echo "--- topic ---" | tee -a "$log"
  timeout -k 3 8 ros2 topic info /behavior_tree_log -v >>"$log" 2>&1 || true
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  grep "^SUMMARY " "$log" || echo "NO SUMMARY for $mode"
}

run_one knot "$ROOT/assets/A_knot.log"
run_one machine "$ROOT/assets/B_machine.log"
run_one tree "$ROOT/assets/C_tree.log"
echo "done"
