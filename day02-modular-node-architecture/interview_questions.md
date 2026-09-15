# Interview Questions

## Beginner Level

### 1. What is a ROS 2 node?

**Answer**

A ROS 2 node is a named unit of responsibility in the ROS graph — typically one focused task with its own publishers, subscribers, services, actions, and parameters. It is not the same thing as an OS process: multiple nodes can share one process (composition), or a node can run alone in its own process.

---

### 2. Why does ROS 2 encourage modular software instead of one large program?

**Answer**

Modular software improves maintainability, scalability, reusability, and clear ownership of subsystems. Each module can be developed, tested, and updated independently. Fault isolation is related but is not automatic from modularity alone — it depends on process deployment (see Investigation C).

---

### 3. What is a Single Point of Failure?

**Answer**

A Single Point of Failure is a component whose failure causes the entire system to stop functioning. In a monolithic robotic application, one software crash can terminate the complete robot.

---

## Intermediate Level

### 4. Why should every sensor generally have its own ROS 2 node?

**Answer**

Separate sensor nodes give clean interfaces, independent testing, easier hardware swaps, and the *option* to isolate faults later by running them in separate processes. A separate node alone does not guarantee fault isolation if those nodes are composed into one process.

---

### 5. What is Fault Isolation?

**Answer**

Fault isolation is the ability to contain a failure so unrelated work can continue. In today's experiments, that containment came from **OS process** boundaries (separate address spaces and lifetimes), not from ROS node names by themselves.

---

### 6. During today's experiment, why did the GPS, IMU, and Motor daemons continue running after the Camera daemon crashed?

**Answer**

Each daemon was executed as an independent operating system process with its own execution context and memory space. Therefore, the Camera daemon's exception terminated only its own process.

---

### 7. Is every ROS 2 node always a separate operating system process?

**Answer**

No. A node is a graph participant; a process is a deployment choice.

ROS 2 supports running nodes in separate processes (process/fault isolation, easier per-node debugging) or composing many nodes into one process (lower overhead, optional intra-process communication). Investigation C showed the same four nodes surviving a camera fault only in the multi-process deployment.

---

## Advanced Level

### 8. Is it always correct to create one node per sensor?

**Answer**

One node per sensor is generally good practice for interfaces and ownership. Exceptions exist when sensors are tightly coupled or must be synchronized as one unit.

Separately: even with one node per sensor, you still decide process layout. Tight perception pipelines may be composed; safety-critical drivers usually keep their own process.

---

### 9. Why did ROS adopt a distributed architecture?

**Answer**

Distributed architectures improve scalability, reliability, maintainability, and modularity. Independent software components can communicate while remaining loosely coupled, allowing robotic systems to grow in complexity without becoming difficult to manage.

---

### 10. Which software engineering principles were demonstrated in today's experiments?

**Answer**

- Single Responsibility Principle
- Separation of Concerns
- Fault Isolation
- Modular Design
- Loose Coupling (introduced conceptually)
- Scalability
- Maintainability
- Reusability

---

## Challenge Questions

These questions test conceptual understanding rather than memorization.

### Q1.

Suppose your Camera node crashes during autonomous navigation.

Should the Motor Controller immediately stop?

Why or why not?

---

### Q2.

A robot consists of Camera, LiDAR, GPS, IMU, Navigation, and Motor Control.

Would you implement everything inside one node or create multiple nodes?

Explain your design decisions.

---

### Q3.

Suppose you replace an Intel RealSense camera with a ZED camera.

In a modular architecture, which software component should require modification?

Why?

---

### Q4.

What is the difference between a monolithic architecture and a distributed architecture?

Provide examples from today's experiments.

---

### Q5.

If you were designing a Search and Rescue Robot, how would you divide the robot into independent ROS 2 nodes?

Explain your reasoning.

---

### Q6.

You have four sensor nodes. In deployment A each runs in its own process. In deployment B all four are composed into one process. A camera driver raises an unhandled exception.

What happens in A vs B, and what does that teach about nodes vs processes?