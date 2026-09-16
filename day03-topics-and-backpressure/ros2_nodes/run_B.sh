#!/usr/bin/env bash
# Investigation B — Queue depth vs staleness (hero demo).
#
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

cat <<'EOF'
============================================================
Investigation B — Deep queue = high-latency zombie
============================================================
In EACH terminal:

  source ./env.sh
  ros2 daemon stop   # once after changing domain/RMW

Same overload both runs: publish_hz=30, process_ms=100, RELIABLE.
Only depth changes — MUST match on publisher and subscriber.

------------------------------------------------------------
B1 — Freshness mode: depth=1
------------------------------------------------------------
Terminal 1:
  python3 frame_camera_pub.py --ros-args \
    -p publish_hz:=30.0 -p depth:=1 -p reliability:=reliable

Terminal 2:
  python3 slow_inference_sub.py --ros-args \
    -p process_ms:=100 -p depth:=1 -p reliability:=reliable

Expect: large gaps, age_frames stays low (near live frontier).

------------------------------------------------------------
B2 — Throughput / backlog mode: depth=10
------------------------------------------------------------
Terminal 1:
  python3 frame_camera_pub.py --ros-args \
    -p publish_hz:=30.0 -p depth:=10 -p reliability:=reliable

Terminal 2:
  python3 slow_inference_sub.py --ros-args \
    -p process_ms:=100 -p depth:=10 -p reliability:=reliable

Expect: gaps still occur, but avg/max age_frames higher than B1
(acting on older frames — FIFO among cached samples).

Capture side-by-side: assets/B_depth1_vs_depth10_age.png
  (or B1_*.png and B2_*.png)
============================================================
EOF
