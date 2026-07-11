# Day 02 — Should Every Sensor Be a Separate ROS 2 Node?

> **Engineering Question**
>
> **Should every sensor be a separate ROS 2 node?**

---

## Objective

In Day 1, we explored how ROS 2 nodes discover each other without a ROS Master.

In Day 2, we step back from ROS and investigate a more fundamental software engineering question:

**Why is modern robotic software designed as multiple independent nodes instead of one large application?**

Rather than accepting modularity as a ROS convention, this investigation demonstrates the architectural reasons behind it through practical experiments.

---

# Learning Objectives

By the end of this investigation, I was able to understand:

- Why monolithic robotic software becomes difficult to maintain.
- What a Single Point of Failure is.
- The importance of Fault Isolation.
- Separation of Concerns.
- Single Responsibility Principle.
- Why distributed software architectures are preferred for robotic systems.
- Why ROS 2 organises robotic applications into independent nodes.

---

# Investigations

## Investigation A — Monolithic Robot Architecture

**Engineering Question**

> What happens if an entire robotic system is implemented as one program?

### Experiment

A simulated robot consisting of:

- Camera
- GPS
- IMU
- Motor Controller

was implemented inside a single Python application.

A software failure was intentionally introduced into the Camera module.

### Result

The complete application terminated immediately.

This demonstrated the concept of a **Single Point of Failure**, where one software failure causes the entire robotic system to stop.

---

## Investigation B — Fault Isolation Through Independent Processes

**Engineering Question**

> Can independent software modules continue operating if one module crashes?

### Experiment

The robotic system was divided into four independent daemons:

- Camera Daemon
- GPS Daemon
- IMU Daemon
- Motor Daemon

The Camera daemon was intentionally crashed.

### Result

Only the Camera daemon terminated.

The remaining daemons continued executing normally.

This demonstrated the principle of **Fault Isolation**, where failures remain isolated to the affected subsystem.

---

# Repository Structure

```
day02-modular-node-architecture/

├── assets/
│
├── daemon/
│   ├── monolithic_robot.py
│   ├── camera_daemon.py
│   ├── gps_daemon.py
│   ├── imu_daemon.py
│   └── motor_daemon.py
│
├── investigations/
│   ├── A-monolithic-vs-modular.md
│   └── B-fault-isolation.md
│
├── interview_questions.md
├── references.md
└── README.md
```

---

# Screenshots

## Investigation A

- Monolithic Robot Running
- Monolithic Robot Crash

## Investigation B

- All Daemons Running
- Camera Daemon Crash While Other Daemons Continue

---

# Key Engineering Concepts

- Monolithic Architecture
- Modular Architecture
- Distributed Software Systems
- Single Responsibility Principle
- Separation of Concerns
- Fault Isolation
- Single Point of Failure
- Process Isolation
- Maintainability
- Scalability

---

# Key Takeaways

- One large robotic application creates a Single Point of Failure.
- Independent software modules improve system reliability.
- Process isolation prevents one software failure from affecting unrelated components.
- Modular software is easier to maintain, debug, and extend.
- ROS 2 adopts this software architecture by organising robotic systems into independent nodes.

---

# Real Robotics Connection

Modern robotic systems—including autonomous mobile robots, drones, industrial manipulators, and autonomous vehicles—are rarely implemented as one large application.

Instead, perception, localization, planning, navigation, control, diagnostics, and hardware interfaces execute as independent software modules.

ROS 2 formalises this architecture through nodes, allowing robotic systems to remain modular, scalable, and fault tolerant.

---

# References

See **references.md**

---

## Next Investigation

**Day 03**

> **What happens when sensor data is published faster than a robot can process it?**

We'll investigate how independent ROS 2 nodes exchange information using publishers, subscribers, topics, and message queues.