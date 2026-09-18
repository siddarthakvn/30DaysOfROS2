# Interview Questions — Day 05

Interview prompts based on **Day 05 – Action Cancellation**.

## 1. What happens inside ROS 2 when a client cancels an executing goal?

**Expected direction:** CancelGoal service → server cancel callback ACCEPT/REJECT → if ACCEPT, status `CANCELING` → execute loop must notice `is_cancel_requested`, clean up, call `canceled()` → terminal `CANCELED` + result. Accepting cancel ≠ already stopped.

## 2. Why is Action cancel different from Ctrl+C on the client?

**Expected direction:** Killing/disconnecting the client does not automatically issue CancelGoal. The server may keep executing. Cancel is an explicit protocol with status and result.

## 3. What is the difference between `CANCELED` and `ABORTED`?

**Expected direction:** `CANCELED` follows an external cancel request that the server completed. `ABORTED` is server-initiated termination (error, or often preemption when a new goal replaces the old one). Policy is application-defined.

## 4. Can an action server refuse to cancel? What should the client observe?

**Expected direction:** Yes — cancel callback can return REJECT (rclpy default rejects). Client sees empty `goals_canceling` / no transition to `CANCELING`; goal can still `SUCCEEDED`. Day 05 Investigation C demonstrated this with `allow_cancel:=false`.

## 5. Why do long robot tasks (nav, manipulation, docking) use Actions instead of Services?

**Expected direction:** Services have no mid-flight feedback and no cancel API. Actions provide goal lifecycle, feedback, and cooperative cancellation — required when an operator or planner says STOP mid-mission.
