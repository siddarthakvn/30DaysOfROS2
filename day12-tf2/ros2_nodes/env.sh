#!/usr/bin/env bash
# Shared environment for Day 12.
set +u
source /opt/ros/humble/setup.bash
set -u

export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-120}"
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export RCUTILS_COLORIZED_OUTPUT=1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ROS_LOG_DIR="${ROS_LOG_DIR:-$ROOT/assets/.ros_logs}"
mkdir -p "$ROS_LOG_DIR"

cd "$(dirname "${BASH_SOURCE[0]}")"
echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
echo "RMW_IMPLEMENTATION=$RMW_IMPLEMENTATION"
echo "cwd=$(pwd)"
