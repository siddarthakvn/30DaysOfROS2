# LinkedIn draft — Day 16

**Hero:** [`01-hero.jpg`](01-hero.jpg)

**Question:** How does wheel rotation become robot position?

---

How does wheel rotation become robot position?

The wheels do not report where the robot is. They only report how fast each wheel is turning.

A differential-drive robot has two driven wheels. It can roll forward and it can spin. It cannot slide sideways. A sideways command does nothing, because neither wheel can push the body to the side.

Two wheel speeds become one body motion:

- Both wheels the same way: the robot drives straight
- Same speed, opposite ways: it spins in place and the center barely moves
- One wheel faster: it drives an arc

Then you add that motion up, a small step at a time.

- Forward speed, times time, moves it along whatever direction it is facing
- The spin changes which way "forward" points
- After a turn, the next straight drive no longer follows the old line
- That running total is `x`, `y`, and yaw

I measured that sum.

- Both wheels the same way for 2 seconds: `x = 1.000 m`, yaw `0°`
- Wheels opposite ways: the center stayed at `0, 0`, and the heading turned `90°`
- The same drive after that turn: `y = 1.000 m`, and the body still had no sideways speed
- Same wheel spin, but the wheel in the formula was 10% too big: the reported distance became `1.100 m`

That total is odometry. It lives in the `odom` frame: a smooth local guess of where the robot is since it started. It is not a map. Nothing in the sum looked at a wall.

A wrong wheel size makes the guess wrong even when the wheels did not spin any faster. Do that on every leg of a square and the end does not meet the start.

A short run on flat ground can look perfect. That does not mean the wheels are telling the truth. It means the error has not had time to pile up yet.

Day 16 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day16-odometry

#BostonDynamics #NVIDIARobotics #ROS2 #Gazebo #Robotics
