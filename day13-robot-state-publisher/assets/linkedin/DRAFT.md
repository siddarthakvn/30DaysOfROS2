# LinkedIn draft — Day 13

**Hero:** [`01-hero.png`](01-hero.png)

**Question:** Who actually publishes the robot's transform tree?

---

A URDF file does not move a robot.
A TF tree does.
And almost nobody can name the node that actually publishes it.

That is Day 13 of #30DaysOfROS2.

**Who publishes the robot's transform tree?**

Not RViz.
Not the URDF.
Not the planner.

**`robot_state_publisher`.**

It takes two inputs:

- the kinematic model (`robot_description`)
- the live angles (`/joint_states`)

Then it splits the body into two contracts:

- **fixed joints** go out **once** on `/tf_static`
- **moving joints** go out on `/tf`, every time the angle changes

The angle source does not publish frames.
Hardware, simulation, or `joint_state_publisher` can supply `/joint_states`.
`robot_state_publisher` is the one that turns those angles into the tree every other node trusts.

In today's run, with no joint states, `base_link` → `hand` was missing.
Shoulder `0.80` and elbow `1.20` moved that same hand from **(0.60, 0, 0.42)** to **(0.18, 0, 0.00)**.
`/tf` and `/tf_static` had one publisher: `robot_state_publisher`.
`map` and `odom` never appeared. Those edges belong to someone else.

If that publisher is wrong, the rest of the stack is guessing:

- a camera bolted to a frame that never updates
- a gripper that exists in XML and nowhere in TF
- a sim and a real robot that no longer share a body

This is the quiet node under humanoids, Nav2, and Isaac-style stacks.

I am building this in public, one engineering question a day, on ROS 2 Humble.

If you work on robot foundations — simulation, description, or the runtime under a humanoid — I would like to talk.

Day 13 / #30DaysOfROS2

Repo: https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day13-robot-state-publisher

#ROS2 #Robotics #TF2 #Isaac #Humanoid #NVIDIA #30DaysOfROS2
