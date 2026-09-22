#!/usr/bin/env bash
# Investigation B — runtime ros2 param set changes live behavior
set -euo pipefail
cd "$(dirname "$0")"
source ./env.sh
ros2 daemon stop >/dev/null 2>&1 || true

echo "=== B: Runtime tune without restart (apply_mode=live) ==="
echo "Expect: after set max_velocity:=0.3, TICK out drops to 0.3 while node stays up."
echo
echo "Terminal 1:"
echo "  python3 velocity_governor.py --ros-args \\"
echo "    -p max_velocity:=1.0 -p request_vx:=1.5 -p apply_mode:=live -p run_sec:=10.0"
echo "Terminal 2 (after a few TICKs):"
echo "  ros2 param set /velocity_governor max_velocity 0.3"
echo "  ros2 param get /velocity_governor max_velocity"
