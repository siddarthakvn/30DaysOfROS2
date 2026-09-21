#!/usr/bin/env bash
# Day 08 — run Investigations A/B/C and capture SUMMARY evidence.
set -euo pipefail
cd "$(dirname "$0")/ros2_nodes"
source ./env.sh
export ROS_LOG_DIR="$(pwd)/../assets/.ros_logs"
mkdir -p "$ROS_LOG_DIR" "$(pwd)/../assets"
ASSETS="$(pwd)/../assets"
ros2 daemon stop >/dev/null 2>&1 || true
sleep 1

run_case() {
  local tag="$1"
  local robot_args="$2"
  local out="$ASSETS/${tag}.log"

  echo "=== Running ${tag} ==="
  python3 lidar_pub.py --ros-args \
    -p period_sec:=1.5 -p warmup_sec:=1.0 -p count:=4 \
    > "/tmp/day08_${tag}_pub.log" 2>&1 &
  local pub_pid=$!

  sleep 0.4
  python3 busy_robot_node.py --ros-args ${robot_args} \
    > "/tmp/day08_${tag}_robot.log" 2>&1 &
  local robot_pid=$!

  # Node runs ~8s + drain; hard-cap so a stuck shutdown cannot hang the suite.
  local waited=0
  while kill -0 "$robot_pid" 2>/dev/null; do
    if (( waited >= 20 )); then
      echo "WARN: ${tag} robot still running after 20s — sending SIGTERM"
      kill "$robot_pid" 2>/dev/null || true
      sleep 1
      kill -9 "$robot_pid" 2>/dev/null || true
      break
    fi
    sleep 1
    waited=$((waited + 1))
  done
  wait "$robot_pid" 2>/dev/null || true
  kill "$pub_pid" 2>/dev/null || true
  sleep 0.5
  kill -9 "$pub_pid" 2>/dev/null || true
  wait "$pub_pid" 2>/dev/null || true

  {
    echo "=== ${tag} PUB (tail) ==="
    tail -n 20 "/tmp/day08_${tag}_pub.log" || true
    echo
    echo "=== ${tag} ROBOT ==="
    # Prefer SUMMARY block; fall back to full log.
    if grep -q "==== SUMMARY ====" "/tmp/day08_${tag}_robot.log"; then
      sed -n '/==== SUMMARY ====/,/==== END SUMMARY ====/p' "/tmp/day08_${tag}_robot.log"
      echo
      echo "--- LIDAR events ---"
      grep -E 'LIDAR (START|END)' "/tmp/day08_${tag}_robot.log" || true
    else
      cat "/tmp/day08_${tag}_robot.log"
    fi
  } > "$out"

  echo "Wrote $out"
  grep -E 'IMU |CONTROL |CONCURRENCY |LIDAR blocks' "$out" || true
  echo
}

run_case A \
  "-p executor:=single -p group_mode:=default -p lidar_block_ms:=500 -p run_sec:=8.0"

ros2 daemon stop >/dev/null 2>&1 || true
sleep 1

run_case B \
  "-p executor:=multi -p num_threads:=4 -p group_mode:=shared_mutex -p lidar_block_ms:=500 -p run_sec:=8.0"

ros2 daemon stop >/dev/null 2>&1 || true
sleep 1

run_case C \
  "-p executor:=multi -p num_threads:=4 -p group_mode:=separate_mutex -p lidar_block_ms:=500 -p run_sec:=8.0"

echo "==== COMPARISON ===="
{
  echo "Day 08 executor comparison"
  echo
  for tag in A B C; do
    echo "----- ${tag} -----"
    grep -E 'CONFIG |LIDAR blocks|IMU |CONTROL |CONCURRENCY ' "$ASSETS/${tag}.log" || true
    echo
  done
} | tee "$ASSETS/comparison.txt"

echo DONE
