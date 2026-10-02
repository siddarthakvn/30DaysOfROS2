#!/usr/bin/env bash
# Run the three lidar cases and write transcripts under assets/.
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/ros2_nodes/env.sh"
ASSETS="$ROOT/assets"
mkdir -p "$ASSETS"

cleanup() {
  if [[ -n "${gz_pid:-}" ]]; then kill "$gz_pid" 2>/dev/null || true; fi
  if [[ -n "${br_pid:-}" ]]; then kill "$br_pid" 2>/dev/null || true; fi
  # Match the server argv, not this script's path.
  pkill -f "headless-rendering" 2>/dev/null || true
  pkill -f "parameter_bridge" 2>/dev/null || true
  sleep 1
}
trap cleanup EXIT
cleanup
ros2 daemon stop >/dev/null 2>&1 || true

run_case() {
  local name="$1"
  local world="$2"
  local listen="$3"
  echo "=== $name ==="
  gz sim -s -r --headless-rendering "$world" >"$ASSETS/${name}_gz.log" 2>&1 &
  local gz_pid=$!
  local i
  for i in $(seq 1 40); do
    if gz topic -l 2>/dev/null | grep -q "/lidar"; then
      break
    fi
    sleep 0.5
  done
  {
    echo "gz topics:"
    gz topic -l 2>/dev/null | grep -E "lidar|stats" || true
    echo "ros topics before bridge:"
    ros2 topic list 2>/dev/null | grep lidar || echo "(no /lidar in ROS)"
  } >"$ASSETS/${name}_before_bridge.txt"

  ros2 run ros_gz_bridge parameter_bridge \
    /lidar@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan \
    >"$ASSETS/${name}_bridge.log" 2>&1 &
  local br_pid=$!
  sleep 2
  python3 "$ROOT/ros2_nodes/measure_scan.py" --ros-args \
    -p listen_sec:="$listen" \
    >"$ASSETS/${name}.log" 2>&1 || true
  echo "--- measure ---"
  cat "$ASSETS/${name}.log"
  kill "$br_pid" "$gz_pid" 2>/dev/null || true
  wait "$br_pid" "$gz_pid" 2>/dev/null || true
  pkill -f "headless-rendering" 2>/dev/null || true
  pkill -f "parameter_bridge" 2>/dev/null || true
  local i
  for i in $(seq 1 20); do
    if ! gz topic -l 2>/dev/null | grep -q "/lidar"; then
      break
    fi
    sleep 0.3
  done
  sleep 1
}

run_case A_perfect "$ROOT/worlds/wall_perfect.sdf" 3.0
run_case B_noisy "$ROOT/worlds/wall_noisy.sdf" 3.0
run_case C_slow "$ROOT/worlds/wall_slow.sdf" 4.0
echo DONE
