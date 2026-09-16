# Interview Questions — Day 03

Interview questions based on **Day 03 – Topics, Queues, and Backpressure**.

---

# Basic Questions

## 1. What is a ROS 2 topic queue?

**Answer**

In ROS 2 user language, the “queue” is primarily the **QoS History + Depth** sample cache on a publisher or subscription endpoint (DDS/RMW history). With `KEEP_LAST`, at most `depth` samples are stored. This is the ROS 2 analogue of ROS 1 `queue_size`.

---

## 2. What happens when the subscriber is slower than the publisher?

**Answer**

The publisher typically keeps publishing at its commanded rate (no app-level backpressure from a slow callback). Unread samples fill the subscription history. With `KEEP_LAST`, once the cache is full, **older samples are dropped** to make room for newer ones. The application still processes remaining samples in order (FIFO among what is still stored), so a deep queue can make you **process stale data**.

---

## 3. Does ROS 2 always keep the newest message and drop the rest?

**Answer**

Not by default. Default depth is **10**, so up to 10 messages can buffer before drops. “Newest kept in the cache” is true under `KEEP_LAST` overflow, but you do **not** automatically jump to processing the newest unless depth is small (especially **1**).

---

## 4. What is the default QoS for publishers and subscriptions in Humble?

**Answer**

`KEEP_LAST` with depth **10**, **RELIABLE**, **VOLATILE** (plus default deadline/lifespan/liveliness). The sensor-data profile uses `KEEP_LAST` depth **5** and **BEST_EFFORT**.

---

# Intermediate Questions

## 5. Why might a robotics team choose depth=1 for a camera topic?

**Answer**

Closed-loop control and many perception consumers care more about **freshness** than processing every frame. Depth 1 limits backlog so the callback tends to see near-latest data, at the cost of dropping intermediate frames under overload.

---

## 6. How can a large queue hurt a real-time robot?

**Answer**

Under sustained overload, a large `KEEP_LAST` depth lets the node fall many frames behind reality while still “successfully” processing old messages. End-to-end decision latency grows roughly with how deep the unread history is — the robot acts on a delayed world.

---

## 7. Are history overflow and BEST_EFFORT the same kind of message loss?

**Answer**

No. History overflow drops oldest samples in a full endpoint cache when new ones arrive. `BEST_EFFORT` allows loss during delivery (e.g. network stress). They are separate mechanisms; on localhost you may see history overflow without additional reliability loss.

---

## 8. Publisher and subscriber each set QoS. Whose depth matters for a slow callback?

**Answer**

Both endpoints have history, but the **subscription** history is the usual place unread samples wait for the executor to take them into a slow callback. Publisher history matters for buffering/retransmission/durability behavior. Depths should be chosen deliberately on both sides; mismatched reliability/durability can prevent connecting at all.

---

# Advanced / Systems Questions

## 9. You profile a Jetson-class robot: camera 30 Hz, detector 10 Hz. Depth is 50 “to be safe.” What do you expect?

**Answer**

Expect a large staleness budget: the detector can be many frames behind live video. Prefer a small depth (often 1–5) for the live perception path, and use a separate recording path if you need completeness.

---

## 10. How would you experimentally prove “no backpressure” on a topic?

**Answer**

Command a fixed publish rate with a slow subscriber callback. Measure publisher output rate and subscriber process rate independently (instrumented logs). If publish rate holds while process rate is lower and sequence gaps appear, the publisher is not being paced by the subscriber’s callback.

---

## 11. Why is sleeping inside a subscription callback a dangerous production pattern — and why use it in Day 03?

**Answer**

Sleep (or heavy work) in a callback blocks that executor thread and prevents other callbacks on that thread from running — a classic ROS concurrency hazard (Day 08). Day 03 uses sleep **deliberately** as a controllable stand-in for slow inference, with a separate frontier callback group/thread so age can still be measured.
