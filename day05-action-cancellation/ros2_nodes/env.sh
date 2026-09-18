#!/usr/bin/env bash
# Shared environment pin for Day 05. Source this from every terminal.
#
#   source ./env.sh

set +u
source /opt/ros/humble/setup.bash

DAY05_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="${DAY05_ROOT}/ws"

if [[ -f "${WS}/install/setup.bash" ]]; then
  # shellcheck disable=SC1091
  source "${WS}/install/setup.bash"
else
  echo "WARN: ${WS}/install/setup.bash missing — run: cd ${WS} && colcon build" >&2
fi
set -u

export ROS_DOMAIN_ID=45
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export RCUTILS_COLORIZED_OUTPUT=1

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
echo "RMW_IMPLEMENTATION=$RMW_IMPLEMENTATION"
echo "DAY05_ROOT=$DAY05_ROOT"
echo "cwd=$(pwd)"
