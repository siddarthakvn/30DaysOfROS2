# LinkedIn draft — Day 12

**Hero:** [`01-hero.png`](01-hero.png)

**Question:** Why does a robot need `base_link`, `odom`, and `map`?

---

Your robot can be in three places at once.

Not metaphorically.
Structurally.

**`base_link`** — where the body is  
**`odom`** — where dead reckoning thinks you are  
**`map`** — where the world says you are  

Day 12 of #30DaysOfROS2 asks:

**Why does a robot need `base_link`, `odom`, and `map`?**

Because one frame cannot do three jobs.

`base_link` is bolted to the robot.
Sensors hang from it.
Wheels hang from it.

`odom` is smooth.
No jumps.
Great for control.
But it drifts — quietly, forever.

`map` is global.
Good for goals and floor plans.
But when localization corrects…
the pose can **jump**.

If control lived in `map`, every correction would feel like a teleport.
If planning lived only in `odom`, your “kitchen” would slowly walk down the hallway.

So ROS 2 doesn’t pick one.

It chains them:

`map` → `odom` → `base_link`

Odometry publishes the continuous edge.
Localization publishes the correcting edge.
TF2 holds the tree in time.

Interview point:

Localization does **not** publish `map` → `base_link` directly.
It publishes `map` → `odom` —
so `odom` → `base_link` stays smooth.

In today’s experiment: odom max step stayed **2.5 cm** while a map jump moved the global pose by **~1.55 m**. Give `base_link` two parents and TF reports *unconnected trees*.

Three frames.
One tree.
Three contracts.

Body. Drift. Truth.

Day 12 / #30DaysOfROS2

Repo: https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day12-tf2

#ROS2 #Robotics #TF2 #Navigation #30DaysOfROS2
