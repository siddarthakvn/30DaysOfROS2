# LinkedIn draft — Day 15

**Hero:** [`01-hero.jpg`](01-hero.jpg)

**Question:** My simulated LiDAR was perfect. Why is that a problem?

---

My simulated LiDAR was perfect. Why is that a problem?

A LiDAR shoots many light beams and measures how far each one travels before it hits something. Those distances are the scan.

In the real world, a beam is a little off every time. In my simulation, it was exact.

I parked the sensor in front of a wall.

- One beam said 1.9006 m
- The next scan, that same beam said 1.9006 m again
- Largest change across the scan: 0.000 m

A real beam would move a little. The wall would not.

With a small amount of noise on the same wall, the scan rate stayed about 5 Hz and the biggest jump between scans was 0.223 m. The wall was still 1.90 m away.

Slowing the sensor from 5 Hz to 1 Hz did not add that error. It only meant a new scan arrived once a second.

A scan has three settings, and they are not the same thing.

- Error: how much each beam wobbles
- Speed: how often a fresh set of beams arrives
- Beam count: how many directions it looks

Before you trust the simulation, add a little error, match the real sensor’s speed and beam count, and test the stop rule again. If the robot jitters, it was only safe because every beam was a tape measure.

Day 15 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day15-simulated-sensors

#BostonDynamics #NVIDIARobotics #ROS2 #Gazebo #Robotics
