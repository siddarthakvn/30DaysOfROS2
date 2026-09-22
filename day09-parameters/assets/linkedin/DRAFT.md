# LinkedIn draft — Day 09

**Status:** Ready after public reveal.

**Question:** How can a running ROS 2 robot change its behavior without changing its code?

**Day 10 teaser:** How do you bring up an entire robot with one command?

---

## Hero image

[`01-hero.png`](01-hero.png) — bright sunlit lab, robot + tuning knobs, cream text panel:
**“Tune it live.”** / **No rebuild. No restart.**

---

## Copy-paste post

Your robot is already running.

You need a new max speed.
A tighter threshold.
A different gain.

Do you stop the robot, edit code, rebuild, and relaunch?

In ROS 2, you usually shouldn’t have to.

That’s what parameters are for.

Not a global ROS 1–style parameter server.
A setting that belongs to a node.

I built a velocity governor:

• request = 1.5 m/s
• max_velocity starts at 1.0 → out = 1.0
• then live: `ros2 param set /velocity_governor max_velocity 0.3`
• out drops to 0.3 — same process, no restart

Then I tried something unsafe:

`ros2 param set … max_velocity 10.0`

Rejected.
Stored value stayed 1.0.
The robot kept the old policy.

So:

Parameter = configuration  
Topic = streams / commands  
Service = short request  
Action = long goal  

And the interview line:

Parameters are per-node settings.
A set only changes the robot if the node accepts it and actually uses the new value.

Settings, not spells.

Day 09 / #30DaysOfROS2

Evidence:
https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day09-parameters

#ROS2 #Robotics #Parameters #RoboticsEngineering #30DaysOfROS2
