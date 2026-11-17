# C — Command silence trips the embedded watchdog

## Hypothesis

If `/cmd_vel` stops arriving while the base is `DRIVING`, the C client's `250 ms` watchdog zeroes both wheels and reports `WATCHDOG_STOP` back through the agent onto `/esp32/status`.

## Method

Same serial pair and agent as B, with `mode:=watchdog`. `driver.py` sends `/cmd_vel` (`vx = 0.400`, `wz = 0.400`) until `DRIVING` is confirmed and 5 commands have been sent, then stops publishing while keeping its status subscription open.

## Result

```text
SUMMARY node=esp32_client mode=watchdog session=1 entities=3 cmd_rx=5 state=WATCHDOG_STOP vx=0.000 wz=0.000 left=0.000 right=0.000 peak_left=0.340 peak_right=0.460 watchdog_trips=1 tx_frames=11 rx_frames=9 crc_err=0
SUMMARY node=agent mode=watchdog session=1 ros_node=esp32_base sub=/cmd_vel pub=/esp32/status cmd_forwarded=5 status_forwarded=7 last_state=WATCHDOG_STOP crc_err=0
SUMMARY node=driver mode=watchdog cmd_tx=5 status_rx=7 trace=IDLE>DRIVING>WATCHDOG_STOP last_state=WATCHDOG_STOP
```

`ros2 topic echo --once /esp32/status`:

```text
data: state=WATCHDOG_STOP cmd_rx=5 vx=0.000 wz=0.000 left=0.000 right=0.000
```

## Conclusion

Peak wheel speeds reached `0.340` and `0.460 m/s` during the 5-command burst, then dropped to `0.000` once `250 ms` passed without a new serial frame. Safety stop lives on the microcontroller side of the wire, and the status topic lets the ROS 2 host confirm that stop happened.
