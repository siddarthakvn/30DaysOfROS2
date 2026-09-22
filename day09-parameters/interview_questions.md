# Day 09 — Interview Questions

## 1. How do you change robot behavior without changing code?

**A:** Use **ROS 2 parameters** — per-node settings declared by the node, optionally loaded from YAML/launch, changeable at runtime with `ros2 param set`. Behavior changes only if the node **accepts** and **applies** the new value.

## 2. How is that different from ROS 1?

**A:** ROS 1 used a **global parameter server**. ROS 2 parameters are **owned by each node** and exposed through parameter services. There is no central blackboard by default.

## 3. Does `ros2 param set` always change behavior?

**A:** No. It updates the stored parameter if validation succeeds. The application must read/use it. A cache-once design can ignore later sets. Unsafe values can be **rejected** in `add_on_set_parameters_callback`.

## 4. When should you use a parameter vs a topic?

**A:** Parameter = **configuration** (limits, gains, modes). Topic = **streaming data/commands**. Don’t put `/cmd_vel` goals into parameters.

## One-liner

**Parameters are per-node settings. A set only changes the robot if the node accepts it and actually uses the new value.**
