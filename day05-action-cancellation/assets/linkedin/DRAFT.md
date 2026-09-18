# LinkedIn Draft — Day 05

**Day 05 teaser used in Day 04:** How does a robot cancel a task while it is still executing?

---

Halfway through a warehouse aisle, the AMR is still rolling toward Station B.

You hit **STOP**.

What should happen?

Not “kill the node.”  
Not “stop publishing and hope.”

In ROS 2, STOP is an **Action cancel**:

1. Client sends CancelGoal for that mission UUID  
2. Server accepts or rejects  
3. If accepted → `CANCELING` (cleanup)  
4. Execute stops the robot → `CANCELED` + how far it got  

**Today’s experiment (Humble):**

| Run | Result |
|---|---|
| Full 10 m delivery | `SUCCEEDED` |
| STOP at 2 s (cancel allowed) | `CANCELED` at 2.2 m |
| STOP at 2 s (cancel rejected) | still `SUCCEEDED` at 10 m |

**Lesson:** Cancel is a handshake, and the server’s policy matters. Same idea Nav2 uses when you cancel `NavigateToPose`.

#30DaysOfROS2 #ROS2 #Robotics

---

*(Human posts after Git Checkpoint / publish ritual.)*
