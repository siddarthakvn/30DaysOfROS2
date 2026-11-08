#!/usr/bin/env bash
# Three graphs. A draws boxes and publishes nothing. B and C are camera, detector, ear.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ROS_DOMAIN_ID=227
# shellcheck disable=SC1091
source "$ROOT/ros2_nodes/env.sh"
export ROS_DOMAIN_ID=227
cd "$ROOT"
"$ROOT/fetch.sh"
mkdir -p "$ROOT/assets"

topic_quiet() {
  local log="$1"
  echo "--- topics ---" >>"$log"
  timeout -k 3 8 ros2 topic info /front/image_raw -v >>"$log" 2>&1 || true
  timeout -k 3 8 ros2 topic info /detections -v >>"$log" 2>&1 || true
  timeout -k 3 8 ros2 topic info /mission_event -v >>"$log" 2>&1 || true
}

echo "=== screen ==="
python3 -u "$ROOT/ros2_nodes/screen.py" >"$ROOT/assets/A_screen.log" 2>&1
topic_quiet "$ROOT/assets/A_screen.log"
grep "^SUMMARY " "$ROOT/assets/A_screen.log" || echo "NO SUMMARY for screen"

run_wired() {
  local scene="$1"
  local log="$2"
  local tmp
  tmp="$(mktemp -d)"
  echo "=== $scene ==="
  python3 -u "$ROOT/ros2_nodes/ear.py" --ros-args -p "scene:=$scene" >"$tmp/ear.log" 2>&1 &
  local ear=$!
  python3 -u "$ROOT/ros2_nodes/detector.py" --ros-args -p "scene:=$scene" >"$tmp/det.log" 2>&1 &
  local det=$!
  python3 -u "$ROOT/ros2_nodes/camera.py" --ros-args -p "scene:=$scene" >"$tmp/cam.log" 2>&1 &
  local cam=$!
  for _ in $(seq 1 80); do
    if grep -q "^READY " "$tmp/ear.log" 2>/dev/null \
      && grep -q "^READY " "$tmp/det.log" 2>/dev/null \
      && grep -q "^READY " "$tmp/cam.log" 2>/dev/null; then
      break
    fi
    sleep 0.25
  done
  {
    echo "=== $scene ==="
    cat "$tmp/cam.log" "$tmp/det.log" "$tmp/ear.log"
    echo "--- image ---"
    timeout -k 3 8 ros2 topic info /front/image_raw -v || true
    echo "--- detections ---"
    timeout -k 3 8 ros2 topic echo --once /detections vision_msgs/msg/Detection2DArray || true
    echo "--- mission ---"
    timeout -k 3 8 ros2 topic echo --once /mission_event std_msgs/msg/String || true
  } >"$log" 2>&1
  kill "$cam" "$det" "$ear" 2>/dev/null || true
  wait "$cam" "$det" "$ear" 2>/dev/null || true
  rm -rf "$tmp"
  grep "^SUMMARY " "$log" || echo "NO SUMMARY for $scene"
}

run_wired blank "$ROOT/assets/B_blank.log"
run_wired street "$ROOT/assets/C_street.log"
echo "done"
