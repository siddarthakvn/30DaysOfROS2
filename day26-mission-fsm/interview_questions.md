# Day 26 — Interview questions

1. A detector fires once while the robot is SEARCHING. Why is the next state VERIFYING and not LOCKDOWN?

2. VERIFYING times out and the shape is gone. Which edge fires, and which tool is allowed again?

3. The robot is in LOCKDOWN and `NavigateToPose` succeeds. What does the coordinator do with that result?

4. Why is HELD refused when the current state is SEARCHING?

5. Day 25 put plan, follow, and recover in a behavior tree. Why is this mission a state machine instead?

6. Who is allowed to call Nav2, and which state grants that?
