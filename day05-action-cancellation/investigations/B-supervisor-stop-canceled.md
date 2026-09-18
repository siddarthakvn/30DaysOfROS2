# Investigation B — Supervisor STOP mid-route

## Hypothesis (H1)

With `allow_cancel:=true`, a CancelGoal at ~2 s is accepted (`return_code=0`, non-empty `goals_canceling`), the goal enters cleanup, and the terminal status is `CANCELED (5)` with partial distance traveled.

## Setup

- `delivery_server` with `allow_cancel:=true`
- `delivery_client` with `distance_m:=10.0`, `cancel_after_sec:=2.0`
- Domain 45 · Fast DDS · observed 2026-09-18

## Procedure

```bash
cd day05-action-cancellation/ros2_nodes
source ./env.sh

# Terminal 1
ros2 run day05_delivery_bringup delivery_server --ros-args -p allow_cancel:=true

# Terminal 2
./run_B.sh
```

## Expected

- Feedback before cancel
- Cancel response: `return_code=0`, `goals_canceling=1`
- Terminal status `CANCELED (5)`
- `traveled < 10 m` and `remaining > 0`

## Actual

| Observation | Evidence |
|---|---|
| Goal accepted; feedback through ~20% | `assets/B_supervisor_stop.log` |
| At ~2.0 s: `Requesting CANCEL now` | same |
| **`Cancel response: return_code=0 goals_canceling=1`** | same |
| **`Terminal status=CANCELED (5) traveled=2.200 remaining=7.800 feedback=11`** | same |
| Server: `Operator STOP accepted` then `CANCELED after 2.20 m` | `assets/AB_server_session.log` |

## Analysis

H1 holds. Supervisor STOP is a real CancelGoal handshake: accept → server cleanup → terminal `CANCELED` with a partial result (2.2 m of 10 m). That is the warehouse “STOP the AMR mid-aisle” contract — not killing the client process.
