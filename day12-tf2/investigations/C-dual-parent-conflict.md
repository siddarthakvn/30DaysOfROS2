# Investigation C — Dual-parent conflict

## Hypothesis

**H3:** Publishing both `map`→`base_link` and `odom`→`base_link` breaks the single-parent TF tree.

---

## Setup

```bash
python3 ros2_nodes/conflict_demo.py --ros-args -p run_sec:=6.0
```

- 0–2s: only `odom`→`base_link`  
- ≥2s: also `map`→`base_link` (illegal second parent)

---

## Actual results

Evidence: [`../assets/C.log`](../assets/C.log)

| Check | Observed |
|---|---|
| Illegal edge added | logged at t=2s |
| After conflict | `Could not find a connection between 'odom' and 'base_link' because they are not part of the same tree. Tf has two or more unconnected trees.` |
| `lookup_fail` | **120** (vs intermittent early misses) |
| `map`→`odom` edge | **NO** (never published — the REP-105 bridge is missing) |

---

## Conclusion

**Supported.** Intuition (“both worlds parent the robot”) fights TF’s tree rule. Localization must publish `map`→`odom`, not a second parent onto `base_link`.
