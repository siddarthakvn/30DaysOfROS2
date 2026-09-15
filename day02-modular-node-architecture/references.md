# References

Primary sources and supporting material for Day 02 (nodes, modular architecture, fault isolation).

---

## ROS 2 Documentation (primary)

- [About Nodes (Humble)](https://docs.ros.org/en/humble/Concepts/Basic/About-Nodes.html) — what a node is in the ROS graph
- [About Composition (Humble)](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Composition.html) — process layout as a deploy-time choice; separate processes for process/fault isolation vs single process for lower overhead
- [ROS 2 Concepts overview (Humble)](https://docs.ros.org/en/humble/)

Composition docs explicitly separate:

- multiple nodes in **separate processes** → process/fault isolation, easier per-node debugging
- multiple nodes in a **single process** → lower overhead, optional intra-process communication

---

## Software Engineering

Robert C. Martin — *Clean Architecture*

- Single Responsibility Principle
- Separation of Concerns
- Modular software design

---

## Operating Systems

Abraham Silberschatz — *Operating System Concepts*

- Processes and address spaces
- Process isolation
- Independent failure domains

---

## Distributed Systems

Andrew S. Tanenbaum — *Distributed Systems: Principles and Paradigms*

- Independent components
- Reliability and partial failure

---

## Robotics Software Engineering

Morgan Quigley, Brian Gerkey, William D. Smart — *Programming Robots with ROS*

- Modular robot software
- Distributed robotics components

---

## Experiments Performed

### Investigation A

- Monolithic Python robot (Camera, GPS, IMU, Motor)
- Intentional camera exception → full application termination
- Evidence: `assets/expA_*.png`

### Investigation B

- Four independent daemon processes
- Camera crash → GPS/IMU/Motor continued
- Evidence: `assets/expB_*.png`

### Investigation C

- Same four `rclpy` nodes; only process count changed
- **C1** (4 processes): camera exited; others survived
- **C2** (1 composed process): camera `RuntimeError` killed all
- Evidence: `assets/expC1_multiprocess_survivors.png`, `assets/expC2_composed_shared_fate.png`
- Note: C2 uses a Python shared executor as a teaching stand-in for multi-node-in-one-process; not a full C++ `ComposableNodeContainer` demo

---

## Notes

- A and B intentionally use plain Python so process isolation is visible without ROS APIs.
- C is required to answer the curriculum question about **nodes** without conflating them with processes.
- Topics / backpressure are Day 03.
