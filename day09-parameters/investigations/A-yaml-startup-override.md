# Investigation A — YAML Startup Override

## Engineering question

Can a YAML params file override a code default at startup without rebuilding the node?

---

## Hypotheses

**H6:** YAML `max_velocity: 0.5` → stored/effective max is **0.5**, not the code default **1.0**.

---

## Setup

| | |
|---|---|
| Code default | `max_velocity = 1.0` |
| YAML | [`../config/cruise_limit.yaml`](../config/cruise_limit.yaml) → `0.5` |
| Request | `request_vx = 1.5` (will be clamped) |

```bash
cd day09-parameters/ros2_nodes
source ./env.sh
python3 velocity_governor.py --ros-args --params-file ../config/cruise_limit.yaml
```

---

## Expected

| Metric | Expect |
|---|---|
| `STORED max_velocity` | 0.5 |
| `TICK out` | 0.5 |

---

## Actual results

Evidence: [`../assets/A.log`](../assets/A.log)

| Metric | Observed |
|---|---|
| Startup CONFIG | `max_velocity=0.500` |
| STORED / EFFECTIVE | **0.500** |
| TICK `out` | **0.500** (request 1.5 clamped) |

---

## Conclusion

**H6 supported.** Startup YAML configures the node without changing code.
