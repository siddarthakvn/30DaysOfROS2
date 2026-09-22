#!/usr/bin/env bash
# Day 09 — run Investigations A/B/C and capture evidence.
set -euo pipefail
cd "$(dirname "$0")/ros2_nodes"
source ./env.sh
export ROS_LOG_DIR="$(pwd)/../assets/.ros_logs"
mkdir -p "$ROS_LOG_DIR" "$(pwd)/../assets"
ASSETS="$(pwd)/../assets"
ros2 daemon stop >/dev/null 2>&1 || true
sleep 1

strip_ansi() {
  python3 -c 'import sys,re; print(re.sub(r"\x1b\[[0-9;]*m","",sys.stdin.read()), end="")'
}

wait_pid_cap() {
  local pid="$1"
  local cap="$2"
  local waited=0
  while kill -0 "$pid" 2>/dev/null; do
    if (( waited >= cap )); then
      kill "$pid" 2>/dev/null || true
      sleep 0.5
      kill -9 "$pid" 2>/dev/null || true
      break
    fi
    sleep 1
    waited=$((waited + 1))
  done
  wait "$pid" 2>/dev/null || true
}

echo "=== A: YAML startup override ==="
python3 velocity_governor.py --ros-args --params-file ../config/cruise_limit.yaml \
  > /tmp/day09_A_robot.log 2>&1 &
A_PID=$!
wait_pid_cap "$A_PID" 12
{
  echo "=== A ROBOT ==="
  if grep -q "==== SUMMARY ====" /tmp/day09_A_robot.log; then
    sed -n '/==== SUMMARY ====/,/==== END SUMMARY ====/p' /tmp/day09_A_robot.log
    echo
    echo "--- startup / ticks ---"
    grep -E 'CONFIG |EFFECTIVE_MAX |TICK ' /tmp/day09_A_robot.log | head -n 8
  else
    cat /tmp/day09_A_robot.log
  fi
} | strip_ansi > "$ASSETS/A.log"
echo "Wrote $ASSETS/A.log"

ros2 daemon stop >/dev/null 2>&1 || true
sleep 1

echo "=== B: runtime param set (live) ==="
python3 velocity_governor.py --ros-args \
  -p max_velocity:=1.0 -p request_vx:=1.5 -p apply_mode:=live \
  -p run_sec:=10.0 -p publish_hz:=2.0 \
  > /tmp/day09_B_robot.log 2>&1 &
B_PID=$!
sleep 2.5
SET_B_OUT=$(ros2 param set /velocity_governor max_velocity 0.3 2>&1 || true)
GET_B_OUT=$(ros2 param get /velocity_governor max_velocity 2>&1 || true)
wait_pid_cap "$B_PID" 14
{
  echo "=== B CLI ==="
  echo "ros2 param set: $SET_B_OUT"
  echo "ros2 param get: $GET_B_OUT"
  echo
  echo "=== B ROBOT ==="
  if grep -q "==== SUMMARY ====" /tmp/day09_B_robot.log; then
    sed -n '/==== SUMMARY ====/,/==== END SUMMARY ====/p' /tmp/day09_B_robot.log
  fi
  echo
  echo "--- ticks around set ---"
  grep -E 'TICK |PARAM_ACCEPT|PARAM_REJECT|CONFIG ' /tmp/day09_B_robot.log
} | strip_ansi > "$ASSETS/B.log"
echo "Wrote $ASSETS/B.log"

ros2 daemon stop >/dev/null 2>&1 || true
sleep 1

echo "=== C: reject invalid max_velocity=10.0 ==="
python3 velocity_governor.py --ros-args \
  -p max_velocity:=1.0 -p request_vx:=1.5 -p apply_mode:=live \
  -p run_sec:=10.0 -p publish_hz:=2.0 \
  > /tmp/day09_C_robot.log 2>&1 &
C_PID=$!
sleep 2.5
SET_C_OUT=$(ros2 param set /velocity_governor max_velocity 10.0 2>&1 || true)
GET_C_OUT=$(ros2 param get /velocity_governor max_velocity 2>&1 || true)
wait_pid_cap "$C_PID" 14
{
  echo "=== C CLI ==="
  echo "ros2 param set: $SET_C_OUT"
  echo "ros2 param get: $GET_C_OUT"
  echo
  echo "=== C ROBOT ==="
  if grep -q "==== SUMMARY ====" /tmp/day09_C_robot.log; then
    sed -n '/==== SUMMARY ====/,/==== END SUMMARY ====/p' /tmp/day09_C_robot.log
  fi
  echo
  echo "--- reject evidence ---"
  grep -E 'PARAM_REJECT|PARAM_ACCEPT|TICK |CONFIG ' /tmp/day09_C_robot.log
} | strip_ansi > "$ASSETS/C.log"
echo "Wrote $ASSETS/C.log"

{
  echo "Day 09 parameter comparison"
  echo
  echo "----- A (YAML startup) -----"
  grep -E 'SUMMARY|STORED|EFFECTIVE|TICKS|CONFIG apply' "$ASSETS/A.log" || true
  echo
  echo "----- B (runtime set 0.3) -----"
  grep -E 'param set|param get|STORED|EFFECTIVE|TICKS|PARAM_ACCEPT|out=0\.3|out=1\.0' "$ASSETS/B.log" || true
  echo
  echo "----- C (reject 10.0) -----"
  grep -E 'param set|param get|STORED|EFFECTIVE|TICKS|PARAM_REJECT|rejects=' "$ASSETS/C.log" || true
} | tee "$ASSETS/comparison.txt"

echo DONE
