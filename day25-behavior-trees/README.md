# Day 25 — A checklist, ticked from the top

> **Engineering Question**
>
> **Why does Nav2 use Behavior Trees instead of one giant state machine?**

---

## The story

The job is the one from Day 24. Plan. Follow. If follow fails, recover, and read the list again.

The first follow fails. Back up succeeds. The second follow succeeds. Those leaf results are the input. What changes between the runs is the control structure around them.

- **Knot.** The five boxes in the picture. An arrow each way between every pair.
- **Machine.** The job written as states and edges. A successful recovery has its own arrow back to plan.
- **Tree.** The same leaves under one recovery node. The node ticks plan-then-follow, and on failure it ticks the recovery fallback, then ticks plan-then-follow again.

The Humble tree this copies in miniature is `navigate_to_pose_w_replanning_and_recovery.xml`: a `RecoveryNode` whose second child is a fallback of clear, spin, wait, and back up. This day keeps plan, follow, and back up, then measures what happens when spin and wait are added too.

---

## What the runs showed

| Case | Structure | The job | Adding spin and wait |
|---|---|---|---|
| **A** knot | **5** states, **20** arrows | no policy. Every box points at every other box | |
| **B** machine | **5** states, **6** arrows | `plan>follow>back_up>plan>follow`, succeeded | **10** arrows. **4** new |
| **C** tree | **6** nodes, **5** links | the same trace, succeeded | **7** links. **2** new |

Two extra recoveries add four arrows to the state machine, because each one needs a failure link and its own arrow back to plan. The same two recoveries add two links to the tree, one child each. The retry rule stays inside the recovery node.

`/behavior_tree_log` is a latched `nav2_msgs/BehaviorTreeLog`. The node is `checklist`.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=229` |

```bash
cd day25-behavior-trees
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=229
```

---

## Quick start

```bash
cd day25-behavior-trees
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=229

python3 ros2_nodes/tick.py --ros-args -p mode:=tree
```

`mode` is `knot`, `machine`, or `tree`.

All three:

```bash
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | The picture, counted | 5 states, 20 arrows |
| **B** | The state machine does the job | 6 arrows, and 4 more when two recoveries are added |
| **C** | The tree does the same job | 5 links, and 2 more for the same two recoveries |

Details: `investigations/`.

---

## Key learnings

- The knot in the picture is a complete digraph. Five behaviors produce 20 directed arrows, and there is still no rule for which arrow to take.
- A state machine can express this job in 6 arrows. The retry is copied: back up's success edge is hard-wired to plan.
- A recovery node expresses the retry once. It ticks the sequence, and on failure it ticks the fallback, then the sequence again. The trace matches the state machine: `plan>follow>back_up>plan>follow`.
- Adding spin and wait costs the state machine 4 arrows and the tree 2 links. One new recovery is a new child, not a new arrow out of every state.
- Nav2 stores that checklist as XML and ticks it from `bt_navigator`. The planner still draws the line. The controller still sends the speed. The tree decides which of those runs next.

Day 24 recovered from a wide box by replanning once. Day 25 is the checklist that makes that second try a line in a list.
