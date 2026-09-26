# Day 12 — TF2 Frames (`base_link` / `odom` / `map`)

> **Engineering Question**
>
> **Why does a robot need `base_link`, `odom`, and `map`?**

---

## The story

Your robot can be in three places at once — structurally.

| Frame | Job |
|---|---|
| **`base_link`** | The body |
| **`odom`** | Smooth dead reckoning (drifts) |
| **`map`** | Global truth (may jump) |

One frame cannot do all three jobs. REP-105 chains them:

```text
map → odom → base_link
```

Day 12 proves why — with a driving robot, a localization **jump**, and a deliberately broken dual-parent tree.

---

## Objective

1. **A** — Only `odom`→`base_link`: continuous motion, no global frame  
2. **B** — Add `map`→`odom` jump: `map` pose jumps, `odom` stays smooth  
3. **C** — Illegal dual parent (`map`→`base_link` + `odom`→`base_link`): TF tree splits  

Bonus probe: a fixed **kitchen** landmark in `map`, expressed in `base_link` — snaps when the map jumps.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| RMW | `rmw_fastrtps_cpp` |
| Domains | A=`120` · B=`121` · C=`122` |

```bash
cd day12-tf2
source ros2_nodes/env.sh
```

---

## Quick start

```bash
cd day12-tf2
source ros2_nodes/env.sh

# A — odom only
ros2 launch launch/demo.launch.py mode:=a

# B — map jump at t=5s
ros2 launch launch/demo.launch.py mode:=b jump_at_sec:=5.0

# C — dual-parent conflict
python3 ros2_nodes/conflict_demo.py
```

Evidence:

```bash
./run_smoke.sh
```

---

## Layout

```text
day12-tf2/
├── ros2_nodes/
│   ├── odom_driver.py      # continuous odom → base_link
│   ├── map_localizer.py    # map → odom (+ jump)
│   ├── frame_probe.py      # continuity metrics + kitchen point
│   └── conflict_demo.py    # illegal dual parent
├── launch/demo.launch.py
└── assets/                 # A/B/C logs + LinkedIn hero
```

---

## Investigations (real results)

| ID | What | Headline metric |
|---|---|---|
| **A** | Odom only | `odom` max step **0.025 m** · `map` samples **0** |
| **B** | Map jump | `odom` max step **0.025 m** · `map` max step **1.55 m** |
| **C** | Dual parent | TF: *“two or more unconnected trees”* |

Details: `investigations/`.

---

## Key learnings

- `base_link` is the body; sensors hang from it (Day 11 URDF).  
- `odom` must stay **continuous** — control hates teleports.  
- `map` may **jump** — localization corrections live on `map`→`odom`.  
- Never give `base_link` two parents.  
- TF2 is the shared spatial API, not “just RViz.”

---

## Interview one-liner

**Three frames, one tree: `map`→`odom`→`base_link` — body, drift, and truth without making control and localization destroy each other.**
