# 🤖 30 Days of ROS 2 — Core to Autonomy

### 30 Engineering Questions. 30 ROS 2 Experiments. 30 GitHub Demos.

> Learn one concept. Build one experiment. Understand the system.

---

## 🚀 About the Challenge

I have worked with ROS 2 while building autonomous robotic systems.

But while working on these projects, I kept coming across questions that made me realise something:

Using ROS 2 and deeply understanding what is happening underneath are two different things.

How do ROS 2 nodes discover each other without a ROS Master?

What happens when one callback blocks?

Why does a robot need `map`, `odom`, and `base_link`?

How does wheel rotation become odometry?

What actually happens after a Nav2 goal is sent?

And what breaks when one ROS 2 robot becomes three?

These are the kinds of questions I want to explore.

For the next 30 days, I will investigate one engineering question behind autonomous robotic systems through a small and reproducible ROS 2 experiment.

This is not a 30-day mega project.

This is not a collection of ROS 2 definitions.

Each day is about asking a question, building an experiment, observing what happens, and understanding the engineering behind the result.

---

## 🎯 The Challenge Rule

### 1 Question → 1 Concept → 1 Experiment → 1 GitHub Demo → 1 Post

Every day I will:

1. Ask one robotics engineering question.
2. Understand the concept behind it.
3. Build a small ROS 2 experiment.
4. Observe what actually happens.
5. Document the implementation and results.
6. Push the experiment to GitHub.
7. Share what I learned publicly.

---

## 🧪 How the Experiments Work

Every experiment follows the same thinking process:

```text
Engineering Question
        ↓
Concept
        ↓
Hypothesis
        ↓
Experiment
        ↓
Observation
        ↓
Engineering Understanding
```

The emphasis is always on **why** something behaves the way it does — not just how to make it work.

---

## 📅 The 30 Days

> ✅ = published · rows without a link are still ahead on the roadmap.

| Day | Engineering Question | Core Concepts | |
|:---:|---|---|:---:|
| [01](day01-distributed-discovery/) | How do ROS 2 nodes find each other without a ROS Master? | ROS 2 architecture, DDS, RMW, discovery, ROS graph | ✅ |
| [02](day02-modular-node-architecture/) | Should every sensor be a separate ROS 2 node? | Nodes, modular architecture, fault isolation | ✅ |
| 03 | What happens when sensor data is published faster than a robot can process it? | Topics, publishers, subscribers, queues | |
| [04](day04-communication-patterns/) | When should a robot use a Topic, Service, or Action? | ROS 2 communication patterns | |
| [05](day05-action-cancellation/) | How does a robot cancel a task while it is still executing? | Actions, goals, feedback, cancellation | |
| 06 | How do robots communicate data that standard ROS messages cannot represent? | Custom `.msg`, `.srv`, `.action` interfaces | |
| [07](day07-qos/) | Can the wrong QoS policy silently break a robotic system? | DDS QoS, reliability, durability, history, depth | ✅ |
| [08](day08-executors/) | What happens when one callback blocks an entire ROS 2 node? | Executors, callbacks, callback groups, multithreading | |
| [09](day09-parameters/) | Can I tune a robot without restarting its ROS 2 nodes? | Parameters and runtime configuration | |
| [10](day10-launch/) | How do you bring up an entire robot with one command? | Launch files, launch arguments, remapping | |
| [11](day11-urdf-xacro/) | How does ROS 2 know what a robot physically looks like? | URDF, links, joints, Xacro | |
| [12](day12-tf2/) | Why does a robot need `base_link`, `odom`, and `map`? | TF2, coordinate frames, transforms | |
| 13 | Who actually publishes the robot's transform tree? | Robot State Publisher, Joint State Publisher, TF tree | |
| 14 | I pressed one keyboard key. How did that make a simulated robot move? | Gazebo, teleoperation, `/cmd_vel`, Twist, differential drive | |
| 15 | My simulated LiDAR was perfect. Why is that a problem? | Gazebo sensors, plugins, LiDAR, IMU, noise, update rate | |
| 16 | How does wheel rotation become robot position? | Differential-drive kinematics, wheel velocities, odometry | |
| 17 | Why does my robot oscillate around the target angle? | PID control, error, P/I/D terms, controller tuning | |
| 18 | Wheel odometry drifts and IMUs drift — so how does a robot estimate its pose? | Sensor fusion, EKF, covariance, `robot_localization` | |
| 19 | What actually happens when a robot "builds a map"? | LiDAR SLAM, scan matching, occupancy grids | |
| 20 | A robot has a map — but how does it know where it is on that map? | Localization, AMCL, particle filters | |
| 21 | What actually happens after I send a Nav2 goal? | Nav2 architecture, NavigateToPose, planner, controller | |
| 22 | Why was my robot avoiding obstacles that didn't exist? | Global/local costmaps, obstacle layer, inflation layer | |
| 23 | How does a robot choose a path from A to B? | A*, Dijkstra, global path planning | |
| 24 | What happens when an obstacle suddenly appears on the planned path? | Local controllers, dynamic obstacle avoidance, replanning | |
| 25 | Why does Nav2 use Behavior Trees instead of one giant state machine? | Behavior Trees, fallback, recovery, retry | |
| 26 | How should a rescue robot transition from SEARCHING to VERIFYING to LOCKDOWN? | Finite state machines, mission logic, coordinator design | |
| 27 | Running YOLO is easy — but how do you make perception part of a ROS 2 system? | ROS images, OpenCV, `cv_bridge`, YOLOv8, detection topics | |
| 28 | YOLO gives pixels. Nav2 needs map coordinates. How do we connect them? | Camera geometry, depth/distance, TF2, map-frame localization | |
| 29 | How can an ESP32 become part of a ROS 2 system? | micro-ROS, ESP32, DDS-XRCE, agent, bidirectional `/cmd_vel` + status | |
| 30 | What breaks when you scale one ROS 2 robot to three? | Namespaces, topic isolation, multi-robot architecture, task allocation | |

---

## 📂 How Each Day Is Organised

```text
dayNN-topic-name/
├── README.md              # the question, the concept, the takeaway
├── investigations/        # one file per experiment: hypothesis → method → result
├── assets/                # screenshots and plots captured during the experiments
├── interview_questions.md # what this concept looks like in an interview
└── references.md          # everything I read to understand it
```

---

## 🛠 Environment

Every experiment in this repository was run on:

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble Hawksbill |
| Middleware (RMW) | Fast DDS (`rmw_fastrtps_cpp`) |
| Language | Python (`rclpy`), C++ (`rclcpp`) where relevant |
| Simulation | Gazebo + RViz2 (from Day 14 onwards) |

Where a result depends on the middleware, the RMW implementation is stated explicitly in that day's write-up.

---

## ▶️ Reproducing the Experiments

```bash
git clone https://github.com/siddarthakvn/30DaysOfROS2.git
cd 30DaysOfROS2

source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=10

cd day01-distributed-discovery
```

Each day's `README.md` lists the exact commands used, so every observation in this repository can be reproduced and challenged.

---

## 🤝 Following Along

If you're learning ROS 2, feel free to explore the repository, reproduce the experiments, and share your observations — especially if you get a **different** result. That is the most useful thing that can happen to an experiment.

**#30DaysOfROS2**

---

## 📄 License

Released under the [MIT License](LICENSE).
