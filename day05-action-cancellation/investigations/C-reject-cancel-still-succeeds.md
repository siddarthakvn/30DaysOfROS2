# Investigation C — STOP rejected; delivery still succeeds

## Hypothesis (H2)

With `allow_cancel:=false`, the same supervisor STOP is rejected. The goal stays executing and still finishes `SUCCEEDED (4)` — cancel is policy, not magic.

## Setup

- `delivery_server` with `allow_cancel:=false`
- `delivery_client` with `distance_m:=10.0`, `cancel_after_sec:=2.0`
- Domain 45 · Fast DDS · observed 2026-09-18

## Procedure

```bash
cd day05-action-cancellation/ros2_nodes
source ./env.sh

# Terminal 1 (restart server — reject cancel)
ros2 run day05_delivery_bringup delivery_server --ros-args -p allow_cancel:=false

# Terminal 2
./run_C.sh
```

## Expected

- Cancel response shows rejection (no goals enter `CANCELING`)
- Terminal status still `SUCCEEDED (4)`
- `traveled ≈ 10.0 m`

## Actual

| Observation | Evidence |
|---|---|
| Goal accepted; feedback continues past the STOP attempt | `assets/C_reject_cancel.log` |
| At ~2.0 s: cancel requested | same |
| **`Cancel response: return_code=0 goals_canceling=0`** | same |
| Feedback continues to 100%; **`Terminal status=SUCCEEDED (4) traveled=10.000`** | same |
| Server: `Operator STOP rejected — allow_cancel=false; delivery continues` then `SUCCEEDED` | `assets/C_server_session.log` |

Note on `return_code`: with rclpy, a user `CancelResponse.REJECT` removes the goal from `goals_canceling` after the low-level cancel processing. Observed signal of rejection is **`goals_canceling=0`** plus continued execution — not a terminal `CANCELED`. Server log confirms the reject policy fired.

## Analysis

H2 holds. Issuing CancelGoal is not enough. The action server’s cancel policy decides whether the robot is allowed to stop. When rejected, the warehouse delivery still arrives at Station B (`SUCCEEDED`).
