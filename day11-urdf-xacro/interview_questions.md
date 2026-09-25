# Day 11 — Interview Questions

## Conceptual

1. **How does ROS 2 know what a robot physically looks like?**  
   It doesn’t sense the hardware. You supply a **URDF** (link/joint tree), usually via the `robot_description` parameter. Nodes like `robot_state_publisher` publish TF so tools share that model.

2. **Is URDF a ROS node?**  
   No. It’s an XML description (a file or string). Nodes *consume* it.

3. **Link vs joint?**  
   A **link** is a rigid body. A **joint** connects parent→child with an origin and a motion type (`fixed`, `revolute`, `continuous`, `prismatic`, …).

4. **What is Xacro for?**  
   Macro language to generate URDF with less duplication (e.g. left/right arms). Runtime still sees expanded URDF.

5. **Visual vs collision vs inertial?**  
   Visual = what you see (RViz). Collision = contact/planning. Inertial = dynamics/sim. They can differ on purpose.

## Practical / debugging

6. **RViz shows everything piled at the origin. What’s wrong?**  
   Missing joints/origins, or wrong parent/child tree — parts aren’t placed relative to each other.

7. **Fixed model looks fine; arm doesn’t move when you drag a slider.**  
   Joint may still be `fixed`, or no `joint_states` are being published for that DOF.

8. **`robot_state_publisher` is running but TF for a revolute chain is incomplete.**  
   Until `joint_states` arrive, only **fixed** joints are fully published as static TF.

9. **Why put URDF in a parameter instead of every node reading a file?**  
   One shared graph-visible blueprint; launch can expand Xacro once and distribute the string.

## One-liner

**Describe the body once (URDF/Xacro) → load `robot_description` → publish frames → the stack can agree on the robot.**
