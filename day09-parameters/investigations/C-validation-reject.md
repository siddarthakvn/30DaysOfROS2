# Investigation C — Validation Reject

## Engineering question

Can a node refuse an unsafe parameter change and keep the previous setting?

---

## Hypotheses

**H4/H5:** Out-of-range `max_velocity=10.0` is rejected by the on-set callback; stored value stays `1.0`.

---

## Setup

| | |
|---|---|
| Allowed range | `[0.0, 2.0]` |
| Attempt | `ros2 param set /velocity_governor max_velocity 10.0` |

```bash
cd day09-parameters/ros2_nodes
source ./env.sh

python3 velocity_governor.py --ros-args \
  -p max_velocity:=1.0 -p request_vx:=1.5 -p apply_mode:=live -p run_sec:=10.0

ros2 param set /velocity_governor max_velocity 10.0
ros2 param get /velocity_governor max_velocity
```

---

## Expected

| Check | Expect |
|---|---|
| CLI set | fails with range reason |
| `get` | still 1.0 |
| Logs | `PARAM_REJECT` |
| TICKs after | still `out=1.000` |

---

## Actual results

Evidence: [`../assets/C.log`](../assets/C.log)

| Check | Observed |
|---|---|
| CLI set | **Setting parameter failed: max_velocity must be in [0.0, 2.0]** |
| CLI get | **Double value is: 1.0** |
| Log | `PARAM_REJECT … value=10.0` |
| SUMMARY | `STORED=1.000`, `rejects=1`, `accepts=0` |
| TICKs after reject | still `max=1.000 out=1.000` |

---

## Conclusion

**H4/H5 supported.** On-set validation is a real gate: bad config does not become robot policy.
