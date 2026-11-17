# B — The agent bridges `/cmd_vel` down and status up

## Hypothesis

Starting the serial agent allows the C client to create `/esp32_base`, receive `/cmd_vel`, compute left/right wheel speeds, and publish `DRIVING` back onto `/esp32/status`.

## Method

`agent.py` opens `agent_uart` on `ROS_DOMAIN_ID=225`. `esp32_client` opens `esp32_uart` with `--mode bridged`. `driver.py` runs with `mode:=bridged`, streaming `vx = 0.400 m/s`, `wz = 0.400 rad/s` at 20 Hz.

## Result

```text
SUMMARY node=esp32_client mode=bridged session=1 entities=3 cmd_rx=5 state=DRIVING vx=0.400 wz=0.400 left=0.340 right=0.460 peak_left=0.340 peak_right=0.460 watchdog_trips=0 tx_frames=10 rx_frames=9 crc_err=0
SUMMARY node=agent mode=bridged session=1 ros_node=esp32_base sub=/cmd_vel pub=/esp32/status cmd_forwarded=5 status_forwarded=6 last_state=DRIVING crc_err=0
SUMMARY node=driver mode=bridged cmd_tx=5 status_rx=5 trace=IDLE>DRIVING last_state=DRIVING
```

`ros2 node list`:

```text
/esp32_base
/teleop_driver
```

`/cmd_vel` showed `Publisher count: 1` (`teleop_driver`) and `Subscription count: 1` (`esp32_base`).

`ros2 topic echo --once /esp32/status`:

```text
data: state=DRIVING cmd_rx=31 vx=0.400 wz=0.400 left=0.340 right=0.460
```

## Conclusion

The C binary linked zero ROS libraries, yet `/esp32_base` appeared as a native ROS 2 node because the agent created the node, subscriber, and publisher on DDS after the serial handshake (`entities=3`, `crc_err=0`) and forwarded traffic both ways.
