# Day 26 — Seen, then confirmed, then stay

> **Engineering Question**
>
> **How should a rescue robot transition from SEARCHING to VERIFYING to LOCKDOWN?**

---

## The story

A shape in a doorway is not a rescue. The coordinator has three states and three arrows.

- **Seen.** SEARCHING becomes VERIFYING. The search stops. Lockdown does not start.
- **Missed.** The second look fails. VERIFYING returns to SEARCHING. A confirm with no second look is refused.
- **Held.** The second look holds. VERIFYING becomes LOCKDOWN. After that, a new glimpse, a miss, and a finished navigation goal are all refused.

Nav2 is allowed to move the robot only while the state is SEARCHING. VERIFYING is a check. LOCKDOWN is a hold. The coordinator is the one that says which of those is legal.

The events are the inputs. What is measured is which transitions are accepted.

---

## What the runs showed

The edge list is fixed: SEEN, HELD, MISSED. Three arrows.

| Case | Events | Trace | Refused | `/mission_state` |
|---|---|---|---|---|
| **A** missed | SEEN, MISSED, HELD | SEARCHING > VERIFYING > SEARCHING | **1** (HELD from SEARCHING) | `SEARCHING`, navigate allowed |
| **B** held | SEEN, HELD | SEARCHING > VERIFYING > LOCKDOWN | **0** | `LOCKDOWN`, navigate refused |
| **C** stay | SEEN, HELD, then SEEN, MISSED, GOAL_DONE | SEARCHING > VERIFYING > LOCKDOWN | **3** | `LOCKDOWN`, navigate refused |

A never enters LOCKDOWN. B and C enter it by the only legal path. C cannot leave.

`/mission_state` is a latched `std_msgs/String`. The node is `coordinator`. The echo matches the final state in each log.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=228` |

```bash
cd day26-mission-fsm
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=228
```

---

## Quick start

```bash
cd day26-mission-fsm
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=228

python3 ros2_nodes/coordinator.py --ros-args -p mode:=held
```

`mode` is `missed`, `held`, or `stay`.

All three:

```bash
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | A miss, then a shortcut confirm | Back to SEARCHING. HELD is refused |
| **B** | Seen, then held | LOCKDOWN. Navigate is no longer allowed |
| **C** | Three events after lockdown | The state does not move. 3 refused |

Details: `investigations/`.

---

## Key learnings

- The legal list is three arrows. SEEN leaves SEARCHING for VERIFYING. HELD leaves VERIFYING for LOCKDOWN. MISSED leaves VERIFYING for SEARCHING.
- HELD from SEARCHING is refused. A single glimpse cannot skip the second look. In A that was the one rejected event, and LOCKDOWN was never entered.
- LOCKDOWN has no outgoing edge. In C, SEEN, MISSED, and GOAL_DONE were all refused. A finished navigation goal is not a reason to search again.
- `navigate_allowed` is 1 only in SEARCHING. The coordinator calls Nav2. Nav2 does not choose the mission state.
- Day 25 used a tree for plan, follow, and recover, because those are a checklist. This mission is a short list of legal steps, so a small state machine is the coordinator.

Day 25 ticked a navigation checklist. Day 26 decides which mission that checklist is serving.
