# References — Day 03

Official and primary sources for **Day 03 – Topics, Queues, and Backpressure** (Humble-first).

---

## Official ROS 2 documentation

| Topic | URL |
|---|---|
| Topics | https://docs.ros.org/en/humble/Concepts/Basic/About-Topics.html |
| Quality of Service settings | https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html |
| Different middleware vendors (RMW) | https://docs.ros.org/en/humble/Concepts/Intermediate/About-Different-Middleware-Vendors.html |
| ROS 2 docs hub | https://docs.ros.org/en/humble/ |

---

## Design / API primary sources

| Topic | URL / location |
|---|---|
| ROS 2 QoS design article | https://design.ros2.org/articles/qos.html |
| `rmw` history policy (`KEEP_LAST` drops oldest) | `/opt/ros/humble/include/rmw/rmw/types.h` (`RMW_QOS_POLICY_HISTORY_KEEP_LAST`) |
| Default / sensor QoS profiles | `/opt/ros/humble/include/rmw/rmw/qos_profiles.h` |
| rclpy QoS presets | `rclpy.qos` (`qos_profile_sensor_data`, etc.) |

---

## Commands used

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
ros2 daemon stop
ros2 doctor --report | grep -i rmw

python3 frame_camera_pub.py --ros-args -p publish_hz:=30.0 -p depth:=10 -p reliability:=reliable
python3 slow_inference_sub.py --ros-args -p process_ms:=100 -p depth:=10 -p reliability:=reliable

ros2 topic info /perception/frames -v
ros2 topic hz /perception/frames
ros2 topic bw /perception/frames
```

---

## Notes

- Deep QoS (deadline, lifespan, liveliness, durability matrix) is reserved for **Day 07**.
- This machine may default to Cyclone DDS; Day 03 **pins Fast DDS** for series consistency with Day 01.
