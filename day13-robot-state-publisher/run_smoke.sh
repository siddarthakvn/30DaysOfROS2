#!/usr/bin/env bash
# Day 13 — who publishes the robot TF tree.
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
  pkill -f 'day13-robot-state-publisher/launch/tree.launch.py' 2>/dev/null || true
  pkill -f 'day13-robot-state-publisher/ros2_nodes/joint_angles.py' 2>/dev/null || true
  pkill -f '/opt/ros/humble/lib/robot_state_publisher/robot_state_publisher' 2>/dev/null || true
  sleep 1
  pkill -9 -f 'day13-robot-state-publisher/launch/tree.launch.py' 2>/dev/null || true
  pkill -9 -f 'day13-robot-state-publisher/ros2_nodes/joint_angles.py' 2>/dev/null || true
  pkill -9 -f '/opt/ros/humble/lib/robot_state_publisher/robot_state_publisher' 2>/dev/null || true
  ros2 daemon stop >/dev/null 2>&1 || true
  sleep 1
}

tf_lookup() {
  local parent="$1" child="$2"
  python3 - <<PY
import time
import rclpy
from tf2_ros import Buffer, TransformListener
rclpy.init()
node = rclpy.create_node("day13_tf_probe")
buf = Buffer()
TransformListener(buf, node)
end = time.time() + 4.0
ok = False
while time.time() < end and rclpy.ok():
    rclpy.spin_once(node, timeout_sec=0.2)
    try:
        t = buf.lookup_transform("${parent}", "${child}", rclpy.time.Time())
        tr = t.transform.translation
        print(f"TF ${parent} -> ${child}: x={tr.x:+.4f} y={tr.y:+.4f} z={tr.z:+.4f}")
        ok = True
        break
    except Exception:
        pass
if not ok:
    print(f"TF ${parent} -> ${child}: NOT_AVAILABLE")
node.destroy_node()
rclpy.shutdown()
PY
}

topic_owners() {
  echo "--- /tf publishers ---"
  timeout 6 ros2 topic info /tf -v 2>&1 || true
  echo
  echo "--- /tf_static publishers ---"
  timeout 6 ros2 topic info /tf_static -v 2>&1 || true
  echo
  echo "--- /joint_states publishers ---"
  timeout 6 ros2 topic info /joint_states -v 2>&1 || true
}

echo "=== A: robot_state_publisher, no joint states ==="
export ROS_DOMAIN_ID=130
kill_all
ros2 launch "$ROOT/launch/tree.launch.py" use_joint_angles:=false \
  > /tmp/day13_A.log 2>&1 &
LP=$!
sleep 4
{
  echo "=== A ==="
  echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
  echo "nodes: robot_state_publisher only"
  echo
  echo "--- ros2 node list ---"
  timeout 5 ros2 node list 2>&1 || true
  echo
  topic_owners
  echo
  echo "--- TF lookups (fixed should exist; full arm should not) ---"
  tf_lookup base_link torso
  tf_lookup forearm hand
  tf_lookup base_link hand
  tf_lookup map base_link
} | strip_ansi >"$ASSETS/A.log"
kill -INT "$LP" 2>/dev/null || true
sleep 1
kill_all
echo "Wrote $ASSETS/A.log"

echo "=== B: joint angles move the arm; RSP publishes /tf ==="
export ROS_DOMAIN_ID=131
kill_all
ros2 launch "$ROOT/launch/tree.launch.py" \
  use_joint_angles:=true shoulder:=0.0 elbow:=0.0 run_sec:=12.0 \
  > /tmp/day13_B0.log 2>&1 &
LP=$!
sleep 4
{
  echo "=== B ==="
  echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
  echo
  echo "--- pose 0 / 0 ---"
  tf_lookup base_link hand
} | strip_ansi >"$ASSETS/B.log"
kill -INT "$LP" 2>/dev/null || true
sleep 1
kill_all

export ROS_DOMAIN_ID=132
ros2 launch "$ROOT/launch/tree.launch.py" \
  use_joint_angles:=true shoulder:=0.80 elbow:=1.20 run_sec:=12.0 \
  > /tmp/day13_B1.log 2>&1 &
LP=$!
sleep 4
{
  echo
  echo "--- pose 0.80 / 1.20 ---"
  tf_lookup base_link hand
  echo
  echo "Expect: hand translation changes. joint_angles does not publish TF."
} | strip_ansi >>"$ASSETS/B.log"
kill -INT "$LP" 2>/dev/null || true
sleep 1
kill_all
echo "Wrote $ASSETS/B.log"

echo "=== C: who publishes what ==="
export ROS_DOMAIN_ID=133
kill_all
ros2 launch "$ROOT/launch/tree.launch.py" \
  use_joint_angles:=true shoulder:=0.40 elbow:=0.50 run_sec:=12.0 \
  > /tmp/day13_C.log 2>&1 &
LP=$!
sleep 6
{
  echo "=== C ==="
  echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
  echo "Question: which node owns /tf, /tf_static, and /joint_states?"
  echo
  echo "--- ros2 node list ---"
  timeout 5 ros2 node list 2>&1 || true
  echo
  topic_owners
  echo
  echo "--- world frames (RSP must not invent these) ---"
  tf_lookup map base_link
  tf_lookup odom base_link
} | strip_ansi >"$ASSETS/C.log"
kill -INT "$LP" 2>/dev/null || true
sleep 1
kill_all
echo "Wrote $ASSETS/C.log"

{
  echo "Day 13 — who publishes the robot TF tree"
  echo
  for tag in A B C; do
    echo "----- ${tag} -----"
    cat "$ASSETS/${tag}.log"
    echo
  done
} >"$ASSETS/comparison.txt"

echo DONE
