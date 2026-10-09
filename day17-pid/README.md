# Day 17 — Why the heading oscillates

> **Engineering Question**
>
> **Why does my robot oscillate around the target angle?**

---

## The story

The robot is not missing the angle. It is still turning when it gets there.

P only looks at the gap. Far away, the command is strong, so a heading with inertia builds turn speed. At the target the gap is zero, so P contributes nothing to stop that speed. The nose crosses. The gap flips. P turns the other way.

D looks at the turn rate and takes the command away before the crossing.

---

## What the runs showed

Target is 90°. Start is 0°. Same P gain, 4.0, for 8 seconds. The only changes are the brake and the plant.

| Case | Plant | D | What happened |
|---|---|---|---|
| **A** | Turn rate is remembered | 0 | Crossed the target **5** times. Went **90°** past it. Ended at 175.9°, not on 90°. |
| **B** | Same plant | 4 | **0** crossings. Ended on **90.00°**. |
| **C** | Turn rate equals the command immediately | 0 | **0** crossings. Ended on **90.00°**. |

Same P. The wobble showed up only when the heading could keep turning after the command went to zero.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=170` |

```bash
cd day17-pid
source ros2_nodes/env.sh
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | P only, heading remembers turn rate | Five crossings, 90° past the target |
| **B** | Same P, plus D | Stops on 90° |
| **C** | Same P, no stored turn rate | Also stops on 90°. The plant was the difference |

Details: `investigations/`.

---

## Key learnings

- P is the gap. At the target it is zero, so it does not brake a turn you already have.
- D is what opposes that turn rate.
- Raising P without D is how this heading keeps swinging.
- If the turn rate is forced to match the command instantly, this same P does not overshoot. Oscillation is not a property of the letter P by itself.

Day 16 turned wheel speeds into a heading. This day chooses the turn command that walks that heading toward an angle.
