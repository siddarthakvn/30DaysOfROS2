# Day 19 — Interview questions

1. A robot publishes `/scan` and someone says "the map is the latest scan." What is missing?

2. Why does an occupancy grid mark cells *along* a beam as free, and only the last cell as occupied?

3. Wheel odometry is off by 3 cm every step. You still paint every scan. What does the wall look like after 15 steps, and why?

4. Scan matching slides a new scan until it agrees with the map. Why can a long, straight wall not tell you that the robot moved *along* that wall?

5. This day's matcher only searches ±10 cm. What happens on the step where the wheel error is 30 cm?

6. Why is `/map` usually transient-local, while a live `/scan` is not?
