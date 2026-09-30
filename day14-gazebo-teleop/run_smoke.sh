#!/usr/bin/env bash
# Day 14 — key → Twist → Gazebo Harmonic diff-drive.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$ROOT/ros2_nodes/env.sh"
ASSETS="$ROOT/assets"
mkdir -p "$ASSETS" "$ROS_LOG_DIR"
WORLD="/usr/share/gz/gz-sim8/worlds/diff_drive.sdf"
TOPIC="/model/vehicle_blue/cmd_vel"
ODOM="/model/vehicle_blue/odometry"
BRIDGE_SPEC="${TOPIC}@geometry_msgs/msg/Twist]gz.msgs.Twist"

strip_ansi() {
  python3 -c 'import sys,re; print(re.sub(r"\x1b\[[0-9;]*m","",sys.stdin.read()), end="")'
}

kill_all() {
  pkill -f 'day14-gazebo-teleop/ros2_nodes/key_twist.py' 2>/dev/null || true
  pkill -f 'ros_gz_bridge' 2>/dev/null || true
  pkill -f 'parameter_bridge' 2>/dev/null || true
  pkill -f 'gz sim' 2>/dev/null || true
  pkill -f 'gz-sim-server' 2>/dev/null || true
  sleep 1
  pkill -9 -f 'key_twist.py' 2>/dev/null || true
  pkill -9 -f 'parameter_bridge' 2>/dev/null || true
  pkill -9 -f 'gz-sim' 2>/dev/null || true
  ros2 daemon stop >/dev/null 2>&1 || true
  sleep 1
}

pose_line() {
  local label="$1"
  local out
  out="$(timeout 8 gz topic -e -t "$ODOM" -n 1 2>/dev/null || true)"
  LABEL="$label" TEXT="$out" python3 - <<'PY'
import os
label = os.environ["LABEL"]
text = os.environ.get("TEXT", "")

def grab(block, name):
    idx = text.find(block)
    if idx < 0:
        return None
    window = text[idx:idx + 500]
    for line in window.splitlines():
        line = line.strip()
        if line.startswith(name + ":"):
            return line.split(":", 1)[1].strip()
    return None

px = grab("position {", "x") or grab("position{", "x")
py = grab("position {", "y") or grab("position{", "y")
print(f"{label} pose x={px} y={py}")
if "position" not in text:
    print(label, "RAW_MISSING")
    print(text[:800])
PY
}

echo "=== A: teleop key bindings become Twist fields ==="
export ROS_DOMAIN_ID=140
kill_all
{
  echo "=== A ==="
  echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
  echo "Package: teleop_twist_keyboard moveBindings, speed=0.5 turn=1.0"
  echo "This node does not drive wheels. It only publishes geometry_msgs/Twist."
  echo
  for key in i j k; do
    echo "--- key '$key' ---"
    python3 "$ROOT/ros2_nodes/echo_once.py" "$TOPIC" >"/tmp/day14_A_${key}_echo.log" 2>&1 &
    echo_pid=$!
    sleep 0.4
    python3 "$ROOT/ros2_nodes/key_twist.py" --ros-args \
      -p "key:=$key" -p "topic:=$TOPIC" -p run_sec:=1.5 \
      >"/tmp/day14_A_${key}.log" 2>&1 &
    pid=$!
    wait "$echo_pid" 2>/dev/null || true
    echo "publisher log:"
    grep -E 'KEY source|complete' "/tmp/day14_A_${key}.log" | strip_ansi || true
    echo "echo:"
    cat "/tmp/day14_A_${key}_echo.log" | strip_ansi || true
    wait "$pid" 2>/dev/null || true
    echo
  done
} | strip_ansi >"$ASSETS/A.log"
echo "Wrote $ASSETS/A.log"

echo "=== B: no bridge, Gazebo does not see the ROS publisher ==="
export ROS_DOMAIN_ID=141
kill_all
gz sim -s -r -v 2 "$WORLD" > /tmp/day14_gz.log 2>&1 &
GZ=$!
sleep 4
python3 "$ROOT/ros2_nodes/key_twist.py" --ros-args \
  -p key:=i -p "topic:=$TOPIC" -p run_sec:=8.0 \
  > /tmp/day14_B_pub.log 2>&1 &
