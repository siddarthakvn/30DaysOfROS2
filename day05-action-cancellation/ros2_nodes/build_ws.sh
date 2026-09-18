#!/usr/bin/env bash
# Build the Day 05 local workspace (interfaces + bringup).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WS="${ROOT}/ws"

set +u
source /opt/ros/humble/setup.bash
set -u

cd "${WS}"
colcon build --symlink-install
echo
echo "Build done. Next: source ${ROOT}/ros2_nodes/env.sh"
