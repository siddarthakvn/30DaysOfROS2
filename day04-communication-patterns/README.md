# Day 04 — Topics, Services, and Actions

> **Engineering Question**
>
> **When should a robot use a Topic, Service, or Action?**

---

## The story

Days 01–03 built the graph, modular nodes, and topic overload. Day 04 asks the next design question: **streaming is not always the right contract.**

On a real robot you choose a **commitment model**:

| Pattern | Commitment |
|---|---|
| **Topic** | “Here is the latest stream. I do not wait for you.” |
| **Service** | “Do this small thing and answer once.” |
| **Action** | “Achieve this goal over time. Report progress. I may cancel.” |

This day uses **turtlesim** (not Gazebo — that is Day 14) so the comparison stays on communication semantics, not simulator setup.

---

## Objective

Run the **same motion idea** (rotate the turtle for a few seconds) under three contracts, then interrupt mid-motion and compare:

1. Progress visible mid-flight?
2. Clean cancel mid-flight?
3. Correlated final result?
4. Introspection (`ros2 topic` / `service` / `action`)?

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble Hawksbill |
| RMW (pinned) | `rmw_fastrtps_cpp` (Fast DDS) |
| Domain | `ROS_DOMAIN_ID=40` |
| Sim | `turtlesim` (`ros-humble-turtlesim`) |

### Pin middleware (every terminal)

```bash
cd day04-communication-patterns/ros2_nodes
source ./env.sh
ros2 daemon stop
ros2 doctor --report | grep -i rmw
# expect: rmw_fastrtps_cpp
```

---

## Hypotheses

| ID | Prediction |
|---|---|
| **H1** | A long Service has no clean mid-flight cancel; an Action exposes cancel → `CANCELED`. |
| **H2** | An Action yields intermediate feedback before the result; a Service yields only one terminal response. |
| **H3** | Stopping a Topic `cmd_vel` publisher is not a server-acked cancel / goal lifecycle. |

---

## Investigations

| ID | Title | File |
|---|---|---|
| **A** | Topic stream motion | [investigations/A-topic-stream-motion.md](investigations/A-topic-stream-motion.md) |
| **B** | Long Service (anti-pattern) | [investigations/B-long-service-no-cancel.md](investigations/B-long-service-no-cancel.md) |
| **C** | Action feedback + cancel | [investigations/C-action-feedback-cancel.md](investigations/C-action-feedback-cancel.md) |

Quick command sheets: `ros2_nodes/run_A.sh`, `run_B.sh`, `run_C.sh`.

---

## Nodes / interfaces

| Piece | Role |
|---|---|
| `turtlesim_node` | Simulated turtle; `/turtle1/cmd_vel`, services, `/turtle1/rotate_absolute` action |
| `cmd_vel_burst.py` | Investigation A — Topic velocity burst |
| `long_rotate_server.py` | Investigation B — blocking `std_srvs/Trigger` rotate (anti-pattern) |
| `long_rotate_client.py` | Investigation B — blocking service client |
| `action_cancel_demo.py` | Investigation C1 — Action goal + timed cancel |

---

## Reproduction (quick start)

```bash
cd day04-communication-patterns/ros2_nodes
source ./env.sh
ros2 daemon stop

# Terminal 1 (all investigations)
ros2 run turtlesim turtlesim_node

# Then follow ./run_A.sh / ./run_B.sh / ./run_C.sh
```

---

## Expected results (before runs)

| Pattern | Progress mid-flight | Clean cancel | Final result | Interrupt failure mode |
|---|---|---|---|---|
| Topic (A) | Only by watching pose / your own pubs | No protocol | No correlated goal result | Stop publisher ≠ cancel ack |
| Service (B) | No client feedback | No cancel API | One response at end | Client Ctrl+C may leave server working |
| Action (C) | Yes (`remaining`) | Yes | Terminal status + result | Cancel → `CANCELED` |

---

## Actual results (summary)

Observed 2026-09-16 · Fast DDS · domain 40 · evidence under `assets/*.log`.

| Run | What changed | Key observation |
|---|---|---|
| A0 | Topic burst 5 s + zero on exit | 99 pubs; pose stopped with `angular_velocity=0` |
| A1 | Stop publisher at 2 s, **no** zero | Warn log; no Action goal for this motion; `angular_velocity` later 0 without cancel status |
| B0 | Long service to completion | Client waits ~5 s for **one** response; server `SPIN` logs only on server |
| B1 | SIGINT client mid-call | Client dies; server still finishes full 5 s (`SERVICE DONE … published=99`) |
| C0 | Action to π | Feedback `remaining` stream; **`SUCCEEDED`**; `delta≈-3.14` |
| C1 | Cancel after 1.0 s | Feedback then cancel; **`CANCELED`**; pose stopped at `theta≈1.02` (not π) |

---

## Comparison table (from evidence)

| Dimension | Topic (A) | Service (B) | Action (C) |
|---|---|---|---|
| Progress visible? | Indirect (pose / pub logs) | **No** (client) | **Yes** (`remaining`) |
| Clean cancel? | **No** | **No** (client kill ≠ cancel) | **Yes** (`CANCELED`) |
| Correlated result? | **No** goal result | One `Trigger` response | Status + `delta` |
| CLI family | `ros2 topic` | `ros2 service` | `ros2 action` |

**Hypotheses:** H1 ✓ · H2 ✓ · H3 ✓

---

## Engineering takeaway

**Stream with Topics. Ask quick questions with Services. Commit the robot to a behavior with Actions.**

Same turtlesim rotation, three contracts:

- Topic interrupt = stop publishing (no goal lifecycle).
- Service interrupt = client can leave while the server keeps working.
- Action interrupt = explicit cancel with terminal `CANCELED` and partial result.

Official Humble rule: services should **never** be used for longer-running processes that may need preemption — use an action.

---

## Interview prep

See [interview_questions.md](interview_questions.md).

## References

See [references.md](references.md).
