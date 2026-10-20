#!/usr/bin/env bash
# Send one NavigateToPose goal three ways and keep each SUMMARY.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/ros2_nodes/env.sh"
export ROS_DOMAIN_ID=210
cd "$ROOT"

GOAL='{pose: {header: {frame_id: map}, pose: {position: {x: 5.2, y: 0.6, z: 0.0}, orientation: {w: 1.0}}}}'

run_one() {
  local mode="$1"
  local log="$2"
  echo "=== $mode ==="
  python3 -u "$ROOT/ros2_nodes/navigate.py" --ros-args -p "mode:=$mode" >"$log" 2>&1 &
  local pid=$!
  for _ in $(seq 1 40); do
    if grep -q "^READY " "$log" 2>/dev/null; then
      break
    fi
    sleep 0.25
  done
  timeout 25 ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "$GOAL" >>"$log" 2>&1 || true
  echo "--- topic ---" | tee -a "$log"
  timeout 8 ros2 action info /navigate_to_pose >>"$log" 2>&1 || true
  timeout 8 ros2 topic info /plan -v >>"$log" 2>&1 || true
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  grep "^SUMMARY " "$log" || echo "NO SUMMARY for $mode"
}

run_one goal_only "$ROOT/assets/A_goal_only.log"
run_one planner_only "$ROOT/assets/B_planner_only.log"
run_one full "$ROOT/assets/C_full.log"
echo "done"
