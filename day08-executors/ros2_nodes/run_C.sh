#!/usr/bin/env bash
# Investigation C — MultiThreaded + separate MutuallyExclusive groups
set -euo pipefail
cd "$(dirname "$0")"
source ./env.sh
ros2 daemon stop >/dev/null 2>&1 || true

echo "=== C: MultiThreadedExecutor + separate MutEx groups ==="
echo "Expect: IMU/control fire during LiDAR block; during_lidar >> 0; max_active >= 2."
echo
echo "Terminal 1:"
echo "  python3 lidar_pub.py --ros-args -p period_sec:=1.5 -p warmup_sec:=1.0 -p count:=4"
echo "Terminal 2:"
echo "  python3 busy_robot_node.py --ros-args \\"
echo "    -p executor:=multi -p num_threads:=4 -p group_mode:=separate_mutex \\"
echo "    -p lidar_block_ms:=500 -p run_sec:=8.0"
