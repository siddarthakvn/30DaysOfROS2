# Day 21 — Interview questions

1. A NavigateToPose goal arrives. Why is that not enough to make the wheels turn?

2. What message does the planner publish, and what message does the controller publish?

3. A straight line from start to goal is 4.6 m, and the planned path is 6.7 m. What does that extra length tell you?

4. The path is on `/plan` and `/cmd_vel` is silent. Where is the robot going?

5. Why does Nav2 put a behavior tree between the action server and the planner, instead of calling the planner once inside the action callback?

6. The controller is tracking the path and a new obstacle blocks it. Which stage should run again, and which message changes?
