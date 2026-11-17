# Day 29 — References

## Primary

1. **micro-ROS architecture & tutorials**  
   https://micro.ros.org/docs/overview/core_concepts/  
   Explains why microcontrollers run `rclc` on top of Micro XRCE-DDS as a client, while `micro_ros_agent` bridges those entities into the standard ROS 2 DDS dataspace.

2. **eProsima Micro XRCE-DDS**  
   https://micro-xrce-dds.docs.eprosima.com/en/latest/  
   OMG DDS-XRCE wire protocol (`CREATE_CLIENT`, `CREATE` entity requests, `WRITE_DATA` / `READ_DATA` streams, and `0x7E` HDLC serial framing with CRC-16). `esp32_client.c` and `wire.py` model this session/entity/data split in miniature.

3. **micro_ros_arduino (ESP32 support)**  
   https://github.com/micro-ROS/micro_ros_arduino  
   Provides `set_microros_transports()`, `rmw_uros_ping_agent()`, and `rclc` headers used in `firmware/esp32_base/esp32_base.ino`.

4. **geometry_msgs/Twist & std_msgs/String**  
   http://docs.ros.org/en/humble/p/geometry_msgs/msg/Twist.html  
   http://docs.ros.org/en/humble/p/std_msgs/msg/String.html  
   `/cmd_vel` carries `(linear.x, angular.z)` down to the base; `/esp32/status` carries the latched board state and wheel speeds back up.

## This machine

- Ubuntu 22.04 LTS, ROS 2 Humble (`rmw_fastrtps_cpp`)
- `ROS_DOMAIN_ID=225`
- `gcc` (Ubuntu 11.4, `-std=c11`) + `socat` POSIX PTY serial pair (`115200` raw)
- No physical ESP32 attached; `esp32_client.c` runs as a standalone C process over PTY

## Related days

- Day 01 — Peer-to-peer DDS discovery on Linux (what does not fit on an MCU)
- Day 07 — QoS durability and depth (`TRANSIENT_LOCAL` depth 1 on `/esp32/status`)
- Day 14 & Day 16 — `/cmd_vel` `Twist` and differential-drive wheel velocity kinematics (`v_l = v - ωL/2`, `v_r = v + ωL/2`)
