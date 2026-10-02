# Day 15 — References

## Primary

1. **Sensors — Gazebo Harmonic**  
   https://gazebosim.org/docs/harmonic/sensors/  
   `update_rate` is how often a sensor message is generated. The tutorial lidar has no noise block.

2. **SDFormat 1.12 sensor**  
   https://sdformat.org/spec/1.12/sensor/  
   Gaussian noise mean and stddev default to 0. A noise model with stddev 0 is still an exact range.

3. **gz-sensors lidar**  
   The installed Harmonic library (`libgz-sensors8-lidar`) applies noise only when a Gaussian noise model is loaded. This day's noisy world sets `stddev` to 0.05 m.

4. **ros_gz_bridge**  
   https://github.com/gazebosim/ros_gz/blob/ros2/ros_gz_bridge/README.md  
   `[` means Gazebo to ROS. This machine uses Harmonic types: `gz.msgs.LaserScan` to `sensor_msgs/msg/LaserScan`.

## This machine

- `gz sim` 8.14.0
- `ros-humble-ros-gzharmonic-bridge`
- Server flag used: `gz sim -s -r --headless-rendering`

## Related days

- Day 14 — a command crosses into Gazebo on the same bridge
- Day 03 — a fast scan and a slow callback are a different problem from an exact scan
