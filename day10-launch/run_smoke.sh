#!/usr/bin/env bash
# Day 10 — fast evidence capture (no hanging CLI tools).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$ROOT/ros2_nodes/env.sh"
ASSETS="$ROOT/assets"
mkdir -p "$ASSETS"
export ROS_LOG_DIR="$ASSETS/.ros_logs"
mkdir -p "$ROS_LOG_DIR"

kill_all() {
  pkill -f 'day10-launch/ros2_nodes' 2>/dev/null || true
  pkill -f 'bringup.launch.py' 2>/dev/null || true
  sleep 1
  pkill -9 -f 'day10-launch/ros2_nodes' 2>/dev/null || true
  pkill -9 -f 'bringup.launch.py' 2>/dev/null || true
  sleep 1
}

capture() {
  local tag="$1"; shift
  local ns="robot1"
  local -a args=()
  for a in "$@"; do
    args+=("$a")
    case "$a" in namespace:=*) ns="${a#namespace:=}" ;; esac
  done

  kill_all
  ros2 daemon stop >/dev/null 2>&1 || true
  sleep 1

  echo "=== ${tag} ns=${ns} args=${args[*]:-} ==="
  if ((${#args[@]})); then
    ros2 launch "$ROOT/launch/bringup.launch.py" "${args[@]}" \
      >"/tmp/day10_${tag}_launch.log" 2>&1 &
  else
    ros2 launch "$ROOT/launch/bringup.launch.py" \
      >"/tmp/day10_${tag}_launch.log" 2>&1 &
  fi
  local lp=$!
  sleep 4

  {
    echo "=== ${tag} ==="
    echo "namespace=$ns"
    echo "args=${args[*]:-defaults}"
    echo
    echo "--- launch log (process starts) ---"
    grep -E 'process started|publishing|ERROR|Error|Traceback' "/tmp/day10_${tag}_launch.log" || true
    echo
    echo "--- ros2 node list ---"
    timeout 5 ros2 node list 2>&1 || true
    echo
    echo "--- ros2 topic list ---"
    timeout 5 ros2 topic list 2>&1 || true
    echo
    echo "--- param speed ---"
    timeout 5 ros2 param get "/${ns}/control_stub" speed 2>&1 || true
  } >"$ASSETS/${tag}.log"

  kill -INT "$lp" 2>/dev/null || true
  sleep 1
  kill_all
  echo "Wrote $ASSETS/${tag}.log"
}

kill_all
capture A
capture B namespace:=robot2
capture C namespace:=robot1 use_camera:=false

{
  echo "Day 10 launch comparison"
  echo
  for tag in A B C; do
    echo "----- ${tag} -----"
    cat "$ASSETS/${tag}.log"
    echo
  done
} | tee "$ASSETS/comparison.txt"

echo DONE
