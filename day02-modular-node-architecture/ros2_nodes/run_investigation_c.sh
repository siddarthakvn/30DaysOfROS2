#!/usr/bin/env bash
#
# Investigation C — runs both deployments of the same four ROS 2 nodes,
# so the only variable is how many processes they are spread across.
#
#   C1: four nodes, four processes  -> expect three survivors
#   C2: four nodes, one process     -> expect zero survivors
#
set -o pipefail

# Humble's setup.bash may reference unset vars (e.g. AMENT_TRACE_SETUP_FILES).
# Disable nounset only while sourcing, then re-enable for the rest of the script.
set +u
source /opt/ros/humble/setup.bash
set -u

export ROS_DOMAIN_ID=42
export RCUTILS_COLORIZED_OUTPUT=0

cd "$(dirname "${BASH_SOURCE[0]}")"

CRASH_AFTER=4
LOGS="$(mktemp -d)"

echo "###############################################################"
echo "#  C1 — FOUR NODES, FOUR PROCESSES                            #"
echo "###############################################################"

python3 sensor_node.py gps            > "$LOGS/gps.log"    2>&1 &  GPS=$!
python3 sensor_node.py imu            > "$LOGS/imu.log"    2>&1 &  IMU=$!
python3 sensor_node.py motor          > "$LOGS/motor.log"  2>&1 &  MOTOR=$!
python3 sensor_node.py camera "$CRASH_AFTER" > "$LOGS/camera.log" 2>&1 &  CAMERA=$!

sleep $(( CRASH_AFTER + 4 ))

echo
echo "--- how the camera ended ---"
tail -2 "$LOGS/camera.log"

echo
echo "--- who is still alive? ---"
for entry in "GPS:$GPS" "IMU:$IMU" "MOTOR:$MOTOR" "CAMERA:$CAMERA"; do
    name="${entry%%:*}"; pid="${entry##*:}"
    if kill -0 "$pid" 2>/dev/null; then
        echo "  $name (pid $pid): ALIVE"
    else
        echo "  $name (pid $pid): DEAD"
    fi
done

echo
echo "--- GPS kept publishing through the failure ---"
tail -3 "$LOGS/gps.log"

kill "$GPS" "$IMU" "$MOTOR" 2>/dev/null
wait 2>/dev/null

echo
echo "###############################################################"
echo "#  C2 — THE SAME FOUR NODES, ONE PROCESS                      #"
echo "###############################################################"

timeout $(( CRASH_AFTER + 8 )) python3 composed_container.py "$CRASH_AFTER" > "$LOGS/composed.log" 2>&1 || true

echo
echo "--- last ticks before the fault (note the single shared pid) ---"
grep -E "tick" "$LOGS/composed.log" | tail -8

echo
echo "--- how it ended ---"
tail -2 "$LOGS/composed.log"

echo
survivors=$(awk '/RuntimeError/{seen=1} seen && /tick/' "$LOGS/composed.log" | wc -l)
echo "--- log lines published by ANY node after the camera failed: $survivors ---"
echo "    (0 means every node died with the process)"

echo
echo "logs: $LOGS"
