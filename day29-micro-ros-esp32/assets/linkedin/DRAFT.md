# LinkedIn draft — Day 29

**Question:** How can an ESP32 become part of a ROS 2 system?

**Hero:** `assets/linkedin/01-hero.jpg`

Numbers below are from `./run_smoke.sh` on this machine (`ROS_DOMAIN_ID=225`). No physical ESP32 was plugged in; a standalone C client (`esp32_client.c`, zero ROS headers) spoke `0x7E` + CRC-16 frames over a `socat` serial pair to the host agent, alongside the reference `rclc` sketch in `firmware/esp32_base/esp32_base.ino`.

---

The ESP32 is running. ROS 2 still cannot see it.

That is Day 29 of #30DaysOfROS2.

How can an ESP32 become part of a ROS 2 system?

Full DDS discovery fits a Linux computer, not kilobytes of microcontroller RAM on the far end of a serial cable. micro-ROS splits the job. A tiny client runs on the board, and an agent on the Linux host holds its seat in the ROS 2 graph.

Three runs over a serial link on Domain 225, sending vx = 0.400 m/s and wz = 0.400 rad/s to a 0.30 m base:

No agent. The C client sent 6 session pings onto the wire. The ROS 2 driver published 10 /cmd_vel messages. /esp32_base never appeared in ros2 node list, /cmd_vel had 0 subscribers, and wheel speeds stayed 0.000, 0.000.

Agent running. The client requested its node, /cmd_vel subscriber, and /esp32/status publisher over serial (3 entities, 0 CRC errors). /esp32_base joined the ROS 2 graph, wheel speeds hit 0.340 and 0.460 m/s, and /esp32/status echoed state=DRIVING back onto DDS.

Commands stop after 5 messages. After 250 ms of serial silence, the firmware watchdog cut both wheels from 0.340 and 0.460 to 0.000 and echoed state=WATCHDOG_STOP back up to the host.

The agent gives the chip a seat on the graph. The watchdog keeps a dropped cable from becoming a runaway robot.

Day 29 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day29-micro-ros-esp32

#ROS2 #microROS #ESP32 #EmbeddedSystems #Robotics
