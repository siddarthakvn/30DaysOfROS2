# Investigation A — Full delivery (Station B)

## Hypothesis (H3)

A warehouse delivery Action publishes feedback while executing and ends with terminal status `SUCCEEDED` when no cancel is requested.

## Setup

- `delivery_server` with `allow_cancel:=true` (cancel policy unused)
- `delivery_client` with `distance_m:=10.0`, `cancel_after_sec:=-1.0`
- Domain 45 · Fast DDS · observed 2026-09-18

## Procedure

```bash
cd day05-action-cancellation/ros2_nodes
source ./env.sh

# Terminal 1
ros2 run day05_delivery_bringup delivery_server --ros-args -p allow_cancel:=true

# Terminal 2
./run_A.sh
```

## Expected

- Goal accepted with UUID
- Feedback stream: `remaining` decreases, `percent` increases
- Terminal status `SUCCEEDED (4)`
- `traveled ≈ 10.0 m`, `remaining ≈ 0.0 m`

## Actual

| Observation | Evidence |
|---|---|
| Goal accepted `id=d7afce141ff94b0ba15bf60d61258549` | `assets/A_full_delivery.log` |
| Feedback 1→50: remaining 9.8→0.0 m, percent 2%→100% | same |
| **`Terminal status=SUCCEEDED (4) traveled=10.000 remaining=0.000 feedback=51`** | same |
| Server: `SUCCEEDED delivery: traveled=10.00 m — arrived Station B` | `assets/AB_server_session.log` |

## Analysis

H3 holds. The delivery Action behaves like a long committed mission: continuous progress feedback, then a correlated terminal result. No cancel path was exercised here — that is Investigation B/C.
