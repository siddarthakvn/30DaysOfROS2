# Day 08 — Interview Questions

## 1. What happens if one subscription callback takes 500 ms on a SingleThreadedExecutor?

**Expected direction:** Other callbacks on that executor (timers, other subscriptions, services) cannot run until it returns. Ready work waits; middleware history may fill (Day 03). The OS may still run other processes/threads, but **this executor’s** callbacks are stalled.

## 2. You switched to MultiThreadedExecutor and nothing improved. Why?

**Expected direction:** Entities likely still share the default (or one) MutuallyExclusive callback group. Official docs: that configuration behaves like single-threaded concurrency. Need separate groups (or Reentrant where safe) **and** free threads.

## 3. What is the difference between a MutuallyExclusive and a Reentrant callback group?

**Expected direction:** MutEx — at most one callback from the group runs at a time (including no re-entry of the same callback). Reentrant — no such restriction; same callback may overlap itself; shared state must be thread-safe. Callbacks in **different** groups may always overlap (if the executor has threads).

## 4. Does MultiThreadedExecutor make a slow callback faster?

**Expected direction:** No. It may allow *other* callbacks to proceed. The slow work still occupies a thread for its duration. Offload heavy work to a worker queue/action/separate process if you need the callback itself to stay short.

## 5. How do Day 02, Day 03, Day 07, and Day 08 fit together?

**Expected direction:**

| Day | Failure |
|---|---|
| 02 | Shared **process** → shared fate on crash |
| 03 | Matched topic + slow process → **staleness / drops** |
| 07 | **QoS mismatch** → no data path |
| 08 | Matched QoS + blocked callback → **starvation / deadline misses** |

## One-liner

**DDS delivers. The executor schedules. Callback groups decide who may run together.**
