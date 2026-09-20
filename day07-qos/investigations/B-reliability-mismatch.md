# Investigation B — Reliability Mismatch (Hero)

## Engineering question

Can publisher and subscriber both exist on the same topic while messages never arrive because reliability QoS is incompatible?

---

## Hypotheses

**H2:** BEST_EFFORT publisher + RELIABLE subscriber → endpoints visible, `recv_total` stays **0**.

**H3:** Changing only the subscriber to BEST_EFFORT restores flow.

---

## Why this matters

This is the classic “sensor topic looks live but my node / `ros2 topic echo` sees nothing” failure.

Official ROS 2 rule: a BEST_EFFORT publisher **cannot** satisfy a RELIABLE subscription → **no connection**, not “lossy connection.”

---

## Setup

### B1 — mismatch

| | Publisher | Subscriber |
|---|---|---|
| Reliability | **BEST_EFFORT** | **RELIABLE** |
| Durability | VOLATILE | VOLATILE |

### B2 — fix

| | Publisher | Subscriber |
|---|---|---|
| Reliability | BEST_EFFORT | **BEST_EFFORT** |
| Durability | VOLATILE | VOLATILE |

---

## Procedure

```bash
cd day07-qos/ros2_nodes
source ./env.sh
ros2 daemon stop
bash run_B.sh

# Terminal 1
python3 qos_pub.py --ros-args \
  -p reliability:=best_effort -p durability:=volatile

# Terminal 2 (mismatch)
python3 qos_sub.py --ros-args \
  -p reliability:=reliable -p durability:=volatile

# Terminal 3
ros2 topic info /qos_demo/stream --verbose
ros2 topic list | grep qos_demo
```

Then restart Terminal 2 with matching BEST_EFFORT.

---

## Expected results

| Step | Expect |
|---|---|
| B1 | Topic listed; both endpoints in `--verbose`; SUB `recv_total=0` while PUB climbs |
| B2 | Same publisher; SUB starts receiving |

---

## Actual results

See:

- [`../assets/B1_mismatch.log`](../assets/B1_mismatch.log)
- [`../assets/B1_topic_info.txt`](../assets/B1_topic_info.txt)
- [`../assets/B2_fixed.log`](../assets/B2_fixed.log)

| Step | Observation |
|---|---|
| B1 topic listed? | Yes |
| B1 endpoints visible? | Yes (pub BEST_EFFORT, sub RELIABLE) |
| B1 `recv_total` | Stayed **0** while PUB `seq` advanced |
| B2 after matching | `recv_total` increased |

---

## Analysis

Discovery and topic listing succeeded. DDS QoS matching failed on reliability.
The system looked “connected” from a casual graph check and was silent on the data path.

---

## Conclusion

**Wrong QoS can silently break a robotic system** without crashing nodes.
Fix the contract (match reliability), not the “queue size.”
