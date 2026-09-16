#!/usr/bin/env bash
# Investigation A — Firehose does not wait (no app-level backpressure).
#
# Prints the exact commands for A0 (keep-up) and A1 (overload).
# Run publisher and subscriber in separate terminals after: source ./env.sh
#
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

cat <<'EOF'
============================================================
Investigation A — The firehose does not wait
============================================================
In EACH terminal:

  source ./env.sh
  ros2 daemon stop   # once after changing domain/RMW

Confirm RMW:
  ros2 doctor --report | grep -i rmw
  # expect rmw_fastrtps_cpp

------------------------------------------------------------
A0 — Baseline (can keep up): process_ms=25, depth=10, RELIABLE
------------------------------------------------------------
Terminal 1:
  python3 frame_camera_pub.py --ros-args \
    -p publish_hz:=30.0 -p depth:=10 -p reliability:=reliable

Terminal 2:
  python3 slow_inference_sub.py --ros-args \
    -p process_ms:=25 -p depth:=10 -p reliability:=reliable

Run ~15s. Expect: few/no gaps, low age_frames, process_hz ≈ publish_hz.

------------------------------------------------------------
A1 — Overload: process_ms=100, depth=10, RELIABLE
------------------------------------------------------------
Terminal 1:
  python3 frame_camera_pub.py --ros-args \
    -p publish_hz:=30.0 -p depth:=10 -p reliability:=reliable

Terminal 2:
  python3 slow_inference_sub.py --ros-args \
    -p process_ms:=100 -p depth:=10 -p reliability:=reliable

Optional Terminal 3 (short window only — CLI adds a subscriber):
  ros2 topic info /perception/frames -v
  ros2 topic hz /perception/frames

Run ~15–20s. Expect: PUB ~30 Hz, PROC ~10 Hz, gaps > 0, age_frames rises
then saturates near depth (order of magnitude).

Capture: assets/A0_*.png  assets/A1_*.png  assets/00_rmw_pin.png
============================================================
EOF
