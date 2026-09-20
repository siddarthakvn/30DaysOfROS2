# Interview Questions — Day 07

Interview questions based on **Day 07 – QoS Compatibility**.

---

## 1. What does QoS stand for?

**Answer**

Quality of Service.

---

## 2. Why can two ROS 2 nodes be on the same topic and still not exchange messages?

**Answer**

Because each endpoint has a QoS contract. DDS only creates a data path if the publisher’s offered QoS is strong enough for what the subscription requests (Request vs Offered). If reliability or durability (among others) is incompatible, there is **no connection** — messages do not flow.

---

## 3. What happens with a BEST_EFFORT publisher and a RELIABLE subscriber?

**Answer**

They are incompatible. The endpoints may still appear in `ros2 topic info --verbose`, but no messages are delivered to that subscriber.

---

## 4. Is QoS mismatch the same as packet loss?

**Answer**

No. Packet loss is a delivery problem on an existing path. QoS mismatch usually means the path was never established for that publisher–subscriber pair.

---

## 5. How do you diagnose a silent QoS failure?

**Answer**

Use `ros2 topic info <topic> --verbose` and compare publisher vs subscriber reliability and durability. Confirm with an instrumented subscriber receive counter. Do not trust `ros2 topic list` alone.

---

## 6. What is TRANSIENT_LOCAL durability for?

**Answer**

It lets the publisher keep recent samples for late-joining compatible subscribers (ROS 1 latch-like behavior when both sides agree). Maps, static TF, and robot description often need this pattern.

---

## 7. Is “always use RELIABLE” good engineering advice?

**Answer**

No. High-rate sensors on lossy links often prefer BEST_EFFORT for freshness. Commands and critical state usually want RELIABLE. Choose from data semantics and loss consequences.

---

## 8. One-liner connecting Day 01 and Day 07?

**Answer**

Discovery finds the nodes; QoS decides whether they may exchange data.
