#!/usr/bin/env bash
# Investigation A — SingleThreadedExecutor starvation
set -euo pipefail
cd "$(dirname "$0")"
source ./env.sh
ros2 daemon stop >/dev/null 2>&1 || true

echo "=== A: SingleThreadedExecutor + default MutEx group ==="
echo "Expect: during 500ms LiDAR sleep, IMU/control during_lidar ≈ 0; large max_gap."
echo
echo "Terminal 1:"
echo "  python3 lidar_pub.py --ros-args -p period_sec:=1.5 -p warmup_sec:=1.0 -p count:=4"
echo "Terminal 2:"
echo "  python3 busy_robot_node.py --ros-args \\"
echo "    -p executor:=single -p group_mode:=default \\"
echo "    -p lidar_block_ms:=500 -p run_sec:=8.0"
