# Investigation C — Sensor QoS Contrast (Light)

## Engineering question

Why does ROS talk about a **sensor data** style QoS (smaller depth, best effort)? Is overload loss only “queue full,” or can reliability change what we see?

---

## Why this investigation exists

History overflow and reliability are **different loss paths**:

| Path | Mechanism |
|---|---|
| History (`KEEP_LAST` full) | Oldest unread samples overwritten in the endpoint cache |
| Reliability (`BEST_EFFORT`) | Samples may be lost on the wire / under middleware stress |
| Lifespan / mismatch | Out of scope today (Day 07) |

On **localhost**, BEST_EFFORT often shows **little extra** loss versus RELIABLE. Recording that honestly is a better engineering outcome than forcing a dramatic network story.

---

## Hypothesis

Fixed: 30 Hz publish, `process_ms=100`, KEEP_LAST **depth=5** (sensor-like depth).

1. **C1 RELIABLE** and **C2 BEST_EFFORT** both show history-overflow-style gaps under overload.
2. On one host, gap/age stats may be **similar**. That supports “separate paths; network path idle here.”
3. If C2 shows clearly more loss, note it as possible BEST_EFFORT/RMW behavior — do **not** expand into full Day 07.

---

## Experimental design

| | C1 | C2 |
|---|---|---|
| Depth (both) | 5 | 5 |
| Reliability (both) | **reliable** | **best_effort** |
| Rates | 30 Hz / 100 ms | same |

QoS must match on both ends or you get no connection (confounder).

---

## Environment

Same pin: Humble, Fast DDS, `ROS_DOMAIN_ID=30`.

---

## Procedure

```bash
cd day03-topics-and-backpressure/ros2_nodes
source ./env.sh
ros2 daemon stop
bash run_C.sh
```

### C1

```bash
python3 frame_camera_pub.py --ros-args \
  -p publish_hz:=30.0 -p depth:=5 -p reliability:=reliable

python3 slow_inference_sub.py --ros-args \
  -p process_ms:=100 -p depth:=5 -p reliability:=reliable
```

### C2

```bash
python3 frame_camera_pub.py --ros-args \
  -p publish_hz:=30.0 -p depth:=5 -p reliability:=best_effort

python3 slow_inference_sub.py --ros-args \
  -p process_ms:=100 -p depth:=5 -p reliability:=best_effort
```

Confirm matching QoS:

```bash
ros2 topic info /perception/frames -v
```

---

## Expected results

- Both runs: overload gaps with depth 5.
- Localhost: C1 ≈ C2 is a **valid** result.
- Do not claim Wi-Fi loss characteristics from this host-only test.

---

## Actual results

Observed on 2026-09-15. Fixed: 30 Hz, `process_ms=100`, KEEP_LAST **depth=5**. Only reliability varied (matched on both ends).

| | C1 RELIABLE | C2 BEST_EFFORT |
|---|---|---|
| process_hz | ~10 | ~9.7 |
| avg / max age_frames | ~7 / ~7 | **7.0 / 7** |
| gaps | yes (`gap≈2`) | yes (`gap≈2`) |
| Difference? | — | **No meaningful difference on localhost** |

Age ~7 sits between B1 (~3) and B2 (~12), consistent with depth=5 as a medium staleness budget.

---

## Evidence

- [`../assets/C1_reliable_depth5.png`](../assets/C1_reliable_depth5.png)
- [`../assets/C2_best_effort_depth5.png`](../assets/C2_best_effort_depth5.png)

---

## Analysis / conclusion

History overflow dominated. On one host, switching RELIABLE → BEST_EFFORT did not add a clear second loss signature. This experiment **cannot** claim Wi-Fi / multi-machine BEST_EFFORT behavior — only that reliability is a **separate** path from queue depth, and depth was the lever that moved `age_frames` today.
