# LinkedIn draft — Day 24

**Question:** What happens when an obstacle suddenly appears on the planned path?

**Hero:** `assets/linkedin/01-hero.jpg`

Numbers below are from `./run_smoke.sh` on this machine. Domain 231.

---

The path was already drawn.

Then a box appeared on it.

That is Day 24 of #30DaysOfROS2.

What happens when an obstacle suddenly appears on the planned path?

The line from start to goal is 6.00 m. It was drawn on an empty floor. Then the box showed up in the middle of it.

Follow that line. The robot stops 0.010 m short of the box and 3.680 m short of the goal. The plan is still the old line.

Let the local controller steer, up to 1.05 m off the line. The plan stays 6.00 m and still runs through the box. The body goes around it, stays 0.315 m clear, and finishes 0.181 m from the goal. No new plan.

Make the box 4 m wide. That steer has nowhere to stand. It stops. One replan draws a new line, 6.70 m, 1.75 m off the old center. The body follows it and finishes 0.195 m from the goal.

A new obstacle is a local problem first. It becomes a new global path when the local steer can no longer pass.

Day 24 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day24-dynamic-obstacles

#ROS2 #Nav2 #Robotics #Navigation #BostonDynamics #NVIDIARobotics
