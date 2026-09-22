# Day 09 — Parameters (Runtime Configuration)

> **Engineering Question**
>
> **How can a running ROS 2 robot change its behavior without changing its code?**
>
> *(Alternate: Can I tune a robot without restarting its ROS 2 nodes?)*

---

## The story

Day 08 showed a blocked callback can starve a node even when DDS is healthy.

Day 09 asks the configuration question:

> The robot is already running.
> You need a new max speed / gain / threshold.
> Do you stop, edit, rebuild, and relaunch?

ROS 2 answer: **parameters** — per-node settings you can load at startup and change at runtime.

But the trap is:

> `ros2 param set` updates the stored setting.
> Behavior changes only if the node **accepts** the value and **uses** it.

---

## Objective

Prove three facts with a velocity governor:

1. **YAML/CLI overrides** replace code defaults at startup (no rebuild)
2. **Runtime `ros2 param set`** can change live behavior without restart
3. **On-set validation** can reject unsafe values; the old setting remains

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble Hawksbill |
| RMW (pinned) | `rmw_fastrtps_cpp` (Fast DDS) |
| Domain | `ROS_DOMAIN_ID=90` |
| Scope | One host (localhost) |

```bash
cd day09-parameters/ros2_nodes
source ./env.sh
ros2 daemon stop
```

---

## Hypotheses

| ID | Prediction |
|---|---|
| **H2/H6** | YAML `max_velocity: 0.5` → stored/effective max is 0.5 at startup (not code default 1.0) |
| **H2/H3** | Live `ros2 param set … 0.3` → TICKs clamp `out` to 0.3 without restart |
| **H4/H5** | `ros2 param set … 10.0` fails; stored max stays previous; `PARAM_REJECT` logged |

---

## Investigations

| ID | Title | File |
|---|---|---|
| **A** | YAML startup override | [investigations/A-yaml-startup-override.md](investigations/A-yaml-startup-override.md) |
| **B** | Runtime tune (hero) | [investigations/B-runtime-param-set.md](investigations/B-runtime-param-set.md) |
| **C** | Validation reject | [investigations/C-validation-reject.md](investigations/C-validation-reject.md) |

Automated evidence: `./run_smoke.sh` → `assets/A.log`, `B.log`, `C.log`, `comparison.txt`.

---

## Nodes

| Node | Role |
|---|---|
| `velocity_governor.py` | Declares `max_velocity`, clamps a fixed `request_vx`, publishes `/day09/cmd_vel_limited` |

Key parameters: `max_velocity` (validated `[0.0, 2.0]`), `request_vx`, `apply_mode` (`live` \| `once`), `run_sec`.

Config file: [`config/cruise_limit.yaml`](config/cruise_limit.yaml).

---

## Reproduction (Investigation B hero)

```bash
cd day09-parameters/ros2_nodes
source ./env.sh
ros2 daemon stop

# Terminal 1
python3 velocity_governor.py --ros-args \
  -p max_velocity:=1.0 -p request_vx:=1.5 -p apply_mode:=live -p run_sec:=10.0

# Terminal 2 (after a few TICKs)
ros2 param set /velocity_governor max_velocity 0.3
ros2 param get /velocity_governor max_velocity
```

Or run all three:

```bash
cd day09-parameters
./run_smoke.sh
```

---

## Key learnings

- Parameters are **per node**, not a ROS 1 global parameter server.
- Declare + descriptors make the config surface explicit.
- YAML/CLI set **startup** configuration without recompiling.
- Runtime sets go through parameter services + optional **on-set validation**.
- Accepting a set ≠ magic behavior — the node must **read and apply** the value.
- Parameters are for **configuration**; topics/services/actions remain for data/commands/goals (Day 04).

---

## Bridge to other days

| Day | Link |
|---|---|
| **02** | Params belong to nodes |
| **04** | Config ≠ stream / goal |
| **07** | Param services / events use QoS |
| **08** | Param handling runs as executor callbacks |
| **09** | Runtime configuration interface |
| **10** | Launch will wire YAML into bringup |

---

## Interview one-liner

**Parameters are per-node settings. A set only changes the robot if the node accepts it and actually uses the new value.**

---

## Tomorrow

How do you bring up an entire robot with one command? (Launch)
