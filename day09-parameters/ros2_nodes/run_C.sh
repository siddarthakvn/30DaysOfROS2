#!/usr/bin/env bash
# Investigation C — validation rejects unsafe values
set -euo pipefail
cd "$(dirname "$0")"
source ./env.sh
ros2 daemon stop >/dev/null 2>&1 || true

echo "=== C: Reject max_velocity=10.0 (outside [0, 2]) ==="
echo "Expect: set fails; STORED stays previous; PARAM_REJECT in logs."
echo
echo "Terminal 1:"
echo "  python3 velocity_governor.py --ros-args \\"
echo "    -p max_velocity:=1.0 -p request_vx:=1.5 -p apply_mode:=live -p run_sec:=10.0"
echo "Terminal 2:"
echo "  ros2 param set /velocity_governor max_velocity 10.0"
echo "  ros2 param get /velocity_governor max_velocity"
