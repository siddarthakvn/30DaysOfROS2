# Day 12 — Interview Questions

1. **Why does a robot need `base_link`, `odom`, and `map`?**  
   Body frame, continuous local odometry, and global (possibly jumpy) localization — three contracts, one TF tree: `map`→`odom`→`base_link`.

2. **What is continuous vs discontinuous in REP-105?**  
   `odom`→`base_link` must evolve smoothly. `map` poses may jump when localization corrects.

3. **Why doesn’t localization publish `map`→`base_link`?**  
   Each frame has one parent. Publishing `map`→`odom` keeps odometry’s edge continuous while still correcting the global chain.

4. **What breaks if both `map` and `odom` parent `base_link`?**  
   An invalid / split TF tree — lookups fail with unconnected trees (Day 12 Investigation C).

5. **Where should a velocity controller look?**  
   Prefer a continuous frame (`odom` / `base_link` relative motion). Avoid feeding discrete map jumps into low-level control.

## One-liner

**Body. Drift. Truth. — `base_link`, `odom`, `map` chained so control and localization don’t destroy each other.**
