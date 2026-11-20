#!/usr/bin/env bash
# Scale one ROS 2 robot to three across three modes:
#   A: collision      — leading-slash '/cmd_vel', '/odom', and unprefixed 'base_link'
#   B: uncoordinated  — namespaced 'cmd_vel'/'odom'/'rN/base_link', no task allocator
#   C: coordinated    — namespaced robots + fleet_coordinator assigning closest robot (r1)
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ROS_DOMAIN_ID=224
# shellcheck disable=SC1091
source "$ROOT/ros2_nodes/env.sh"
export ROS_DOMAIN_ID=224
cd "$ROOT"
mkdir -p "$ROOT/assets"

wait_ready() {
  local log="$1"
  for _ in $(seq 1 80); do
    if grep -q "READY mode=" "$log" 2>/dev/null; then
      return 0
    fi
    sleep 0.25
  done
  return 1
}

run_mode() {
  local mode="$1"
  local log="$2"
  local tmp
  tmp="$(mktemp -d)"
  echo "=== $mode ==="
  ros2 launch "$ROOT/launch/fleet.launch.py" "mode:=$mode" >"$tmp/launch.log" 2>&1 &
  local lpid=$!
  wait_ready "$tmp/launch.log" || true

  {
    echo "--- nodes ---"
    timeout -k 3 8 ros2 node list --no-daemon | sort || true
    echo "--- topics ---"
    timeout -k 3 8 ros2 topic list --no-daemon | sort || true
    if [[ "$mode" == "collision" ]]; then
      echo "--- cmd_vel_info ---"
      timeout -k 3 8 ros2 topic info /cmd_vel -v || true
      echo "--- odom_info ---"
      timeout -k 3 8 ros2 topic info /odom -v || true
    else
      echo "--- r1_cmd_vel_info ---"
      timeout -k 3 8 ros2 topic info /r1/cmd_vel -v || true
      echo "--- r2_cmd_vel_info ---"
      timeout -k 3 8 ros2 topic info /r2/cmd_vel -v || true
      echo "--- tf_r1 ---"
      timeout -k 2 3 ros2 run tf2_ros tf2_echo map r1/base_link || true
    fi
    if [[ "$mode" == "coordinated" ]]; then
      echo "--- assignment ---"
      timeout -k 3 8 ros2 topic echo --once /fleet/assignment std_msgs/msg/String || true
    fi
    echo "--- summary_echo ---"
    timeout -k 3 8 ros2 topic echo --once /fleet/summary std_msgs/msg/String || true
  } >"$tmp/cli.log" 2>&1

  kill -INT "$lpid" 2>/dev/null || true
  for _ in $(seq 1 20); do
    kill -0 "$lpid" 2>/dev/null || break
    sleep 0.2
  done
  pkill -f "[p]ython3 -u $ROOT/ros2_nodes/" 2>/dev/null || true
  wait "$lpid" 2>/dev/null || true

  cat "$tmp/launch.log" "$tmp/cli.log" >"$log"
  rm -rf "$tmp"

  grep -E "(COORDINATOR |ROBOT |SUMMARY )" "$log" | grep -v "^data:" | sed 's/^\[python3-[0-9]*\] //' || echo "NO SUMMARY for $mode"
}

run_mode collision "$ROOT/assets/A_collision.log"
run_mode uncoordinated "$ROOT/assets/B_uncoordinated.log"
run_mode coordinated "$ROOT/assets/C_coordinated.log"
echo "done"
