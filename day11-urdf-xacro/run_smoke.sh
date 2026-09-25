#!/usr/bin/env bash
# Day 11 — Investigations A/B/C evidence (headless; no RViz required).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$ROOT/ros2_nodes/env.sh"
ASSETS="$ROOT/assets"
mkdir -p "$ASSETS" "$ROS_LOG_DIR"
export PATH="${HOME}/.local/bin:${PATH}"

strip_ansi() {
  python3 -c 'import sys,re; print(re.sub(r"\x1b\[[0-9;]*m","",sys.stdin.read()), end="")'
}

kill_all() {
  pkill -f 'day11-urdf-xacro' 2>/dev/null || true
  pkill -f 'robot_state_publisher' 2>/dev/null || true
  pkill -f 'joint_demo.py' 2>/dev/null || true
  pkill -f 'display.launch.py' 2>/dev/null || true
  sleep 1
  pkill -9 -f 'robot_state_publisher' 2>/dev/null || true
  pkill -9 -f 'joint_demo.py' 2>/dev/null || true
  pkill -9 -f 'display.launch.py' 2>/dev/null || true
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
node = rclpy.create_node("day11_tf_probe")
buf = Buffer()
TransformListener(buf, node)
end = time.time() + 5.0
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

echo "=== A: fixed humanoid URDF ==="
export ROS_DOMAIN_ID=110
kill_all

{
  echo "=== A ==="
  echo "model=urdf/humanoid_fixed.urdf"
  echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
  echo
  echo "--- check_urdf ---"
  check_urdf "$ROOT/urdf/humanoid_fixed.urdf" 2>&1 || true
  echo
  echo "--- links / joints (grep) ---"
  grep -E '<(link|joint) ' "$ROOT/urdf/humanoid_fixed.urdf" || true
} | strip_ansi >"$ASSETS/A.log"

ros2 launch "$ROOT/launch/display.launch.py" \
  model:=urdf/humanoid_fixed.urdf use_joint_demo:=false \
  > /tmp/day11_A_launch.log 2>&1 &
LP=$!
sleep 3
{
  echo
  echo "--- ros2 node list ---"
  timeout 5 ros2 node list 2>&1 || true
  echo
  echo "--- robot_description length ---"
  timeout 5 ros2 param get /robot_state_publisher robot_description 2>&1 \
    | python3 -c 'import sys; d=sys.stdin.read(); print("chars=", len(d)); print("has_base_link=", "base_link" in d); print("has_r_hand=", "r_hand" in d)'
  echo
  echo "--- TF (fixed tree on /tf_static) ---"
  tf_lookup base_link r_hand
  tf_lookup base_link torso
} | strip_ansi >>"$ASSETS/A.log"
kill -INT "$LP" 2>/dev/null || true
sleep 1
kill_all
echo "Wrote $ASSETS/A.log"

echo "=== B: movable joints + joint states ==="
{
  echo "=== B ==="
  echo "model=urdf/humanoid_movable.urdf"
  echo
  echo "--- check_urdf ---"
  check_urdf "$ROOT/urdf/humanoid_movable.urdf" 2>&1 || true
  echo
  echo "--- revolute joints ---"
  grep -n 'type="revolute"' "$ROOT/urdf/humanoid_movable.urdf" || true
} | strip_ansi >"$ASSETS/B.log"

export ROS_DOMAIN_ID=111
kill_all
ros2 launch "$ROOT/launch/display.launch.py" \
  model:=urdf/humanoid_movable.urdf use_joint_demo:=true \
  joint_mode:=pose \
  joints:=r_shoulder,r_elbow \
  positions:=0.0,0.0 \
  run_sec:=15.0 \
  > /tmp/day11_B1_launch.log 2>&1 &
LP=$!
sleep 5
{
  echo
  echo "--- pose1 ROS_DOMAIN_ID=$ROS_DOMAIN_ID shoulder=0 elbow=0 ---"
  tf_lookup base_link r_hand
} | strip_ansi >>"$ASSETS/B.log"
kill -INT "$LP" 2>/dev/null || true
sleep 1
kill_all

export ROS_DOMAIN_ID=112
kill_all
ros2 launch "$ROOT/launch/display.launch.py" \
  model:=urdf/humanoid_movable.urdf use_joint_demo:=true \
  joint_mode:=pose \
  joints:=r_shoulder,r_elbow \
  positions:=0.80,1.20 \
  run_sec:=15.0 \
  > /tmp/day11_B2_launch.log 2>&1 &
LP=$!
sleep 5
{
  echo
  echo "--- pose2 ROS_DOMAIN_ID=$ROS_DOMAIN_ID shoulder=0.80 elbow=1.20 ---"
  tf_lookup base_link r_hand
  echo
  echo "Expect: r_hand translation differs between pose1 and pose2 (H2/H3/H6)."
} | strip_ansi >>"$ASSETS/B.log"
kill -INT "$LP" 2>/dev/null || true
sleep 1
kill_all
echo "Wrote $ASSETS/B.log"

echo "=== C: Xacro left/right arms ==="
export ROS_DOMAIN_ID=113
kill_all

XACRO_OUT="$ASSETS/humanoid_xacro_expanded.urdf"
xacro "$ROOT/xacro/humanoid.urdf.xacro" >"$XACRO_OUT"

{
  echo "=== C ==="
  echo "model=xacro/humanoid.urdf.xacro"
  echo "expanded=$XACRO_OUT"
  echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
  echo
  echo "--- xacro expand (link/joint names) ---"
  grep -E '<(link|joint) ' "$XACRO_OUT" || true
  echo
  echo "--- check_urdf on expanded URDF ---"
  check_urdf "$XACRO_OUT" 2>&1 || true
  echo
  echo "--- L/R symmetry counts ---"
  echo -n "r_ name hits: "; grep -c 'name="r_' "$XACRO_OUT" || true
  echo -n "l_ name hits: "; grep -c 'name="l_' "$XACRO_OUT" || true
  echo -n "r_shoulder present: "; grep -c 'name="r_shoulder"' "$XACRO_OUT" || true
  echo -n "l_shoulder present: "; grep -c 'name="l_shoulder"' "$XACRO_OUT" || true
} | strip_ansi >"$ASSETS/C.log"

ros2 launch "$ROOT/launch/display.launch.py" \
  model:=xacro/humanoid.urdf.xacro use_joint_demo:=true \
  joint_mode:=zero \
  joints:=r_shoulder,r_elbow,l_shoulder,l_elbow \
  positions:=0.0,0.0,0.0,0.0 \
  run_sec:=12.0 \
  > /tmp/day11_C_launch.log 2>&1 &
LP=$!
sleep 4
{
  echo
  echo "--- TF both hands at zero joint states ---"
  tf_lookup base_link r_hand
  tf_lookup base_link l_hand
  echo
  echo "Expect: mirrored X for left vs right hand (H4)."
} | strip_ansi >>"$ASSETS/C.log"
kill -INT "$LP" 2>/dev/null || true
sleep 1
kill_all

{
  echo "Day 11 URDF / Xacro comparison"
  echo
  for tag in A B C; do
    echo "----- ${tag} -----"
    cat "$ASSETS/${tag}.log"
    echo
  done
} >"$ASSETS/comparison.txt"

echo DONE
