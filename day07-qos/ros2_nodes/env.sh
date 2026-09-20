#!/usr/bin/env bash
# Shared environment pin for Day 07. Source this from every terminal.
#
#   source ./env.sh

set +u
source /opt/ros/humble/setup.bash
set -u

export ROS_DOMAIN_ID=70
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export RCUTILS_COLORIZED_OUTPUT=1

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
echo "RMW_IMPLEMENTATION=$RMW_IMPLEMENTATION"
echo "cwd=$(pwd)"
