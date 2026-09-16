#!/usr/bin/env bash
# Investigation C — Sensor-profile thinking (light reliability contrast).
#
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

cat <<'EOF'
============================================================
Investigation C — Sensor QoS contrast (localhost, honest)
============================================================
In EACH terminal:

  source ./env.sh
  ros2 daemon stop   # once after changing domain/RMW

Fixed: publish_hz=30, process_ms=100, KEEP_LAST depth=5.
Vary reliability — MUST match on publisher and subscriber.

------------------------------------------------------------
C1 — depth=5, RELIABLE
------------------------------------------------------------
Terminal 1:
  python3 frame_camera_pub.py --ros-args \
    -p publish_hz:=30.0 -p depth:=5 -p reliability:=reliable

Terminal 2:
  python3 slow_inference_sub.py --ros-args \
    -p process_ms:=100 -p depth:=5 -p reliability:=reliable

------------------------------------------------------------
C2 — depth=5, BEST_EFFORT
------------------------------------------------------------
Terminal 1:
  python3 frame_camera_pub.py --ros-args \
    -p publish_hz:=30.0 -p depth:=5 -p reliability:=best_effort

Terminal 2:
  python3 slow_inference_sub.py --ros-args \
    -p process_ms:=100 -p depth:=5 -p reliability:=best_effort

Expect: history-overflow gaps in both. On localhost, C1 and C2 may look
similar — that is a valid result (reliability ≠ history overflow).

Capture: assets/C_reliable_vs_best_effort.png
============================================================
EOF
