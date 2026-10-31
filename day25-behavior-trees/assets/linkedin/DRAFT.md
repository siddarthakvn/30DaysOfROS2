# LinkedIn draft — Day 25

**Question:** Why does Nav2 use Behavior Trees instead of one giant state machine?

**Hero:** `assets/linkedin/01-hero.jpg`

Numbers below are from `./run_smoke.sh` on this machine. Domain 229. The leaf results are scripted: the first follow fails, back up succeeds, the second follow succeeds. What was counted is the control structure.

---

Five boxes. Twenty arrows.

That is Day 25 of #30DaysOfROS2.

Why does Nav2 use Behavior Trees instead of one giant state machine?

The picture links every behavior to every other one. Five boxes, 20 arrows, and still no rule for what happens when follow fails.

The job was the one from yesterday. Plan. Follow. Follow fails. Back up. Plan. Follow. Succeed.

A state machine does that job in 6 arrows. Add spin and wait and it grows to 10. Four new arrows. Each recovery needs a failure link and its own arrow back to plan.

A behavior tree does the same job in 5 links, and the trace is the same: plan, follow, back up, plan, follow. Add spin and wait and it grows to 7. Two new links. One each. The retry stays a single rule at the top. If follow fails, recover, then tick the checklist again.

Same steps. The tree is the one that stays a list.

Day 25 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day25-behavior-trees

#ROS2 #Nav2 #Robotics #Navigation #BehaviorTrees #BostonDynamics #NVIDIARobotics
