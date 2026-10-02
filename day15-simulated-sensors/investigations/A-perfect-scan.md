# Investigation A — A still sensor with no noise

## Question

If the robot and the wall do not move, and the lidar has no noise, do two scans match?

## Setup

`worlds/wall_perfect.sdf`

- Sensor at the origin, wall face at 1.90 m
- 32 beams, update rate 5 Hz
- No `<noise>` block

## Procedure

```bash
cd day15-simulated-sensors
source ros2_nodes/env.sh
gz sim -s -r --headless-rendering worlds/wall_perfect.sdf
```

Before the bridge:

```bash
gz topic -l | grep lidar
ros2 topic list | grep lidar
```

Then:

```bash
ros2 run ros_gz_bridge parameter_bridge \
  /lidar@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan
python3 ros2_nodes/measure_scan.py --ros-args -p listen_sec:=3.0
```

## Expected

Gazebo publishes `/lidar`. ROS does not, until the bridge. Consecutive ranges match.

## Actual

From `./run_smoke.sh` on this machine.

Before the bridge (`assets/A_perfect_before_bridge.txt`):

- Gazebo topics include `/lidar`
- ROS has no `/lidar`

After the bridge (`assets/A_perfect.log`):

```text
SUMMARY scans=15 hz=4.96 max_abs_diff_m=0.000000 center_mean_m=1.9006
```

The center beam matches the wall face (1.90 m). Nothing in the scan changed from one message to the next.

## Conclusion

A perfect simulated lidar repeats itself. The bridge is a separate gate: the scan can exist in Gazebo and still be invisible to ROS.
