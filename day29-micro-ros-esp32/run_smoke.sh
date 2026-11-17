#!/usr/bin/env bash
# A: C firmware + serial wire, no agent. B: agent bridges /cmd_vel and /esp32/status. C: /cmd_vel stops -> 250 ms watchdog.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ROS_DOMAIN_ID=225
# shellcheck disable=SC1091
source "$ROOT/ros2_nodes/env.sh"
export ROS_DOMAIN_ID=225
cd "$ROOT"
mkdir -p "$ROOT/assets" "$ROOT/build"

gcc -O2 -Wall -Wextra -std=c11 \
  "$ROOT/firmware/host_sim/esp32_client.c" \
  -o "$ROOT/build/esp32_client"

wait_ready() {
  local log="$1"
  local needle="$2"
  for _ in $(seq 1 80); do
    if grep -q "$needle" "$log" 2>/dev/null; then
      return 0
    fi
    sleep 0.1
  done
  return 1
}

start_cable() {
  local dir="$1"
  socat pty,raw,echo=0,link="$dir/esp32_uart" pty,raw,echo=0,link="$dir/agent_uart" >/dev/null 2>&1 &
  CABLE_PID=$!
  for _ in $(seq 1 50); do
    if [[ -e "$dir/esp32_uart" && -e "$dir/agent_uart" ]]; then
      return 0
    fi
    sleep 0.05
  done
  return 1
}

echo "=== no_agent ==="
TMP_A="$(mktemp -d)"
CABLE_PID=""
start_cable "$TMP_A"
python3 -u "$ROOT/ros2_nodes/driver.py" --ros-args -p mode:=no_agent >"$TMP_A/driver.log" 2>&1 &
DRV_PID=$!
"$ROOT/build/esp32_client" --dev "$TMP_A/esp32_uart" --mode no_agent --duration-ms 1500 >"$TMP_A/esp32.log" 2>&1 &
MCU_PID=$!
wait_ready "$TMP_A/driver.log" "^READY " || true
wait "$MCU_PID" 2>/dev/null || true
{
  echo "=== no_agent ==="
  cat "$TMP_A/esp32.log" "$TMP_A/driver.log"
  echo "--- nodes ---"
  timeout -k 3 8 ros2 node list || true
  echo "--- cmd_vel ---"
  timeout -k 3 8 ros2 topic info /cmd_vel -v || true
  echo "--- status ---"
  timeout -k 3 8 ros2 topic info /esp32/status -v || true
} >"$ROOT/assets/A_no_agent.log" 2>&1
kill "$DRV_PID" "$CABLE_PID" 2>/dev/null || true
wait "$DRV_PID" "$CABLE_PID" 2>/dev/null || true
rm -rf "$TMP_A"
grep "^SUMMARY " "$ROOT/assets/A_no_agent.log" || echo "NO SUMMARY for no_agent"

run_bridged() {
  local mode="$1"
  local log="$2"
  local tmp
  tmp="$(mktemp -d)"
  echo "=== $mode ==="
  CABLE_PID=""
  start_cable "$tmp"
  python3 -u "$ROOT/ros2_nodes/agent.py" --dev "$tmp/agent_uart" --mode "$mode" >"$tmp/agent.log" 2>&1 &
  local agent_pid=$!
  "$ROOT/build/esp32_client" --dev "$tmp/esp32_uart" --mode "$mode" >"$tmp/esp32.log" 2>&1 &
  local mcu_pid=$!
  sleep 0.3
  python3 -u "$ROOT/ros2_nodes/driver.py" --ros-args -p "mode:=$mode" >"$tmp/driver.log" 2>&1 &
  local drv_pid=$!
  wait_ready "$tmp/esp32.log" "^READY " || true
  wait_ready "$tmp/agent.log" "^READY " || true
  wait_ready "$tmp/driver.log" "^READY " || true
  {
    echo "=== $mode ==="
    cat "$tmp/esp32.log" "$tmp/agent.log" "$tmp/driver.log"
    echo "--- nodes ---"
    timeout -k 3 8 ros2 node list || true
    echo "--- cmd_vel ---"
    timeout -k 3 8 ros2 topic info /cmd_vel -v || true
    echo "--- status ---"
    timeout -k 3 8 ros2 topic echo --once /esp32/status std_msgs/msg/String || true
  } >"$log" 2>&1
  kill "$drv_pid" "$mcu_pid" "$agent_pid" "$CABLE_PID" 2>/dev/null || true
  wait "$drv_pid" "$mcu_pid" "$agent_pid" "$CABLE_PID" 2>/dev/null || true
  rm -rf "$tmp"
  grep "^SUMMARY " "$log" || echo "NO SUMMARY for $mode"
}

run_bridged bridged "$ROOT/assets/B_bridged.log"
run_bridged watchdog "$ROOT/assets/C_watchdog.log"
echo "done"
