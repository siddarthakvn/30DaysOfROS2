# A — Firmware running, no agent

## Hypothesis

When the C client transmits session requests over serial and `teleop_driver` publishes `/cmd_vel` on ROS 2 without an agent between them, `/esp32_base` never appears on the ROS 2 graph and zero commands reach the client.

## Method

`socat` opens a raw PTY pair (`esp32_uart` ↔ `agent_uart`). `esp32_client` runs on `esp32_uart` for `1500 ms`, sending `CREATE_CLIENT` frames every `250 ms`. `driver.py` runs on `ROS_DOMAIN_ID=225` with `mode:=no_agent`, publishing `Twist(linear.x=0.40, angular.z=0.40)` on `/cmd_vel`. No agent opens `agent_uart`.

## Result

```text
SUMMARY node=esp32_client mode=no_agent session=0 entities=0 cmd_rx=0 state=NO_AGENT vx=0.000 wz=0.000 left=0.000 right=0.000 peak_left=0.000 peak_right=0.000 watchdog_trips=0 tx_frames=6 rx_frames=0 crc_err=0
SUMMARY node=driver mode=no_agent cmd_tx=10 status_rx=0 trace=NONE last_state=NONE
```

`ros2 node list` showed only `/teleop_driver`. `ros2 topic info /cmd_vel -v` reported `Publisher count: 1` and `Subscription count: 0`. `ros2 topic info /esp32/status -v` reported `Publisher count: 0` and `Subscription count: 1`.

## Conclusion

The C client was alive and sent 6 frames onto the wire. The ROS 2 driver was alive and published 10 velocity commands. Without the agent holding a DDS participant for the serial client, the board does not exist in ROS 2.
