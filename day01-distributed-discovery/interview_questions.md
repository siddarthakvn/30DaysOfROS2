# Interview Questions — Day 01

Interview questions based on **Day 01 – Distributed Discovery in ROS 2**.

---

# Basic Questions

## 1. Why does ROS 2 not require a ROS Master?

**Answer**

ROS 2 uses DDS-based distributed discovery through the RMW layer. Each node advertises its publishers and subscribers via the middleware, so there is no centralized ROS Master (`roscore`) registry process.

---

## 2. How do ROS 2 nodes discover each other?

**Answer**

Nodes on the same `ROS_DOMAIN_ID` use DDS discovery (behind RMW) to find compatible publishers and subscribers and then exchange data. Nodes on different domains do not discover each other.

---

## 3. What is DDS?

**Answer**

DDS (Data Distribution Service) is the communication middleware ROS 2 uses underneath RMW. It provides discovery, transport, and configurable **Quality of Service (QoS)** policies. Reliability is a **QoS setting** (for example BEST_EFFORT vs RELIABLE), not a guarantee that every DDS deployment is “always reliable.”

---

## 4. What is the role of the RMW layer?

**Answer**

The ROS Middleware (RMW) layer abstracts client libraries (`rclcpp`, `rclpy`) from a specific DDS vendor. Application code talks to RMW; the active implementation (for example Fast DDS or Cyclone DDS) can change without rewriting node logic.

---

## 5. Why does RMW exist?

**Answer**

Without RMW, ROS 2 would be hard-tied to one middleware. RMW gives a common interface so you can switch implementations such as Fast DDS (`rmw_fastrtps_cpp`) or Cyclone DDS (`rmw_cyclonedds_cpp`) at the environment / install level.

---

# Intermediate Questions

## 6. What is `ROS_DOMAIN_ID`?

**Answer**

`ROS_DOMAIN_ID` selects the DDS domain. Nodes in different domains do not discover or communicate with each other, even on the same machine or Wi-Fi network. Isolation is typically **silent** (no crash, no “wrong domain” error).

---

## 7. What happens if the publisher starts before the subscriber?

**Answer**

The publisher keeps publishing. When a compatible subscriber later joins on the same domain, discovery matches them and the subscriber receives **new** messages. With default demo QoS, it does not replay samples published before it subscribed.

---

## 8. Why didn't the listener receive the old messages?

**Answer**

Default talker/listener QoS is volatile (no durable history for late joiners). The listener only receives messages published after it joined. Durability and history depth are Day 07 territory.

---

## 9. What happens when nodes belong to different `ROS_DOMAIN_ID`s?

**Answer**

They do not discover each other. No data flows on that topic pairing, and neither side necessarily reports an error.

---

## 10. What happens when a node leaves a running ROS 2 system?

**Answer**

Other nodes keep running. The departed participant eventually drops out of the ROS Graph after discovery / liveliness updates. The CLI view (`ros2 node list`) may lag a short time after Ctrl+C — it is not an instant Master delete.

---

# Advanced Questions

## 11. How does ROS 2 support scalable distributed robotic systems?

**Answer**

Distributed discovery removes a single Master SPOF for name lookup. Domain IDs isolate deployments. QoS lets you tune reliability and history per topic. Scalability still depends on network design (multicast, Discovery Server, etc.) — localhost demos do not prove every Wi-Fi fleet “just works.”

---

## 12. Why is dynamic discovery important in robotics?

**Answer**

Robots, sensors, and PCs start, stop, and reconnect at different times. Dynamic discovery lets peers join and leave without restarting the whole system or depending on a Master that must be up first.

---

## 13. What middleware did you use during your experiments?

**Answer**

Fast DDS via `rmw_fastrtps_cpp` (Humble default in this series).

---

## 14. How did you verify the middleware implementation?

**Answer**

```bash
ros2 doctor --report | grep -i rmw
```

Evidence: `assets/middleware_verification.png` shows `RMW MIDDLEWARE: rmw_fastrtps_cpp`.

---

## 15. What is the biggest architectural difference between ROS 1 and ROS 2 (for discovery)?

**Answer**

ROS 1 discovery depends on a centralized Master (`roscore`). ROS 2 discovery is peer-oriented through DDS/RMW and does not require that Master process.

---

# Practical Interview Scenario

**Question**

Imagine 20 autonomous warehouse robots on the same Wi-Fi. How would you prevent robots from one deployment communicating with another?

**Answer**

Assign different `ROS_DOMAIN_ID`s per deployment (and document them). That creates logical isolation so robots only discover peers in their own domain. Also verify that CLI tools and launch files export the intended domain, and remember that a wrong domain fails silently.
