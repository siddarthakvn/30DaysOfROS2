# LinkedIn draft — Day 21

**Question:** What actually happens after I send a Nav2 goal?

---

You tapped a point on the map.

The wheels never saw that point.

That is Day 21 of #30DaysOfROS2.

What actually happens after I send a Nav2 goal?

I sent one NavigateToPose goal three times. A wall stood between the robot and the pin. The straight distance was 4.60 m.

Goal only. The action arrived. No path. No speed. The action came back aborted. The robot was still 4.600 m away.

Planner only. A path appeared: 27 poses, 6.69 m long, climbing to y = 2.50 m to clear the wall. The robot had not moved. A line on the map is not a wheel command.

Then the controller was allowed to run. It turned that same line into Twist. 279 speed commands. Peak 0.45 m/s. The body never entered the wall. Final error 0.130 m. The action returned succeeded.

The order was goal, then path, then cmd_vel.

A goal is a place. A path is a line. A command is a speed. They leave in that order.

Day 21 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day21-nav2-architecture

#ROS2 #Nav2 #Robotics #Navigation #BostonDynamics #NVIDIARobotics

## Hero image prompt

```text
Technical engineering diagram, one wide 16:9 frame, dark charcoal background, cream lines, amber highlights. No workbench, no laptop, no photograph.

Four boxes in a row, connected by arrows.

Box 1, title GOAL. A map pin and the words NavigateToPose.
Box 2, title TREE. A short checklist: plan, drive, check.
Box 3, title PLANNER. A dotted route bending over a wall, from a start mark to the pin. A straight line through the wall is drawn faint and crossed out.
Box 4, title CONTROLLER. A small arrow labeled cmd_vel leaving the box toward a wheel.

Caption under the row: The goal is a pose. The planner draws the line. The controller sends the speed.

Top title, cream serif: What happens after a Nav2 goal.
Flat vector, sharp readable text, serious, no neon, no 3D, no hologram.
```
