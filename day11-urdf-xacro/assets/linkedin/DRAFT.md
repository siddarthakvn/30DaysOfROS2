# LinkedIn draft — Day 11

**Hero:** [`01-hero.png`](01-hero.png)

**Question:** How does ROS 2 know what a robot physically looks like?

---

How does ROS 2 know what a robot physically looks like?

It doesn’t see aluminum.
It doesn’t see motors.
It doesn’t “recognize” a humanoid.

You give it a description.

**URDF.**

A tree of:

• **links** — rigid bodies (torso, upper arm, palm)  
• **joints** — how those bodies connect  
• **origins** — where each part sits relative to its parent  

For a humanoid, that might look like:

`base` → `torso` → `shoulder` → `elbow` → `wrist` → `hand`

Not a sketch in someone’s notebook.
A shared kinematic model the whole stack can trust.

Then **Xacro** keeps the model maintainable:

Left arm.
Right arm.
Same macro.
Mirror it.

Less copy-paste.
Fewer silent asymmetries.

Interview point:

URDF is not a ROS node.
It’s the blueprint.

Launch can load it.
`robot_description` can carry it.
TF and RViz can use it.

Without that blueprint:

• RViz guesses wrong  
• sensors attach to nowhere  
• sim and real diverge  

So Day 11 isn’t really about XML.

It’s about this:

Describe the body once —
then ROS 2 can share one idea of the robot.

Day 11 / #30DaysOfROS2

Repo: https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day11-urdf-xacro

#ROS2 #Robotics #URDF #Xacro #Humanoid #30DaysOfROS2
