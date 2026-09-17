# Interview Questions — Day 04

Interview questions based on **Day 04 – Topics, Services, and Actions**.

---

# Basic Questions

## 1. When should you use a Topic vs a Service vs an Action?

**Answer**

- **Topic:** continuous streams (sensors, state, `cmd_vel`-style commands). One-way; no per-message result/cancel.
- **Service:** short request/response that finishes quickly and needs one answer.
- **Action:** long-running goals that need progress feedback and/or cancellation.

Rule of thumb: stream → Topic; quick ask → Service; mission → Action.

---

## 2. Why must services not be used for long preemptable robot tasks?

**Answer**

Humble docs state services are expected to return quickly and should **never** be used for longer-running processes, especially ones that may need preemption. There is no standard feedback channel or cancel protocol. Use an **Action**.

---

## 3. How does Action cancellation differ from stopping a Topic publisher?

**Answer**

Stopping a publisher only stops new messages. There is no goal ID, no cancel acceptance, and no guaranteed cleanup handshake. Action cancel is an explicit request; the server may enter `CANCELING`, clean up, and end in `CANCELED` with a correlated result.

---

## 4. What is under the hood of a ROS 2 Action?

**Answer**

Per the ROS 2 design doc, an action is **three services** (`send_goal`, `cancel_goal`, `get_result`) plus **two topics** (`feedback`, `status`) under a `/_action/` namespace, hidden from default `ros2 topic/service list`.

---

# Intermediate Questions

## 5. Can there be multiple service or action servers on the same name?

**Answer**

There should be only **one** server per name. With multiple, it is **undefined** which receives client requests. Multiple clients are fine.

---

## 6. Are ROS 2 services “synchronous”?

**Answer**

At the *interaction model* level, docs describe services as synchronous request/response. Client libraries may expose blocking or async APIs, and the common C implementation is asynchronous under the hood. The engineering point is the contract: one request → one response, no progress/cancel — not that the OS thread must freeze forever.

---

## 7. Give a real robotics example of each pattern.

**Answer**

- Topic: `/scan`, `/odom`, `/cmd_vel`
- Service: spawn, clear costmap, load map, one-shot IK
- Action: Nav2 `navigate_to_pose`, MoveIt trajectory execution, turtlesim `rotate_absolute`

---

# Advanced Questions

## 8. Why do Actions exist if you could wire Topics + Services yourself?

**Answer**

You can hack a protocol with topics and services, but Actions give a **standard goal lifecycle** (accept, feedback, result, cancel), UUIDs, first-class client APIs, and `ros2 action` introspection. Homegrown stacks diverge and break tooling/interop (Nav2, MoveIt, mission FSMs).

---

## 9. What fails if navigation is implemented as a long Service?

**Answer**

The mission layer cannot cleanly preempt on obstacle / e-stop / higher-priority goal via a cancel protocol; it is stuck waiting for one reply; there is no standard progress channel. That is an architecture failure, not just an API preference.
