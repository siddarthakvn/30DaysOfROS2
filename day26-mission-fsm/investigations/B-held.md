# B — Seen, then held

## Hypothesis

SEEN followed by HELD is the only way into LOCKDOWN. At the end, a navigation goal is no longer allowed.

## Method

`mode:=held`.

The script is SEEN, then HELD. No other events are offered.

## Result

```text
SUMMARY mode=held final=LOCKDOWN trace=SEARCHING>VERIFYING>LOCKDOWN events=SEEN>HELD legal=2 rejected=0 lockdown=1 navigate_allowed=0 edges=3
```

Both events were legal. Nothing was rejected. The trace is SEARCHING, VERIFYING, LOCKDOWN. `navigate_allowed=0`.

`ros2 topic echo --once /mission_state` printed `data: LOCKDOWN`.

## Conclusion

Lockdown is the second look holding, not the first glimpse. Once the coordinator is there, it stops lending the robot to Nav2.
