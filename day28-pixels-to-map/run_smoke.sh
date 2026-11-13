#!/usr/bin/env bash
# A publishes the pixel only. B drops that point on the map origin. C uses TF.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ROS_DOMAIN_ID=226
# shellcheck disable=SC1091
source "$ROOT/ros2_nodes/env.sh"
export ROS_DOMAIN_ID=226
cd "$ROOT"
mkdir -p "$ROOT/assets"

wait_ready() {
  local log="$1"
  local needle="$2"
  for _ in $(seq 1 80); do
    if grep -q "$needle" "$log" 2>/dev/null; then
      return 0
    fi
    sleep 0.25
  done
  return 1
}

echo "=== pixel ==="
python3 -u "$ROOT/ros2_nodes/scene.py" >"$ROOT/assets/A_pixel.log" 2>&1 &
scene=$!
wait_ready "$ROOT/assets/A_pixel.log" "^READY " || true
{
  echo "--- pixel ---"
  timeout -k 3 8 ros2 topic echo --once /pixel geometry_msgs/msg/PointStamped || true
  echo "--- depth ---"
  timeout -k 3 8 ros2 topic echo --once /depth std_msgs/msg/Float64 || true
  echo "--- point_camera ---"
  timeout -k 3 8 ros2 topic info /point_camera -v || true
  echo "--- point_map ---"
  timeout -k 3 8 ros2 topic info /point_map -v || true
  echo "--- goal ---"
  timeout -k 3 8 ros2 topic info /goal -v || true
} >>"$ROOT/assets/A_pixel.log" 2>&1
kill "$scene" 2>/dev/null || true
wait "$scene" 2>/dev/null || true
grep "^SUMMARY " "$ROOT/assets/A_pixel.log" || echo "NO SUMMARY for pixel"

run_chain() {
  local mode="$1"
  local log="$2"
  local tmp
  tmp="$(mktemp -d)"
  echo "=== $mode ==="
  python3 -u "$ROOT/ros2_nodes/scene.py" >"$tmp/scene.log" 2>&1 &
  local scene=$!
  python3 -u "$ROOT/ros2_nodes/ray.py" >"$tmp/ray.log" 2>&1 &
  local ray=$!
  python3 -u "$ROOT/ros2_nodes/placer.py" --ros-args -p "mode:=$mode" >"$tmp/placer.log" 2>&1 &
  local placer=$!
  wait_ready "$tmp/scene.log" "^READY " || true
  wait_ready "$tmp/ray.log" "^READY " || true
  wait_ready "$tmp/placer.log" "^READY " || true
  {
    echo "=== $mode ==="
    cat "$tmp/scene.log" "$tmp/ray.log" "$tmp/placer.log"
    echo "--- pixel ---"
    timeout -k 3 8 ros2 topic echo --once /pixel geometry_msgs/msg/PointStamped || true
    echo "--- point_camera ---"
    timeout -k 3 8 ros2 topic echo --once /point_camera geometry_msgs/msg/PointStamped || true
    echo "--- point_map ---"
    timeout -k 3 8 ros2 topic echo --once /point_map geometry_msgs/msg/PointStamped || true
    echo "--- goal ---"
    timeout -k 3 8 ros2 topic echo --once /goal geometry_msgs/msg/PoseStamped || true
    echo "--- tf ---"
    timeout -k 2 3 ros2 run tf2_ros tf2_echo map camera_optical_frame || true
  } >"$log" 2>&1
  kill "$scene" "$ray" "$placer" 2>/dev/null || true
  wait "$scene" "$ray" "$placer" 2>/dev/null || true
  rm -rf "$tmp"
  grep "^SUMMARY " "$log" || echo "NO SUMMARY for $mode"
}

run_chain origin "$ROOT/assets/B_origin.log"
run_chain map "$ROOT/assets/C_map.log"
echo "done"
