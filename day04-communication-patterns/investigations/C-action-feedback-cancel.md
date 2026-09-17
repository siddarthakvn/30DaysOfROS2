# Investigation C — Action feedback + cancel

## Hypothesis (H1, H2)

`/turtle1/rotate_absolute` provides:

- goal accept/reject
- feedback (`remaining`)
- terminal result
- cancel → `CANCELED`

This is the correct contract for a long, preemptable motion.

## Setup

- `turtlesim_node` (built-in action server)
- `action_cancel_demo.py` for reproducible cancel (C1)

## Procedure

See `ros2_nodes/run_C.sh`.

### C0 — Run to completion

```bash
ros2 action send_goal --feedback /turtle1/rotate_absolute \
  turtlesim/action/RotateAbsolute "{theta: 3.14}"
```

### C1 — Cancel mid-goal

```bash
python3 action_cancel_demo.py --ros-args \
  -p theta:=3.14 -p cancel_after_sec:=1.0
```

## Expected

- Feedback `remaining` updates before the result
- Successful run ends `SUCCEEDED` with `delta`
- Cancelled run reports `CANCELED`

## Actual

Observed 2026-09-16 · Fast DDS · domain 40 · logs under `assets/`.

| Run | Observation | Evidence |
|---|---|---|
| C0 | Goal accepted with UUID; continuous `Feedback: remaining` from ~3.14 → ~0; `Result: delta≈-3.136`; **`Goal finished with status: SUCCEEDED`**. Final pose `theta≈3.136`. | `assets/C0_action_feedback_success.log` |
| C1 | Goal accepted; 64 feedback msgs; cancel at 1.0 s (`return_code=0`, goal in `goals_canceling`); **`Terminal status=CANCELED (5) delta≈-1.008`**. Pose stopped at `theta≈1.024` (not π). | `assets/C1_action_cancel.log` |

Note: an earlier CLI attempt with `theta: 6.28` from `theta=0` finished instantly (≈ full turn identity). Use `theta: 3.14` for a visible mid-flight window. Automated SIGINT on `ros2 action send_goal` did not reliably cancel under scripting — the Python cancel client is the reproducible path.

## Analysis

H1/H2 hold on the Action path: mid-flight **feedback** is first-class (C0/C1), and cancel produces an explicit **`CANCELED`** terminal status with a partial `delta` (C1). That is the opposite of B1 (client gone, server still finishes) and A1 (no goal lifecycle at all).
