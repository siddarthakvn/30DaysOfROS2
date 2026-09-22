# Investigation B — Runtime `ros2 param set` (Hero)

## Engineering question

Can you change robot behavior while the node keeps running — without a rebuild or restart?

---

## Hypotheses

**H2:** Mutable params can be set at runtime.

**H3:** With `apply_mode=live`, TICKs use the new `max_velocity` after a successful set.

---

## Setup

| | |
|---|---|
| Start | `max_velocity=1.0`, `request_vx=1.5`, `apply_mode=live` |
| Live set | `ros2 param set /velocity_governor max_velocity 0.3` |

```bash
cd day09-parameters/ros2_nodes
source ./env.sh

python3 velocity_governor.py --ros-args \
  -p max_velocity:=1.0 -p request_vx:=1.5 -p apply_mode:=live -p run_sec:=10.0

# other terminal
ros2 param set /velocity_governor max_velocity 0.3
ros2 param get /velocity_governor max_velocity
```

---

## Expected

| Phase | Expect |
|---|---|
| Before set | `out=1.000` |
| CLI set | successful |
| After set | `PARAM_ACCEPT`, then `out=0.300` |

---

## Actual results

Evidence: [`../assets/B.log`](../assets/B.log)

| Phase | Observed |
|---|---|
| Before | `out=1.000` |
| `ros2 param set` | **Set parameter successful** |
| `ros2 param get` | **Double value is: 0.3** |
| Accept log | `PARAM_ACCEPT … value=0.300` |
| After | `out=0.300` |
| SUMMARY | `STORED=0.300`, `accepts=1`, node never restarted |

---

## Analysis

The parameter service accepted `0.3`. Because the timer **re-reads** `max_velocity` each tick (`apply_mode=live`), commanded output dropped immediately. Same process, same code — only configuration changed.

---

## Conclusion

**H2 and H3 supported.** Runtime parameters can retune behavior without restart when the node applies the new value.
