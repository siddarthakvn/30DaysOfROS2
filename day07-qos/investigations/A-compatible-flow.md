# Investigation A — Compatible Flow

## Engineering question

If publisher and subscriber QoS are compatible, do messages flow normally?

---

## Hypothesis

**H1:** RELIABLE + VOLATILE on both ends → `recv_total` increases and `last_seq` advances.

---

## Setup

| | Publisher | Subscriber |
|---|---|---|
| Topic | `/qos_demo/stream` | same |
| Reliability | RELIABLE | RELIABLE |
| Durability | VOLATILE | VOLATILE |
| History | KEEP_LAST depth 10 | KEEP_LAST depth 10 |
| Rate | 10 Hz | — |

---

## Procedure

```bash
cd day07-qos/ros2_nodes
source ./env.sh
ros2 daemon stop
bash run_A.sh

# Terminal 1
python3 qos_pub.py --ros-args \
  -p reliability:=reliable -p durability:=volatile

# Terminal 2
python3 qos_sub.py --ros-args \
  -p reliability:=reliable -p durability:=volatile

# Terminal 3
ros2 topic info /qos_demo/stream --verbose
```

---

## Expected results

- PUB `seq` increases
- SUB `recv_total` increases, `measured_hz ≈ 10`
- Verbose info shows matching RELIABLE / VOLATILE on both endpoints

---

## Actual results

See [`../assets/A_compatible.log`](../assets/A_compatible.log) and [`../assets/A_topic_info.txt`](../assets/A_topic_info.txt).

| Observation | Result |
|---|---|
| SUB receives? | Yes — `recv_total` climbed |
| `last_seq` advances? | Yes |
| QoS match in `--verbose`? | Yes (RELIABLE / VOLATILE both sides) |

---

## Conclusion

Compatible Request≤Offer unlocks the data path. This is the control case for Investigations B and C.
