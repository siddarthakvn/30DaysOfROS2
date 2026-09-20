#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/ros2_nodes"
source ./env.sh
export ROS_LOG_DIR="$(pwd)/../assets/.ros_logs"
mkdir -p "$ROS_LOG_DIR"
ASSETS="$(pwd)/../assets"
ros2 daemon stop >/dev/null 2>&1 || true
sleep 1

run_pair() {
  local tag="$1"; shift
  local pub_args="$1"; shift
  local sub_args="$1"; shift
  local wait_before_sub="${1:-1}"
  local wait_after_sub="${2:-4}"
  local info_out="${3:-}"

  python3 qos_pub.py --ros-args $pub_args > "/tmp/day07_${tag}_pub.log" 2>&1 &
  local pub_pid=$!
  sleep "$wait_before_sub"
  python3 qos_sub.py --ros-args $sub_args > "/tmp/day07_${tag}_sub.log" 2>&1 &
  local sub_pid=$!
  sleep "$wait_after_sub"
  if [[ -n "$info_out" ]]; then
    ros2 topic info /qos_demo/stream --verbose > "$info_out" 2>&1 || true
  fi
  kill "$sub_pid" "$pub_pid" 2>/dev/null || true
  wait "$sub_pid" "$pub_pid" 2>/dev/null || true
}

echo "=== A ==="
run_pair A \
  "-p reliability:=reliable -p durability:=volatile -p publish_hz:=10.0" \
  "-p reliability:=reliable -p durability:=volatile" \
  1 4 "$ASSETS/A_topic_info.txt"
{
  echo "=== PUB ==="; tail -n 20 /tmp/day07_A_pub.log
  echo "=== SUB ==="; tail -n 20 /tmp/day07_A_sub.log
} > "$ASSETS/A_compatible.log"

echo "=== B1 ==="
ros2 daemon stop >/dev/null 2>&1 || true
sleep 1
python3 qos_pub.py --ros-args -p reliability:=best_effort -p durability:=volatile -p publish_hz:=10.0 > /tmp/day07_B1_pub.log 2>&1 &
PUB_B=$!
sleep 1
python3 qos_sub.py --ros-args -p reliability:=reliable -p durability:=volatile > /tmp/day07_B1_sub.log 2>&1 &
SUB_B=$!
sleep 5
ros2 topic info /qos_demo/stream --verbose > "$ASSETS/B1_topic_info.txt" 2>&1 || true
{
  echo "=== PUB ==="; tail -n 25 /tmp/day07_B1_pub.log
  echo "=== SUB (expect recv_total=0) ==="; tail -n 25 /tmp/day07_B1_sub.log
} > "$ASSETS/B1_mismatch.log"
kill "$SUB_B" 2>/dev/null || true
wait "$SUB_B" 2>/dev/null || true

echo "=== B2 ==="
python3 qos_sub.py --ros-args -p reliability:=best_effort -p durability:=volatile > /tmp/day07_B2_sub.log 2>&1 &
SUB_B2=$!
sleep 4
{
  echo "=== PUB still BEST_EFFORT ==="; tail -n 15 /tmp/day07_B1_pub.log
  echo "=== SUB BEST_EFFORT (expect receives) ==="; tail -n 20 /tmp/day07_B2_sub.log
} > "$ASSETS/B2_fixed.log"
kill "$SUB_B2" "$PUB_B" 2>/dev/null || true
wait "$SUB_B2" "$PUB_B" 2>/dev/null || true

echo "=== C1 ==="
ros2 daemon stop >/dev/null 2>&1 || true
sleep 1
run_pair C1 \
  "-p reliability:=reliable -p durability:=volatile -p publish_hz:=2.0" \
  "-p reliability:=reliable -p durability:=volatile" \
  3 3 ""

echo "=== C2 ==="
run_pair C2 \
  "-p reliability:=reliable -p durability:=transient_local -p depth:=10 -p publish_hz:=2.0" \
  "-p reliability:=reliable -p durability:=transient_local -p depth:=10" \
  3 3 "$ASSETS/C_topic_info.txt"

echo "=== C3 ==="
run_pair C3 \
  "-p reliability:=reliable -p durability:=volatile -p publish_hz:=2.0" \
  "-p reliability:=reliable -p durability:=transient_local" \
  1 4 ""

{
  echo "=== C1 VOLATILE late join ==="
  echo "-- PUB --"; tail -n 8 /tmp/day07_C1_pub.log
  echo "-- SUB --"; tail -n 12 /tmp/day07_C1_sub.log
  echo
  echo "=== C2 TRANSIENT_LOCAL late join ==="
  echo "-- PUB --"; tail -n 8 /tmp/day07_C2_pub.log
  echo "-- SUB --"; tail -n 12 /tmp/day07_C2_sub.log
  echo
  echo "=== C3 VOLATILE pub + TRANSIENT_LOCAL sub (expect 0) ==="
  echo "-- PUB --"; tail -n 8 /tmp/day07_C3_pub.log
  echo "-- SUB --"; tail -n 12 /tmp/day07_C3_sub.log
} > "$ASSETS/C_durability.log"

echo "==== SUMMARY ===="
echo "A:"; grep 'SUB recv' "$ASSETS/A_compatible.log" | tail -3 || true
echo "B1:"; grep 'SUB recv' "$ASSETS/B1_mismatch.log" | tail -5 || true
echo "B2:"; grep 'SUB recv' "$ASSETS/B2_fixed.log" | tail -5 || true
echo "C1:"; sed -n '/C1 VOLATILE/,/C2 TRANSIENT/p' "$ASSETS/C_durability.log" | grep 'SUB recv' || true
echo "C2:"; sed -n '/C2 TRANSIENT/,/C3 VOLATILE/p' "$ASSETS/C_durability.log" | grep 'SUB recv' || true
echo "C3:"; sed -n '/C3 VOLATILE/,$p' "$ASSETS/C_durability.log" | grep 'SUB recv' || true
grep -i reliability "$ASSETS/B1_topic_info.txt" | head -10 || true
echo DONE
