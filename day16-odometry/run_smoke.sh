#!/usr/bin/env bash
# Four wheel-to-pose cases. Numbers come from the integrator, not from a guess.
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
  python3 wheel_odom.py --ros-args "$@" >"$ASSETS/${name}.log" 2>&1 || true
  grep SUMMARY "$ASSETS/${name}.log" || cat "$ASSETS/${name}.log"
}

# Both wheels 5 rad/s, radius 0.1 m -> 0.5 m/s forward for 2 s.
run A_straight \
  -p omega_left:=5.0 -p omega_right:=5.0 \
  -p radius:=0.1 -p track_width:=0.4 -p seconds:=2.0

# Opposite wheels. Track 0.4 m, rim speed 0.2 m/s -> yaw rate 1 rad/s for 90 deg.
run B_spin \
  -p omega_left:=-2.0 -p omega_right:=2.0 \
  -p radius:=0.1 -p track_width:=0.4 -p seconds:=1.570796

# Turn 90 deg, then the same straight command. Forward is now along y.
run C_after_turn \
  -p omega_left:=5.0 -p omega_right:=5.0 \
  -p radius:=0.1 -p track_width:=0.4 -p seconds:=2.0 \
  -p yaw0:=1.570796

# Same wheel rotation as A, but the radius used in the sum is 10% large.
run D_wrong_radius \
  -p omega_left:=5.0 -p omega_right:=5.0 \
  -p radius:=0.11 -p track_width:=0.4 -p seconds:=2.0

echo DONE
