#!/usr/bin/env bash
# Investigation A — Topic stream motion (stop publishing ≠ cancel).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

cat <<'EOF'
============================================================
Investigation A — Topic stream motion
============================================================
In EACH terminal:

  source ./env.sh
  ros2 daemon stop   # once after changing domain/RMW

Confirm RMW:
  ros2 doctor --report | grep -i rmw
  # expect rmw_fastrtps_cpp

------------------------------------------------------------
Terminal 1 — turtlesim
------------------------------------------------------------
  ros2 run turtlesim turtlesim_node

------------------------------------------------------------
A0 — Full burst (baseline motion)
------------------------------------------------------------
Terminal 2:
  python3 cmd_vel_burst.py --ros-args \
    -p duration_sec:=5.0 -p angular_z:=1.0 -p send_zero_on_exit:=true

Expect: turtle rotates ~5 s; zero Twist on exit; clean visual stop.

------------------------------------------------------------
A1 — Interrupt by stopping the publisher (hero for H3)
------------------------------------------------------------
Reset turtle pose if needed:
  ros2 service call /turtle1/teleport_absolute turtlesim/srv/TeleportAbsolute \
    "{x: 5.5, y: 5.5, theta: 0.0}"
  ros2 service call /clear std_srvs/srv/Empty "{}"

Terminal 2:
  python3 cmd_vel_burst.py --ros-args \
    -p duration_sec:=5.0 -p stop_after_sec:=2.0 -p angular_z:=1.0 \
    -p send_zero_on_exit:=false

Optional Terminal 3 (during / after burst):
  ros2 topic echo /turtle1/pose --once
  ros2 topic info /turtle1/cmd_vel
  # There is NO ros2 action lifecycle for this motion.

Expect:
  - Motion while publisher is alive
  - After exit: no goal ID, no CANCELING/CANCELED, no Action feedback
  - Turtle may keep last velocity or coast depending on turtlesim — observe honestly
  - "Stop publishing" is not a cancel protocol

Capture: assets/A0_*.png  assets/A1_*.png  (turtlesim + terminal)
============================================================
EOF
