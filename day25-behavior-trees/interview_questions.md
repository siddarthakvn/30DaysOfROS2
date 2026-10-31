# Day 25 — Interview questions

1. Five navigation behaviors each have an arrow to every other one. How many directed arrows is that, and what policy does it encode?

2. Plan, follow, and back up succeed with the trace `plan>follow>back_up>plan>follow`. Why is that not yet an argument for a behavior tree?

3. A successful recovery in the state machine has an edge back to PLAN. Where does that same retry live in the recovery node?

4. Spin and wait are added. Why does the state machine gain four arrows while the tree gains two links?

5. What does `bt_navigator` tick, and what does it deliberately leave to the planner and the controller?

6. `FollowPath` fails. Which node in `navigate_to_pose_w_replanning_and_recovery.xml` decides whether to try again?
