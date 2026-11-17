# Day 29 — The agent holds its seat

> **Engineering Question**
>
> **How can an ESP32 become part of a ROS 2 system?**

---

## The story

An ESP32 cannot run full DDS discovery over a USB cable. It has kilobytes of RAM and a serial wire, not multicast sockets and megabytes of participant state.

micro-ROS splits the job across that wire:

- **Client.** A tiny C binary (`esp32_client.c`, compiled with `gcc` and zero ROS or DDS headers) opens a serial port and speaks `0x7E` + CRC-16 binary frames. It asks for one session and three entities: node `esp32_base`, subscriber `/cmd_vel`, publisher `/esp32/status`.
- **Agent.** `agent.py` sits between the serial port and Fast DDS. Nothing on ROS 2 exists until the serial client asks for it. Once asked, the agent holds `esp32_base`'s seat on the ROS 2 graph, packs `geometry_msgs/Twist` down into 26-byte serial frames, and publishes 43-byte status frames back onto `/esp32/status`.
- **Watchdog.** If `/cmd_vel` stops for `250 ms`, the C client cuts both wheels to `0.000` and reports `WATCHDOG_STOP` back up the wire.

No physical ESP32 was plugged into `/dev/ttyUSB0` on this machine. The serial cable is a real POSIX pseudo-terminal pair created by `socat`, and the matching `rclc` / `micro_ros_arduino` sketch for physical silicon lives in `firmware/esp32_base/esp32_base.ino`.

---

## What the runs showed

Domain `225`. Target command `vx = 0.400 m/s`, `wz = 0.400 rad/s`. Wheel separation `0.30 m`, so `left = 0.340 m/s` and `right = 0.460 m/s`. Watchdog timeout `250 ms`.

| Case | What ran | `ros2 node list` | C client wheels | `/esp32/status` |
|---|---|---|---|---|
| **A** no_agent | C client on serial + ROS 2 driver, **no agent** | `/teleop_driver` only | `0.000, 0.000` (`NO_AGENT`) | 0 publishers |
| **B** bridged | C client + serial agent + ROS 2 driver | `/esp32_base`, `/teleop_driver` | `0.340, 0.460` (`DRIVING`) | `state=DRIVING ... left=0.340 right=0.460` |
| **C** watchdog | 5 commands, then `/cmd_vel` stops | `/esp32_base`, `/teleop_driver` | `0.000, 0.000` (peak `0.340, 0.460`) | `state=WATCHDOG_STOP ... left=0.000 right=0.000` |

In A, the C client sent 6 handshake frames into the serial wire (`rx_frames=0`, `session=0`) while `teleop_driver` published 10 `Twist` messages on DDS. `/cmd_vel` had 0 subscribers. Neither side heard the other.

In B, the serial handshake created all 3 entities (`session=1`, `entities=3`, `crc_err=0`). `/esp32_base` appeared on `ros2 node list`, `/cmd_vel` showed 1 publisher and 1 subscriber, and `/esp32/status` echoed `DRIVING` with `left=0.340 right=0.460`.

In C, `teleop_driver` stopped after 5 commands once `DRIVING` was confirmed. After `250 ms` of serial silence, the C client tripped `watchdog_trips=1`, zeroed both wheels, and the driver observed the full state trace `IDLE>DRIVING>WATCHDOG_STOP`.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=225` |
| Wire | `socat` POSIX PTY pair (`115200` raw), `0x7E` + CRC-16 framing |
| Firmware | `firmware/host_sim/esp32_client.c` (host C11) + `firmware/esp32_base/esp32_base.ino` (`rclc` reference) |

```bash
cd day29-micro-ros-esp32
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=225
```

---

## Quick start

Run all three investigations (compiles `esp32_client.c` into `build/esp32_client` and opens the `socat` serial pair):

```bash
cd day29-micro-ros-esp32
./run_smoke.sh
```

On physical ESP32 hardware flashed with `firmware/esp32_base/esp32_base.ino`:

```bash
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | Firmware + ROS 2 driver, no agent | 6 serial pings, 10 `Twist` messages, `/esp32_base` absent |
| **B** | Agent bridges serial and DDS | `/esp32_base` joins graph; wheels `0.340, 0.460`; echo `DRIVING` |
| **C** | `/cmd_vel` goes silent mid-drive | 250 ms watchdog cuts `0.340, 0.460` to `0.000, 0.000` |

Details: `investigations/`.

---

## Key learnings

- A serial cable is not DDS discovery. In A both the C client and the ROS 2 `/cmd_vel` publisher were running, and `/cmd_vel` still had `Subscription count: 0`.
- The agent creates DDS entities on the board's behalf. `esp32_base`, its `/cmd_vel` subscriber, and its `/esp32/status` publisher only appear on `ROS_DOMAIN_ID=225` after `CREATE_NODE`, `CREATE_SUB`, and `CREATE_PUB` cross the wire (`entities=3`).
- Two-way traffic closes the loop. `/cmd_vel` goes down as compact binary frames (26 bytes on the wire); applied wheel speeds and board state come back up onto `/esp32/status` (43 bytes on the wire).
- A bridged motor board needs a local command timeout. If the agent, Wi-Fi, or USB cable drops while the robot is moving, DDS stops delivering `Twist` frames; without the `250 ms` firmware watchdog in C, the wheels would stay at `0.340` and `0.460 m/s`.
- Honest scope: `esp32_client.c` and `agent.py` implement the session/entity/proxy pattern in miniature over a real Linux PTY pair, not the full OMG DDS-XRCE wire specification or physical ESP32 silicon. `firmware/esp32_base/esp32_base.ino` shows the real `rclc` calls used with `micro_ros_agent`.

Day 28 turned a camera pixel into a map goal. Day 29 is how the speed commands from that stack cross a serial wire into a microcontroller and report back.