PUB=$!
sleep 1.5
{
  echo "=== B ==="
  echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
  echo "world=$WORLD"
  echo "Gazebo Harmonic server only. Bridge NOT started."
  echo
  echo "--- ros2 topic info (ROS side) ---"
  timeout 6 ros2 topic info "$TOPIC" -v 2>&1 || true
  echo
  echo "--- gz topic info (Gazebo Transport side) ---"
  timeout 6 gz topic -i -t "$TOPIC" 2>&1 || true
  echo
  echo "Expect: a ROS publisher exists, and no ROS-side bridge publisher on gz yet."
} | strip_ansi >"$ASSETS/B.log"
kill "$PUB" 2>/dev/null || true
kill "$GZ" 2>/dev/null || true
sleep 1
kill_all
echo "Wrote $ASSETS/B.log"

echo "=== C: bridge + diff-drive, forward moves, sideways command does not ==="
export ROS_DOMAIN_ID=142
kill_all
gz sim -s -r -v 2 "$WORLD" > /tmp/day14_gz_c.log 2>&1 &
GZ=$!
sleep 4
ros2 run ros_gz_bridge parameter_bridge "$BRIDGE_SPEC" > /tmp/day14_bridge.log 2>&1 &
BR=$!
sleep 2
{
  echo "=== C ==="
  echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
  echo "bridge=$BRIDGE_SPEC"
  echo "Gazebo: Harmonic (gz sim 8). Humble docs show Fortress + ignition.msgs."
  echo "This run uses gz.msgs.Twist because that is what this machine speaks."
  echo
  echo "--- bridge log ---"
  grep -E 'Creating|Failed|error|Error' /tmp/day14_bridge.log | strip_ansi || true
  echo
  echo "--- pose before ---"
  pose_line BEFORE
} | strip_ansi >"$ASSETS/C.log"

python3 "$ROOT/ros2_nodes/key_twist.py" --ros-args \
  -p key:=i -p "topic:=$TOPIC" -p run_sec:=3.0 \
  > /tmp/day14_C_forward.log 2>&1
sleep 0.5
{
  echo
  echo "--- after key i (linear.x=0.5, angular.z=0) ---"
  grep 'KEY source' /tmp/day14_C_forward.log | strip_ansi || true
  pose_line AFTER_FORWARD
} | strip_ansi >>"$ASSETS/C.log"

python3 "$ROOT/ros2_nodes/key_twist.py" --ros-args \
  -p key:=k -p "topic:=$TOPIC" -p run_sec:=2.0 \
  > /tmp/day14_C_stop.log 2>&1
sleep 1.0
{
  echo
  echo "--- after stop, so the forward command can decay ---"
  grep 'KEY source' /tmp/day14_C_stop.log | strip_ansi || true
  pose_line AFTER_STOP
} | strip_ansi >>"$ASSETS/C.log"

python3 "$ROOT/ros2_nodes/key_twist.py" --ros-args \
  -p key:=k -p override:=linear_y -p override_speed:=0.5 \
  -p "topic:=$TOPIC" -p run_sec:=3.0 \
  > /tmp/day14_C_strafe.log 2>&1
sleep 0.5
{
  echo
  echo "--- after linear.y=0.5 only (diff-drive cannot strafe) ---"
  grep 'KEY source' /tmp/day14_C_strafe.log | strip_ansi || true
  pose_line AFTER_STRAFE
  echo
  echo "--- gz topic publishers after bridge ---"
  timeout 6 gz topic -i -t "$TOPIC" 2>&1 || true
} | strip_ansi >>"$ASSETS/C.log"

kill "$BR" 2>/dev/null || true
kill "$GZ" 2>/dev/null || true
sleep 1
kill_all
echo "Wrote $ASSETS/C.log"

{
  echo "Day 14 — key to simulated motion"
  echo
  for tag in A B C; do
    echo "----- ${tag} -----"
    cat "$ASSETS/${tag}.log"
    echo
  done
} >"$ASSETS/comparison.txt"

echo DONE
