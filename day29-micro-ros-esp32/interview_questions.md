# Day 29 — Interview questions

1. Why doesn't a bare-metal or FreeRTOS ESP32 simply run Fast DDS peer-to-peer discovery like a Raspberry Pi or laptop?

2. When `ros2 node list` shows `/esp32_base`, which process actually holds the DDS participant on the network, and when are its topics created?

3. In Investigation A, both the firmware process and the `/cmd_vel` publisher were running. Why did `ros2 topic info /cmd_vel` report `Subscription count: 0`?

4. Why must a motor base publish feedback or status back up to ROS 2 instead of treating `/cmd_vel` as fire-and-forget?

5. What happens if `micro_ros_agent` crashes or the USB/Wi-Fi link drops while the robot is driving at `0.40 m/s`, and why must the watchdog timer live on the ESP32 rather than on the Linux host?

6. In `firmware/esp32_base/esp32_base.ino`, what role does `rmw_uros_ping_agent()` play before `rclc_node_init_default()` runs?
