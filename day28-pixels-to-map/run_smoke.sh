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
  python3 pixel_to_map.py --ros-args "$@" >"$ASSETS/${name}.log" 2>&1 || true
  grep SUMMARY "$ASSETS/${name}.log" || cat "$ASSETS/${name}.log"
}

run A_full -p case:=full
run B_bad_depth -p case:=bad_depth
run C_no_tf -p case:=no_tf
run D_stale_pose -p case:=stale_pose

echo DONE
