#!/usr/bin/env bash
# Investigation A — compatible QoS (messages should flow)
set -euo pipefail
cd "$(dirname "$0")"
source ./env.sh
ros2 daemon stop >/dev/null 2>&1 || true

echo "=== A: Compatible RELIABLE + VOLATILE both sides ==="
echo "Terminal 1:"
echo "  python3 qos_pub.py --ros-args -p reliability:=reliable -p durability:=volatile"
echo "Terminal 2:"
echo "  python3 qos_sub.py --ros-args -p reliability:=reliable -p durability:=volatile"
echo "Terminal 3:"
echo "  ros2 topic info /qos_demo/stream --verbose"
echo "Expect: SUB recv_total increases; last_seq advances."
