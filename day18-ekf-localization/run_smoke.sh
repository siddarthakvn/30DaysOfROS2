#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/ros2_nodes/env.sh"
ASSETS="$ROOT/assets"
mkdir -p "$ASSETS"
cd "$ROOT/ros2_nodes"

run() {
  local name="$1"
  shift
  echo "=== $name ==="
  python3 fuse_pose.py --ros-args "$@" >"$ASSETS/${name}.log" 2>&1 || true
  grep SUMMARY "$ASSETS/${name}.log" || cat "$ASSETS/${name}.log"
}

run A_wheels -p case:=wheels
run B_gyro -p case:=gyro
run C_ekf -p case:=ekf
run D_fight -p case:=fight

echo DONE
