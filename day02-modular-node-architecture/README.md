# Day 02 — Should Every Sensor Be a Separate ROS 2 Node?

> **Engineering Question**
>
> **Should every sensor be a separate ROS 2 node?**

*(Curriculum alternate: why design around nodes instead of one giant robot program? Same intent.)*

---

## Objective

Day 01 showed how ROS 2 nodes find each other without a ROS Master.

Day 02 asks a more fundamental architecture question: why split a robot into modules at all — and whether a ROS 2 **node** is the same thing as a fault-isolation boundary.

Investigations A and B use plain Python to show process-level SPOF vs isolation. Investigation C uses real ROS 2 nodes to show that **node ≠ process**.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble Hawksbill (required for Investigation C) |
| Default experiment domain (C) | `ROS_DOMAIN_ID=42` |
| A / B | Plain Python 3 — no ROS required |

---

## Learning Objectives

- Why monolithic robotic software creates a Single Point of Failure
- What fault isolation requires (OS process boundaries)
- Separation of Concerns and Single Responsibility
- What a ROS 2 node is vs what an OS process is
- Why ROS 2 allows composition (many nodes, one process)
- Why “separate node” does not automatically mean “fault isolated”

---

## Investigations

### Investigation A — Monolithic Robot Architecture

One Python process runs Camera, GPS, IMU, and Motor. An intentional camera exception terminates the entire application → **Single Point of Failure**.

Details: [A-monolithic-vs-modular.md](investigations/A-monolithic-vs-modular.md)

### Investigation B — Fault Isolation Through Independent Processes

The same four subsystems run as four OS processes (daemons). Crashing the camera leaves GPS, IMU, and Motor running → **process-level fault isolation**.

Details: [B-fault-isolation.md](investigations/B-fault-isolation.md)

### Investigation C — Node Boundary vs Process Boundary

The same four **ROS 2 nodes** are deployed two ways:

| Run | Layout | Observed result |
|---|---|---|
| **C1** | 4 nodes / 4 processes | Camera exits; other three keep running |
| **C2** | 4 nodes / 1 process | Camera `RuntimeError` kills the whole container |

Architecture stays modular either way. Only process layout decides who survives.

Details: [C-node-boundary-vs-process-boundary.md](investigations/C-node-boundary-vs-process-boundary.md)

---

## Reproduction (quick start)

### A — monolith

```bash
cd day02-modular-node-architecture/daemon
python3 monolithic_robot.py
```

### B — daemons (four terminals)

```bash
cd day02-modular-node-architecture/daemon
python3 camera_daemon.py   # terminal 1
python3 gps_daemon.py      # terminal 2
python3 imu_daemon.py      # terminal 3
python3 motor_daemon.py    # terminal 4
```

### C — ROS 2 node vs process

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=42
cd day02-modular-node-architecture/ros2_nodes
bash run_investigation_c.sh
```

Or run C1/C2 manually as documented in Investigation C.

---

## Repository Structure

```
day02-modular-node-architecture/
├── assets/
│   ├── expA_*.png
│   ├── expB_*.png
│   ├── expC1_multiprocess_survivors.png
│   └── expC2_composed_shared_fate.png
├── daemon/                 # Investigations A & B (plain Python)
├── ros2_nodes/             # Investigation C (rclpy)
│   ├── sensor_node.py
│   ├── composed_container.py
│   └── run_investigation_c.sh
├── investigations/
│   ├── A-monolithic-vs-modular.md
│   ├── B-fault-isolation.md
│   └── C-node-boundary-vs-process-boundary.md
├── interview_questions.md
├── references.md
└── README.md
```

---

## Screenshots / Evidence

### Investigation A

- Monolith running · Monolith crash

### Investigation B

- All daemons running · Camera crashed, others alive

### Investigation C

- [C1 survivors](assets/expC1_multiprocess_survivors.png) — camera `Exit 1`, others still `Running`
- [C2 shared fate](assets/expC2_composed_shared_fate.png) — one PID; camera fault ends the process

---

## Key Engineering Concepts

- Monolithic vs modular architecture
- Single Point of Failure
- Fault isolation (process boundary)
- ROS 2 nodes (responsibility / graph participants)
- Composition (deploy-time process layout)
- Separation of Concerns / Single Responsibility

---

## Engineering Conclusion

**Should every sensor be a separate ROS 2 node?**

**Yes, in general — as nodes.** Separate nodes give clean interfaces, independent testing, and the option to isolate later.

**Fault isolation is not automatic.** It comes from **OS processes**, not from the node abstraction alone. Composition keeps node modularity while deliberately sharing fate for performance.

Investigation B showed isolation. Investigation C showed *why*: the process boundary, not the word “node.”

---

## Real Robotics Connection

Perception pipelines are often composed for large-message efficiency. Drivers and safety-critical control usually keep separate processes. Drawing four boxes on an architecture diagram does not tell you whether a camera crash takes down motor control — asking how many processes does.

---

## References

See [references.md](references.md)

---

## Next Investigation

**Day 03**

> **What happens when sensor data is published faster than a robot can process it?**

Topics, publishers, subscribers, and backpressure.
