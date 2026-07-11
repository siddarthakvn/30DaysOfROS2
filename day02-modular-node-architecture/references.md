# References

The following resources were used to understand the software engineering principles and ROS 2 concepts explored in this investigation.

---

## ROS 2 Documentation

- ROS 2 Concepts
- Understanding Nodes
- ROS 2 Architecture

https://docs.ros.org/en/humble/

---

## Software Engineering

Robert C. Martin

**Clean Architecture: A Craftsman's Guide to Software Structure and Design**

Key concepts referenced:

- Single Responsibility Principle
- Separation of Concerns
- Modular Software Design

---

## Operating Systems

Abraham Silberschatz

**Operating System Concepts**

Relevant topics:

- Processes
- Process Isolation
- Independent Execution
- Fault Isolation

---

## Distributed Systems

Andrew S. Tanenbaum

**Distributed Systems: Principles and Paradigms**

Relevant concepts:

- Distributed Architecture
- Independent Components
- Reliability
- Scalability

---

## Robotics Software Engineering

Morgan Quigley, Brian Gerkey, William D. Smart

**Programming Robots with ROS**

Referenced concepts:

- Modular Robot Software
- Distributed Robotics
- Software Components

---

## Experiments Performed

Investigation A

- Simulated a monolithic robotic application.
- Introduced an intentional software failure.
- Observed complete application termination.

---

Investigation B

- Divided the robotic system into independent daemons.
- Introduced an intentional Camera daemon failure.
- Observed that unrelated daemons continued executing.

---

## Notes

This investigation intentionally focused on software architecture rather than ROS communication.

Topics, publishers, subscribers, and message passing will be explored in **Day 03**.