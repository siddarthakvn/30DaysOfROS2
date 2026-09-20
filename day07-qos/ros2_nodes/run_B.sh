#!/usr/bin/env bash
# Investigation B — reliability mismatch (silent failure), then fix
set -euo pipefail
cd "$(dirname "$0")"
source ./env.sh
ros2 daemon stop >/dev/null 2>&1 || true

echo "=== B1: MISMATCH — BEST_EFFORT pub + RELIABLE sub (expect ZERO receives) ==="
echo "Terminal 1:"
echo "  python3 qos_pub.py --ros-args -p reliability:=best_effort -p durability:=volatile"
echo "Terminal 2:"
echo "  python3 qos_sub.py --ros-args -p reliability:=reliable -p durability:=volatile"
echo "Terminal 3:"
echo "  ros2 topic info /qos_demo/stream --verbose"
echo "Expect: topic exists, both endpoints visible, SUB recv_total stays 0."
echo
echo "=== B2: FIX — change sub to BEST_EFFORT (expect flow) ==="
echo "  python3 qos_sub.py --ros-args -p reliability:=best_effort -p durability:=volatile"
