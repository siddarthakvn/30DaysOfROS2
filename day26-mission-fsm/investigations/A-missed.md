# A — A glimpse, a miss, and a refused shortcut

## Hypothesis

SEEN moves the robot from SEARCHING to VERIFYING. MISSED moves it back. HELD, offered while SEARCHING again, is refused, so LOCKDOWN is never entered.

## Method

`coordinator.py` with `mode:=missed`.

The coordinator starts in SEARCHING. The script is SEEN, then MISSED, then HELD. Only pairs in the edge table are taken. The table is SEEN from SEARCHING, HELD from VERIFYING, and MISSED from VERIFYING.

## Result

```text
SUMMARY mode=missed final=SEARCHING trace=SEARCHING>VERIFYING>SEARCHING events=SEEN>MISSED>HELD legal=2 rejected=1 lockdown=0 navigate_allowed=1 edges=3
```

Two events were legal. HELD was rejected because the state was already SEARCHING again. `lockdown=0`. Navigate is allowed, because the final state is SEARCHING.

`ros2 topic echo --once /mission_state` printed `data: SEARCHING`. One publisher, node `coordinator`, type `std_msgs/msg/String`, durability `TRANSIENT_LOCAL`.

## Conclusion

A detection opens a check. A missed check returns to the search. Confirming without that check is not a transition.
