# LinkedIn draft — Day 22

**Question:** Why was my robot avoiding obstacles that didn't exist?

**Hero:** `assets/linkedin/01-hero.jpg`

Numbers below are from `./run_smoke.sh` on this machine. Domain 220.

---

The room was empty.

The planner still went the long way around a cushion.

That is Day 22 of #30DaysOfROS2.

Why was my robot avoiding obstacles that didn't exist?

The straight line from the robot to the goal is 4.40 m. The floor on that line is bare. One old laser cell is still in the global costmap. It was marked from 2.325 m away. The robot is now 3.225 m away, and the clearing ray stops at 3.0 m, so the cell stays.

Live scan. The cell is free. The path is 4.40 m and drives straight through that spot.

Obstacle layer only. The cell is lethal. The path is 4.44 m and steps one cell aside. The center comes within 0.050 m. The robot body is 0.22 m in radius, so the body would still cover that cell.

Then the inflation layer. The same one cell becomes 60 inscribed cells and 316 more with a cost. The path is 4.90 m. It bends 0.57 m off the line and stays 0.552 m away from the phantom. That distance is the inflation radius. The disk is empty floor.

The local costmap is a 3 m window around the robot. The phantom sits outside it. The planner still followed the global map.

A costmap is the room the planner believes. Clear the cell, and the straight path comes back.

Day 22 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day22-costmaps

#ROS2 #Nav2 #Robotics #Navigation #BostonDynamics #NVIDIARobotics
