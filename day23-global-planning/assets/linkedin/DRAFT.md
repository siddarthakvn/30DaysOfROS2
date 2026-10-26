# LinkedIn draft — Day 23

**Question:** How does a robot choose a path from A to B?

**Hero:** `assets/linkedin/01-hero.jpg`

Numbers below are from `./run_smoke.sh` on this machine. Domain 230.

---

The straight line was a wall.

The planner still had to choose a path.

That is Day 23 of #30DaysOfROS2.

How does a robot choose a path from A to B?

A to B is 7.00 m in a straight line. Ten samples of that line sit on a wall. The line is not a path.

Dijkstra spreads by travel cost alone. It opened 3989 of 4284 free cells. The path it brought back is 61 poses and 7.49 m.

A* adds one guess: the straight-line distance still left. It opened 832 cells. The path is 7.49 m again.

Same length. The cell lists differ, because a grid can hold more than one route of that length. The search is what changed. Dijkstra filled the room. A* walked toward B.

A path is a line of poses. The wheels have not moved yet.

Day 23 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day23-global-planning

#ROS2 #Nav2 #Robotics #Navigation #PathPlanning #BostonDynamics #NVIDIARobotics
