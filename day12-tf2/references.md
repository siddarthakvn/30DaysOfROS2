# Day 12 — References

## Primary

1. **About Tf2** (ROS 2 Humble)  
   https://docs.ros.org/en/humble/Concepts/Intermediate/About-Tf2.html  
   - Time-buffered transform tree; lookup between frames

2. **REP-105 — Coordinate Frames for Mobile Platforms**  
   https://reps.openrobotics.org/rep-0105/  
   - Semantics of `base_link`, `odom`, `map`  
   - Required topology `map` → `odom` → `base_link`  
   - Who publishes which edge

3. **TF2 tutorials** (Humble)  
   https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Tf2-Main.html

4. **Nav2 — State Estimation** (REP-105 in navigation context)  
   https://docs.nav2.org/getting_started/navigation_concepts/state_estimation.html

## Related series days

- Day 11 — URDF / body frames under `base_link`
- Day 13 — who publishes the transform tree
- Day 16–20 — odometry, EKF, SLAM, AMCL fill these edges
