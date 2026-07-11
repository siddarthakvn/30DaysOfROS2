# Interview Questions

## Beginner Level

### 1. What is a ROS 2 node?

**Answer**

A ROS 2 node is an independent executable responsible for performing a specific task within a robotic system. Nodes communicate with each other using ROS 2 communication mechanisms such as topics, services, and actions.

---

### 2. Why does ROS 2 encourage modular software instead of one large program?

**Answer**

Modular software improves maintainability, scalability, fault isolation, and reusability. Each module performs a single responsibility and can be developed, tested, and updated independently.

---

### 3. What is a Single Point of Failure?

**Answer**

A Single Point of Failure is a component whose failure causes the entire system to stop functioning. In a monolithic robotic application, one software crash can terminate the complete robot.

---

## Intermediate Level

### 4. Why should every sensor generally have its own ROS 2 node?

**Answer**

Keeping each sensor in its own node isolates failures, simplifies debugging, improves maintainability, and allows hardware to be replaced without affecting unrelated parts of the system.

---

### 5. What is Fault Isolation?

**Answer**

Fault Isolation is the ability of a system to contain failures within the affected module so that the remaining components continue operating normally.

---

### 6. During today's experiment, why did the GPS, IMU, and Motor daemons continue running after the Camera daemon crashed?

**Answer**

Each daemon was executed as an independent operating system process with its own execution context and memory space. Therefore, the Camera daemon's exception terminated only its own process.

---

### 7. Is every ROS 2 node always a separate operating system process?

**Answer**

Not always.

In most applications, each node runs in its own process.

However, ROS 2 also supports composable nodes, where multiple nodes execute inside a single process to reduce communication overhead and improve performance.

---

## Advanced Level

### 8. Is it always correct to create one node per sensor?

**Answer**

Not necessarily.

While one node per sensor is generally good practice, multiple sensors may be grouped together when they are tightly coupled, require synchronized processing, or have strict performance requirements. The decision depends on the system architecture and engineering trade-offs.

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