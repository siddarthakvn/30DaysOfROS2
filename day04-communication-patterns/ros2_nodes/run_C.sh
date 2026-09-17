#!/usr/bin/env bash
# Investigation C — Action feedback + cancel (hero).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

cat <<'EOF'
============================================================
Investigation C — Action feedback + cancel
============================================================
In EACH terminal:

  source ./env.sh
  ros2 daemon stop   # once after changing domain/RMW

------------------------------------------------------------
Terminal 1 — turtlesim (provides /turtle1/rotate_absolute)
------------------------------------------------------------
  ros2 run turtlesim turtlesim_node

Confirm:
  ros2 action list
  ros2 action info /turtle1/rotate_absolute
  ros2 interface show turtlesim/action/RotateAbsolute

------------------------------------------------------------
C0 — Goal to completion (feedback + result)
------------------------------------------------------------
Terminal 2:
  ros2 action send_goal --feedback /turtle1/rotate_absolute \
    turtlesim/action/RotateAbsolute "{theta: 3.14}"

Expect: Accepted; feedback remaining decreases; Result SUCCEEDED with delta.

------------------------------------------------------------
C1 — Cancel mid-goal (H1 / H2 hero)
------------------------------------------------------------
Reset heading for a clear rotate:
  ros2 service call /turtle1/teleport_absolute turtlesim/srv/TeleportAbsolute \
    "{x: 5.5, y: 5.5, theta: 0.0}"

Terminal 2 — reproducible cancel client (preferred):
  python3 action_cancel_demo.py --ros-args \
    -p theta:=3.14 -p cancel_after_sec:=1.0

Optional interactive CLI (Ctrl+C after feedback appears):
  ros2 action send_goal --feedback /turtle1/rotate_absolute \
    turtlesim/action/RotateAbsolute "{theta: 3.14}"
  # Note: theta:=6.28 from theta=0 is ~identity (finishes instantly).

Expect:
  - Mid-flight feedback (remaining)
  - Cancel path → terminal status CANCELED
  - Correlated result — not a silent Topic dropout

Compare mentally with A (stop publisher) and B (Ctrl+C client).

Capture: assets/C0_*.png  assets/C1_*.png  (or *.log transcripts)
============================================================
EOF
