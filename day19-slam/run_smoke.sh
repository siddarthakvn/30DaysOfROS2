#!/usr/bin/env bash
# Run the three map builds and keep each SUMMARY in assets/.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/ros2_nodes/env.sh"
export ROS_DOMAIN_ID=190
cd "$ROOT"

run_one() {
  local mode="$1"
  local log="$2"
  echo "=== $mode ==="
  python3 -u "$ROOT/ros2_nodes/build_map.py" --ros-args -p "mode:=$mode" >"$log" 2>&1 &
  local pid=$!
  for _ in $(seq 1 90); do
    if grep -q "^SUMMARY " "$log" 2>/dev/null; then
      break
    fi
    sleep 1
  done
  echo "--- topic ---" | tee -a "$log"
  timeout 8 ros2 topic info /map -v >>"$log" 2>&1 || true
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  grep "^SUMMARY " "$log" || echo "NO SUMMARY for $mode"
}

run_one truth "$ROOT/assets/A_truth.log"
run_one drift "$ROOT/assets/B_drift.log"
run_one match "$ROOT/assets/C_match.log"
echo "done"
