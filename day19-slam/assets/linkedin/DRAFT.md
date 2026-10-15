# LinkedIn draft — Day 19

**Hero:** [`01-hero.jpg`](01-hero.jpg)

**Question:** What actually happens when a robot "builds a map"?

---

A robot draws the room with a laser, one sweep at a time.

That is Day 19 of #30DaysOfROS2.

What actually happens when a robot "builds a map"?

A LiDAR hands you distances. A fan of beams. Then another fan, from a few centimeters away.

I drove a robot across a 4 m square and painted the same 16 sweeps three ways.

The real pose drew one clean square. 322 occupied cells. The beams landed on the walls.

The wheels added 3 cm of extra forward motion every step. After 15 steps they were 45 cm ahead of the truth. The same walls were stored again in the wrong place: 553 occupied cells, and the square grew a second edge.

Then I slid each new sweep until its hits sat on the walls already drawn, and painted that. Final pose error fell from 45.0 cm to 3.6 cm. The square was single again.

The laser was never the problem. The pose used to place the sweep was.

If the map looks wavy, the sweeps never lined up. The picture was drawn on top of drift.

Day 19 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day19-slam

#ROS2 #SLAM #Robotics #LiDAR #BostonDynamics #NVIDIARobotics
