# LinkedIn draft — Day 17

**Hero:** [`01-hero.jpg`](01-hero.jpg)

**Question:** Why does my robot oscillate around the target angle?

---

Why does my robot oscillate around the target angle?

It is not missing the angle. It is still turning when it gets there.

The usual fix is to turn harder when the gap is bigger. That is the P in PID. Far from the target, the command is strong. At the target, the gap is zero, so that command is zero too.

A real heading does not stop the instant the command does. On the way in, the robot has already built up turn speed. Nothing in P asked it to slow down before arrival. So it coasts past the angle. The gap flips to the other side. P turns the other way. The same thing happens on the way back.

That is the wobble.

I pointed the same controller at 90°.

- P only, and the heading remembers its turn speed: it crossed the target 5 times and finished near 176°, not on 90°.
- The same P, plus a brake on that turn speed: it stopped on 90.00° and never crossed.
- The same P, but the turn speed is forced to match the command immediately: it also stopped on 90°. No stored speed, no swing.

D is the term that notices the gap closing fast and eases off before the crossing. Raising P alone, with no D, is how the swing gets worse.

I is a different job. It pushes a gap that will not go away. It is not what made this heading hunt back and forth.

Day 17 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day17-pid

#BostonDynamics #NVIDIARobotics #ROS2 #Robotics
