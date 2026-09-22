#!/usr/bin/env bash
# Investigation A — YAML overrides code default at startup
set -euo pipefail
cd "$(dirname "$0")"
source ./env.sh
ros2 daemon stop >/dev/null 2>&1 || true

echo "=== A: YAML startup override (code default 1.0 -> YAML 0.5) ==="
echo "Expect: STORED/EFFECTIVE max_velocity=0.5; TICK out=0.5"
echo
echo "  python3 velocity_governor.py --ros-args --params-file ../config/cruise_limit.yaml"
