# Investigation B — Queue Depth vs Staleness (Hero)

## Engineering question

Is a bigger queue “safer,” or does it make the robot act on a stale world?

---

## Why this investigation exists

Default ROS 2 topic QoS uses `KEEP_LAST` with depth **10**. That sounds comforting (“room for 10 messages”). Under a sensor firehose it can mean:

> You faithfully process the **past** while the present has already moved on.

Depth **1** is the opposite policy: drop aggressively, stay near now.

This is the investigation meant to feel like a real autonomy review: **latency as a function of queue policy**.

---

## Hypothesis

Same overload both runs (30 Hz publish, 100 ms process, RELIABLE). Only depth changes.

1. **B1 depth=1:** Large sequence gaps; **`age_frames` stays low** (near the live frontier).
2. **B2 depth=10:** Gaps still occur when saturated; **`avg_age_frames` / `max_age_frames` higher** than B1 — FIFO among up to 10 cached samples means older frames are processed before newer ones.

**Falsifies H2/H3 if** depth 1 and 10 show the same age distribution, or depth 10 consistently behaves like newest-first (LIFO) among cached samples.

---

## Experimental design

| | B1 Freshness | B2 Backlog |
|---|---|---|
| Publish Hz | 30 | 30 |
| `process_ms` | 100 | 100 |
| Reliability | RELIABLE (both ends) | same |
| History | KEEP_LAST | KEEP_LAST |
| **Depth (both ends)** | **1** | **10** |

Publisher and subscriber depths **must match**.

---

## Environment

Same as Investigation A: Humble, `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`, `ROS_DOMAIN_ID=30`, `ros2_nodes/`.

---

## Procedure

```bash
cd day03-topics-and-backpressure/ros2_nodes
source ./env.sh
ros2 daemon stop
bash run_B.sh   # prints commands
```

### B1 — depth 1

```bash
# Terminal 1
python3 frame_camera_pub.py --ros-args \
  -p publish_hz:=30.0 -p depth:=1 -p reliability:=reliable

# Terminal 2
python3 slow_inference_sub.py --ros-args \
  -p process_ms:=100 -p depth:=1 -p reliability:=reliable
```

### B2 — depth 10

Same with `depth:=10` on **both** nodes.

Run each ≥15–20 s. Compare `gap`, `avg_age_frames`, `max_age_frames` from `STATS` lines.

---

## Expected results

| Run | Gaps | Age |
|---|---|---|
| B1 depth=1 | Large / frequent | Low (fresh) |
| B2 depth=10 | Present when saturated | Higher (stale backlog), order-of-magnitude near depth |

Conceptual sketch (not data):

```text
age_frames  ▲
            │          ●●●●  depth=10
            │     ●●●●
            │  ●●
            │ ●              depth=1
            └────────────────────────►  time
```

---

## Actual results

Observed on 2026-09-15 (same host/RMW/domain as Investigation A). Overload fixed: 30 Hz publish, `process_ms=100`, RELIABLE. Only depth varied.

| Metric | B1 depth=1 | B2 depth=10 |
|---|---|---|
| process_hz | ~9.7 | ~9.8 |
| typical gap | ~1–2 | ~2 |
| avg_age_frames | **~3.0** | **~12.0** |
| max_age_frames | **3** | **12** |

Note: an early B2 attempt looked like freshness mode again (age~2) — likely mismatched depth or too-short run. Confirmed B2 after verifying both nodes logged `KEEP_LAST depth=10` and running ~20 s.

---

## Evidence

- [`../assets/B1_depth1.png`](../assets/B1_depth1.png)
- [`../assets/B2_depth10.png`](../assets/B2_depth10.png)

---

## Analysis

Publish and process rates stayed the same (~30 / ~10). **Age** was the signal that changed. Depth 1 kept processed frames near live (age ≈ sleep-time advance at 30 Hz). Depth 10 allowed a backlog so callbacks acted ~12 frames behind — FIFO among cached samples, not “always newest.” Larger depth did not make the robot smarter; it made it **later**.

---

## Conclusion

History depth is a **staleness budget**. Prefer depth **1** (or small) for closed-loop / live perception. Prefer larger depth only when you intentionally want to absorb bursts and can tolerate acting on older samples (e.g. some logging paths).
