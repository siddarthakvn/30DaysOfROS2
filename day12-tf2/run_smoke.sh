#!/usr/bin/env bash
# Day 12 — Investigations A/B/C evidence.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$ROOT/ros2_nodes/env.sh"
ASSETS="$ROOT/assets"
mkdir -p "$ASSETS" "$ROS_LOG_DIR"

strip_ansi() {
  python3 -c 'import sys,re; print(re.sub(r"\x1b\[[0-9;]*m","",sys.stdin.read()), end="")'
}

kill_all() {
  pkill -f 'day12-tf2' 2>/dev/null || true
  pkill -f 'odom_driver.py' 2>/dev/null || true
  pkill -f 'map_localizer.py' 2>/dev/null || true
  pkill -f 'frame_probe.py' 2>/dev/null || true
  pkill -f 'conflict_demo.py' 2>/dev/null || true
  pkill -f 'demo.launch.py' 2>/dev/null || true
  sleep 1
  pkill -9 -f 'odom_driver.py' 2>/dev/null || true
  pkill -9 -f 'map_localizer.py' 2>/dev/null || true
  pkill -9 -f 'frame_probe.py' 2>/dev/null || true
  pkill -9 -f 'conflict_demo.py' 2>/dev/null || true
  ros2 daemon stop >/dev/null 2>&1 || true
  sleep 1
}

wait_pid_cap() {
  local pid="$1" cap="$2" waited=0
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

extract_summary() {
  local logfile="$1"
  if grep -q "==== SUMMARY ====" "$logfile"; then
    sed -n '/==== SUMMARY ====/,/==== END SUMMARY ====/p' "$logfile"
  else
    echo "(no SUMMARY found)"
    tail -n 40 "$logfile" || true
  fi
}

echo "=== A: odom only (smooth, no map) ==="
export ROS_DOMAIN_ID=120
kill_all
ros2 launch "$ROOT/launch/demo.launch.py" mode:=a run_sec:=12.0 \
  > /tmp/day12_A.log 2>&1 &
LP=$!
wait_pid_cap "$LP" 18
{
  echo "=== A ==="
  echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
  echo "mode=odom_only  tree=odom->base_link"
  echo
  echo "--- SUMMARY ---"
  extract_summary /tmp/day12_A.log
  echo
  echo "--- highlights ---"
  grep -E 'ODOM pose|map_robot=MISSING|frame_probe|odom_driver' /tmp/day12_A.log \
    | strip_ansi | head -n 20 || true
} | strip_ansi >"$ASSETS/A.log"
echo "Wrote $ASSETS/A.log"

echo "=== B: map jump while odom stays continuous ==="
export ROS_DOMAIN_ID=121
kill_all
ros2 launch "$ROOT/launch/demo.launch.py" mode:=b run_sec:=12.0 jump_at_sec:=5.0 \
  > /tmp/day12_B.log 2>&1 &
LP=$!
wait_pid_cap "$LP" 18
{
  echo "=== B ==="
  echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
  echo "mode=map_jump  tree=map->odom->base_link"
  echo
  echo "--- SUMMARY ---"
  extract_summary /tmp/day12_B.log
  echo
  echo "--- MAP JUMP line ---"
  grep -E 'MAP JUMP|ILLEGAL' /tmp/day12_B.log | strip_ansi || true
  echo
  echo "--- highlights (around jump) ---"
  grep -E 'map_robot=|ODOM pose|MAP JUMP' /tmp/day12_B.log \
    | strip_ansi | head -n 30 || true
} | strip_ansi >"$ASSETS/B.log"
echo "Wrote $ASSETS/B.log"

echo "=== C: dual-parent conflict (illegal tree) ==="
export ROS_DOMAIN_ID=122
kill_all
python3 "$ROOT/ros2_nodes/conflict_demo.py" --ros-args -p run_sec:=6.0 \
  > /tmp/day12_C.log 2>&1 &
LP=$!
wait_pid_cap "$LP" 12
{
  echo "=== C ==="
  echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
  echo "mode=dual_parent_conflict"
  echo
  echo "--- SUMMARY ---"
  extract_summary /tmp/day12_C.log
  echo
  echo "--- conflict / lookup evidence ---"
  grep -E 'ILLEGAL|FAILED|dual_parent|lookup|WARNING|Error|parent' /tmp/day12_C.log \
    | strip_ansi | head -n 40 || true
} | strip_ansi >"$ASSETS/C.log"
echo "Wrote $ASSETS/C.log"

{
  echo "Day 12 TF2 comparison — base_link / odom / map"
  echo
  for tag in A B C; do
    echo "----- ${tag} -----"
    cat "$ASSETS/${tag}.log"
    echo
  done
} >"$ASSETS/comparison.txt"

kill_all
echo DONE
