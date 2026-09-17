#!/usr/bin/env bash
# Investigation B — Long Service anti-pattern (no cancel / no feedback).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

cat <<'EOF'
============================================================
Investigation B — Long-running Service (anti-pattern)
============================================================
In EACH terminal:

  source ./env.sh
  ros2 daemon stop   # once after changing domain/RMW

------------------------------------------------------------
Terminal 1 — turtlesim
------------------------------------------------------------
  ros2 run turtlesim turtlesim_node

------------------------------------------------------------
Terminal 2 — long rotate service server
------------------------------------------------------------
  python3 long_rotate_server.py --ros-args -p duration_sec:=5.0 -p angular_z:=1.0

Confirm:
  ros2 service list | grep long_rotate
  ros2 service type /long_rotate
  # expect std_srvs/srv/Trigger

------------------------------------------------------------
B0 — Happy path (single response after ~5 s)
------------------------------------------------------------
Terminal 3:
  python3 long_rotate_client.py

Expect: client blocks ~5 s; ONE response; server logs SPIN lines;
        no mid-flight feedback messages to the client.

------------------------------------------------------------
B1 — Interrupt client mid-call (H1)
------------------------------------------------------------
Reset turtle if needed, restart server if busy flag stuck (Ctrl+C server + relaunch).

Terminal 3:
  python3 long_rotate_client.py
  # After ~2 s: Ctrl+C the CLIENT only

Watch Terminal 2 (server): does rotation continue until duration ends?
Watch turtlesim: does the turtle keep spinning?

Expect:
  - No cancel API on the service
  - Client Ctrl+C ≠ server cancel
  - Server may finish the full duration (confirm — do not invent)

Optional: second client while busy:
  python3 long_rotate_client.py
  # expect rejected: already rotating

Capture: assets/B0_*.png  assets/B1_*.png
============================================================
EOF
