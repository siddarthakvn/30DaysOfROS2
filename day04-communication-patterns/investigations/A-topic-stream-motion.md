# Investigation A — Topic stream motion

## Hypothesis (H3)

Stopping a Topic publisher mid-motion is **not** the same as an Action cancel: there is no goal ID, no `CANCELING` / `CANCELED` handshake, and no standard result.

## Setup

- `turtlesim_node`
- `cmd_vel_burst.py` → `/turtle1/cmd_vel`
- Domain 40, `rmw_fastrtps_cpp`

## Procedure

See `ros2_nodes/run_A.sh`.

### A0 — Full burst with zero on exit

```bash
source ./env.sh
python3 cmd_vel_burst.py --ros-args \
  -p duration_sec:=5.0 -p angular_z:=1.0 -p send_zero_on_exit:=true
```

### A1 — Stop publishing early (no zero)

```bash
python3 cmd_vel_burst.py --ros-args \
  -p duration_sec:=5.0 -p stop_after_sec:=2.0 -p angular_z:=1.0 \
  -p send_zero_on_exit:=false
```

## Expected

- Motion while Twist messages arrive
- After A1 exit: log warns that exit is without zero Twist
- No `ros2 action` lifecycle for this motion
- Turtle behavior after last message: **observe** (may coast or hold last cmd — record honestly)

## Actual

Observed 2026-09-16 · Fast DDS · domain 40 · logs under `assets/`.

| Run | Observation | Evidence |
|---|---|---|
| A0 | Published 99 Twists over 5.0 s; zero Twist on exit; pose `theta≈-1.32`, `angular_velocity=0` | `assets/A0_topic_full_burst.log` |
| A1 | Stopped after 2.0 s / 39 pubs **without** zero Twist; immediate pose `theta≈2.91`, `angular_velocity=1.0`; +1.5 s later same `theta`, `angular_velocity=0.0`. Motion path is **not** listed as an action goal — only `/turtle1/rotate_absolute` exists on `ros2 action list`. | `assets/A1_topic_stop_publisher.log` |

## Analysis

H3 holds: interrupting Topic motion means **ceasing publications**. There is no goal UUID, no cancel ack, and no terminal Action status. In this turtlesim run, velocity eventually read back as 0 without an explicit zero publish from our node — that is simulator/controller behavior, **not** a cancel protocol. Compare with Investigation C’s explicit `CANCELED`.
