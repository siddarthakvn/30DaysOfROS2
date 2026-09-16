# Investigation A — The Firehose Does Not Wait

## Engineering question

When inference is slower than the camera, does ROS 2 apply backpressure — or does the world keep flooding you?

---

## Why this investigation exists

A common wrong mental model:

> “If my callback is slow, the publisher will slow down.”

Topics are not a request/reply credit protocol. This investigation checks whether the commanded publish rate survives compute starvation on the subscriber.

---

## Hypothesis

1. **A0 (keep-up):** With `process_ms` small enough to match 30 Hz, processed frame ids stay nearly continuous; `age_frames` stays low.
2. **A1 (overload):** Publisher measured rate stays ~30 Hz. Subscriber process rate ≈ `1000/process_ms`. Frame **gaps** appear. Age rises then saturates (bounded by `KEEP_LAST` depth), rather than the publisher waiting.

**Falsifies H1 if** publish rate collapses to match the subscriber under overload.

---

## Experimental design

| | A0 Baseline | A1 Overload |
|---|---|---|
| Topic | `/perception/frames` | same |
| Msg | `std_msgs/Int32` (frame id) | same |
| Publish Hz | 30 | 30 |
| `process_ms` | **25** | **100** |
| QoS (both ends) | KEEP_LAST depth **10**, RELIABLE, VOLATILE | same |

Frontier watcher: depth-1 subscription on the subscriber node (never sleeps) so `age_frames = live_seq - processed_seq` stays meaningful while the slow callback blocks.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| RMW | `RMW_IMPLEMENTATION=rmw_fastrtps_cpp` |
| Domain | `ROS_DOMAIN_ID=30` |
| Working directory | `ros2_nodes/` |

---

## Procedure

```bash
cd day03-topics-and-backpressure/ros2_nodes
source ./env.sh
ros2 daemon stop
ros2 doctor --report | grep -i rmw

# Print this sheet anytime:
bash run_A.sh
```

### A0 — keep up

**Terminal 1**

```bash
source ./env.sh
python3 frame_camera_pub.py --ros-args \
  -p publish_hz:=30.0 -p depth:=10 -p reliability:=reliable
```

**Terminal 2**

```bash
source ./env.sh
python3 slow_inference_sub.py --ros-args \
  -p process_ms:=25 -p depth:=10 -p reliability:=reliable
```

Run ≥15 s. Note `gap`, `age_frames`, `PUB measured_hz`, `STATS process_hz`.

### A1 — overload

Same as A0 but `process_ms:=100` on the subscriber.

Optional short inspect (CLI adds another subscription — prefer node logs as ground truth):

```bash
source ./env.sh
ros2 topic info /perception/frames -v
ros2 topic hz /perception/frames
```

---

## Expected results

| Run | Expect |
|---|---|
| A0 | Few/no gaps; process_hz ≈ publish_hz; low `age_frames` |
| A1 | Pub ~30 Hz unchanged; process ~10 Hz; `gap > 0`; age grows then saturates near depth scale |

---

## Actual results

Observed on 2026-09-15 (Ubuntu 22.04, Humble, `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`, `ROS_DOMAIN_ID=30`).

| Expectation | Observed |
|---|---|
| A0 keep-up | **Confirmed.** Sub: `process_hz=30.0`, `gap=0`, `age_frames=0`, `gaps_cumulative=0`. Pub held `measured_hz=30.0`. |
| A1 pub rate held | **Confirmed.** Pub stayed `measured_hz=30.0` while sub processed at ~10 Hz — no app-level backpressure. |
| A1 gaps + bounded age | **Confirmed.** Sub: `process_hz≈9.8`, `gap≈2–3`, `avg_age_frames≈12`, `max_age_frames=12` (saturates near depth-10 scale; live advances ~3 frames during the 100 ms sleep). |

---

## Evidence

- A0: terminal logs (paste in session; optional screenshot not filed)
- A1: [`../assets/A1_overload_gaps.png`](../assets/A1_overload_gaps.png)
- RMW pin confirmed via `ros2 doctor` → `middleware name: rmw_fastrtps_cpp` before runs

---

## Analysis

Expected vs observed matched. The publisher did **not** slow to the subscriber’s rate. Surplus frames became **gaps** after the subscription history filled; processed frames sat ~12 behind live with depth 10. Age slightly above depth is consistent with the frontier moving during `process_ms=100` at 30 Hz (~3 frames), not unbounded growth.

---

## Conclusion

Under overload, ROS 2 topics do **not** apply app-level backpressure to the publisher. The sensor firehose keeps its rate; the slow consumer buffers then drops oldest (`KEEP_LAST`) and processes a stale window.
