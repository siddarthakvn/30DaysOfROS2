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
  python3 heading_pid.py --ros-args "$@" >"$ASSETS/${name}.log" 2>&1 || true
  grep SUMMARY "$ASSETS/${name}.log" || cat "$ASSETS/${name}.log"
}

# Heading remembers turn rate. P only. Target 90 deg.
run A_p_only \
  -p kp:=4.0 -p kd:=0.0 -p ki:=0.0 \
  -p plant:=inertia -p target_deg:=90.0 -p seconds:=8.0

# Same plant and P, plus a brake on turn rate.
run B_with_d \
  -p kp:=4.0 -p kd:=4.0 -p ki:=0.0 \
  -p plant:=inertia -p target_deg:=90.0 -p seconds:=8.0

# Turn rate equals the command immediately. Same P. No stored speed.
run C_instant \
  -p kp:=4.0 -p kd:=0.0 -p ki:=0.0 \
  -p plant:=instant -p target_deg:=90.0 -p seconds:=8.0

echo DONE
