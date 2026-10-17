# Day 20 — Interview questions

1. A robot already has an occupancy grid. What is still missing before it can say where it is?

2. Where does the first cloud of guesses come from when nobody gives an initial pose? Where does it come from when RViz sends a 2D pose estimate?

3. Why can the wheels move every particle and still leave the robot lost?

4. A rectangular kitchen gives two poses that explain the first scan. What kind of later motion breaks that tie?

5. After resampling, every particle is a copy of a pose 0.5 m away from the truth. Why can a filter with no process noise stay wrong forever?

6. Why does AMCL publish the correction as `map` → `odom` rather than rewriting `odom` → `base_link` on every laser hit?
