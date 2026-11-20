# LinkedIn draft — Day 30

**Question:** What breaks when you scale one ROS 2 robot to three?

**Hero:** `assets/linkedin/01-hero.jpg`

Numbers below are from `./run_smoke.sh` on this machine (`ROS_DOMAIN_ID=224`), launching three robots (`r1`, `r2`, `r3`) toward one target at `(2.50, 3.00)`.

---

I sent one target. All three robots broke in two different ways.

That is Day 30 — the final day of #30DaysOfROS2.

What breaks when you scale one ROS 2 robot to three?

Everything you named with a leading slash, and every goal you broadcast without a coordinator.

Three robots launched on Domain 224: r1 at 1.500 m from the target, r2 at 2.500 m, r3 at 3.202 m.

Run 1: hardcoded /cmd_vel, /odom, and base_link. Even inside /r1, /r2, and /r3 namespaces, leading slashes bypassed isolation. /cmd_vel had 3 publishers and 3 subscribers. Each base took 213 conflicting commands, wandered nearly 5 m off course (14.840 m total travel), and 0 of 3 reached the goal.

Run 2: relative cmd_vel and odom plus r1/base_link, r2/base_link, r3/base_link. Every robot got 1 publisher and 1 subscriber on its own wheels — and all 3 sprinted to the exact same coordinate, piling up 3.3 cm apart after 7.091 m of fleet travel.

Run 3: namespaces plus fleet_coordinator. The coordinator scored distances (1.500 m, 2.500 m, 3.202 m) and sent /r1/goal only. r1 drove 1.464 m to the target in 35 commands. r2 and r3 stayed parked at 0.000 m with 0 commands.

Namespaces give each robot its own body. A coordinator gives the fleet a brain.

Day 1 started with two nodes finding each other without a master. Day 30 ends with three robots sharing one graph without stealing each other's wheels.

30 questions. 30 experiments. Core to autonomy.

Day 30 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day30-multi-robot

#ROS2 #MultiRobot #Nav2 #Robotics #Autonomy #RoboticsEngineering
