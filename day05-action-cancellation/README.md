# Day 05 — Action Cancellation (Warehouse Delivery STOP)

> **Engineering Question**
>
> **How does a robot cancel a task while it is still executing?**
>
> *(Story: What happens when a robot is halfway through a mission and you suddenly tell it: “STOP”?)*

---

## The story

Day 04 showed that Actions (not Topics or long Services) are the right contract for long, interruptible robot work.

Day 05 asks **how STOP is actually coordinated**: CancelGoal is a handshake. Accepting cancel moves the goal to `CANCELING`; the server must still stop work and call `canceled()` before the terminal status is `CANCELED`.

**Real-life example:** a warehouse AMR delivers a package to **Station B** along an aisle (`distance_m`). An operator hits **STOP** mid-route. We observe feedback, cancel response codes, terminal status, and how far the robot traveled.

---

## Objective

Prove that Action cancellation is cooperative and policy-dependent:

1. Full delivery → feedback → `SUCCEEDED`
2. Supervisor STOP with cancel allowed → `CANCELED` + partial distance
3. Same STOP with cancel rejected → delivery still `SUCCEEDED`

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble Hawksbill |
| RMW (pinned) | `rmw_fastrtps_cpp` (Fast DDS) |
| Domain | `ROS_DOMAIN_ID=45` |
| Packages | `day05_delivery_interfaces`, `day05_delivery_bringup` (local `ws/`) |

### Pin middleware (every terminal)

```bash
cd day05-action-cancellation/ros2_nodes
source ./env.sh
ros2 daemon stop
```

### Build once

```bash
./build_ws.sh
source ./env.sh
```

---

## Hypotheses

| ID | Prediction |
|---|---|
| **H1** | With `allow_cancel:=true`, cancel at ~2 s → CancelGoal OK + `goals_canceling` → terminal **`CANCELED (5)`** with traveled &lt; goal. |
| **H2** | With `allow_cancel:=false`, the same STOP is rejected → goal still **`SUCCEEDED (4)`**. |
| **H3** | A completing delivery publishes feedback before the result and ends **`SUCCEEDED`**. |

---

## Investigations

| ID | Title | File |
|---|---|---|
| **A** | Full delivery (no cancel) | [investigations/A-full-delivery-success.md](investigations/A-full-delivery-success.md) |
| **B** | Supervisor STOP mid-route | [investigations/B-supervisor-stop-canceled.md](investigations/B-supervisor-stop-canceled.md) |
| **C** | STOP rejected by server | [investigations/C-reject-cancel-still-succeeds.md](investigations/C-reject-cancel-still-succeeds.md) |

Scripts: `ros2_nodes/run_A.sh`, `run_B.sh`, `run_C.sh`.

---

## Nodes / interfaces

| Piece | Role |
|---|---|
| `DeliverToStation.action` | Goal `distance_m` / Result traveled+remaining / Feedback remaining+% |
| `delivery_server` | Simulates aisle motion; `allow_cancel` parameter |
| `delivery_client` | Operator / mission client; optional timed STOP |

---

## Reproduction (quick start)

```bash
cd day05-action-cancellation/ros2_nodes
source ./env.sh
ros2 daemon stop

# Terminal 1 — cancel-friendly server (A and B)
ros2 run day05_delivery_bringup delivery_server --ros-args -p allow_cancel:=true

# Terminal 2
./run_A.sh    # full delivery
./run_B.sh    # STOP at 2 s

# Restart server for C:
ros2 run day05_delivery_bringup delivery_server --ros-args -p allow_cancel:=false
./run_C.sh
```

---

## Expected results (before runs)

| Run | Progress mid-flight | Cancel request | Terminal status | Distance |
|---|---|---|---|---|
| A | Yes (`remaining` / %) | None | `SUCCEEDED` | traveled ≈ 10 m |
| B | Yes | Accepted (`goals_canceling` &gt; 0) | `CANCELED` | traveled &lt; 10 m |
| C | Yes | Rejected (`goals_canceling` = 0) | `SUCCEEDED` | traveled ≈ 10 m |

---

## Actual results (summary)

Observed 2026-09-18 · Fast DDS · domain 45 · evidence under `assets/*.log`.

| Run | What changed | Key observation |
|---|---|---|
| A | Full 10 m delivery | Feedback → **`SUCCEEDED (4)`** traveled=10.000 |
| B | STOP at 2.0 s, `allow_cancel:=true` | `goals_canceling=1` → **`CANCELED (5)`** traveled=2.200 |
| C | STOP at 2.0 s, `allow_cancel:=false` | `goals_canceling=0` → still **`SUCCEEDED (4)`** traveled=10.000 |

**Hypotheses:** H1 ✓ · H2 ✓ · H3 ✓

---

## Comparison (from evidence)

| Dimension | A (complete) | B (STOP allowed) | C (STOP rejected) |
|---|---|---|---|
| Feedback mid-flight? | Yes | Yes | Yes |
| Cancel accepted? | n/a | Yes (`goals_canceling=1`) | No (`goals_canceling=0`) |
| Terminal status | `SUCCEEDED` | `CANCELED` | `SUCCEEDED` |
| Distance at end | 10.0 m | 2.2 m | 10.0 m |

---

## Engineering takeaway

**STOP is not killing a node.** It is CancelGoal → (optional) `CANCELING` → server cleanup → `CANCELED` + result. If the server rejects cancel, the mission keeps going.

Same contract Nav2 uses when you cancel `NavigateToPose` mid-route.

---

## Out of scope (Day 05)

- Ignore-cancel stuck in `CANCELING`
- Client disconnect without CancelGoal
- Preemption / `ABORTED` via a new goal

---

## Interview prep

See [interview_questions.md](interview_questions.md).

## References

See [references.md](references.md).
