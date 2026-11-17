# Evidence — Day 29

| File | What |
|---|---|
| `A_no_agent.log` | C client sends 6 serial pings; `/esp32_base` absent; `/cmd_vel` has 0 subscribers |
| `B_bridged.log` | Agent creates `/esp32_base`; wheels `0.340, 0.460`; `/esp32/status` echoes `DRIVING` |
| `C_watchdog.log` | `/cmd_vel` stops after 5 commands; 250 ms watchdog cuts wheels to `0.000, 0.000` |
| `linkedin/01-hero.jpg` | ESP32 client, `micro_ros_agent`, `/cmd_vel` + `status`, ROS 2 graph |
| `linkedin/DRAFT.md` | Post draft |
