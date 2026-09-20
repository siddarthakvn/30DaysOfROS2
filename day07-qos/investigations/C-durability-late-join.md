# Investigation C — Durability and Late Join

## Engineering question

How does durability change late-joiner behavior, and when does it block communication entirely?

---

## Hypotheses

**H4:** VOLATILE publisher + TRANSIENT_LOCAL subscriber → no communication.

**H5:** TRANSIENT_LOCAL on **both** sides can deliver retained samples to a late joiner (within depth).

---

## Setup

| Case | Pub durability | Sub durability | Join time |
|---|---|---|---|
| C1 | VOLATILE | VOLATILE | late (~3 s) |
| C2 | TRANSIENT_LOCAL | TRANSIENT_LOCAL | late (~3 s) |
| C3 | VOLATILE | TRANSIENT_LOCAL | any |

Use `reliability:=reliable` and `publish_hz:=2.0` for easier reading of sequence numbers.

---

## Procedure

```bash
cd day07-qos/ros2_nodes
source ./env.sh
ros2 daemon stop
bash run_C.sh
```

Follow the printed C1 / C2 / C3 commands. For late join, start the publisher first, wait ~3 seconds, then start the subscriber.

---

## Expected results

| Case | Expect |
|---|---|
| C1 | Late sub gets near-live `last_seq`, not a full replay from 1 |
| C2 | Late sub can see older retained seqs (within depth) |
| C3 | `recv_total=0` (durability mismatch) |

---

## Actual results

See [`../assets/C_durability.log`](../assets/C_durability.log) and [`../assets/C_topic_info.txt`](../assets/C_topic_info.txt).

| Case | Observation |
|---|---|
| C1 late VOLATILE | First reported `last_seq=7` (near live, not 1) |
| C2 late TRANSIENT_LOCAL both | First report `recv_total=7 last_seq=7` at ~7 Hz burst — retained history delivered |
| C3 mismatch | `recv_total` stayed 0 |

---

## Conclusion

Durability is not “nice to have.”
It decides late-join semantics **and** can refuse the match entirely.
Latch-like behavior needs **both** sides TRANSIENT_LOCAL (typically with RELIABLE).
