# C — Lockdown does not resume the search

## Hypothesis

After the legal entry into LOCKDOWN, SEEN, MISSED, and a finished navigation goal leave the state where it is.

## Method

`mode:=stay`.

The script begins with the legal pair from B, SEEN then HELD. Then it offers SEEN, MISSED, and GOAL_DONE. GOAL_DONE is a navigation result. It is not in the edge table at all.

## Result

```text
SUMMARY mode=stay final=LOCKDOWN trace=SEARCHING>VERIFYING>LOCKDOWN events=SEEN>HELD>SEEN>MISSED>GOAL_DONE legal=2 rejected=3 lockdown=1 navigate_allowed=0 edges=3
```

The same two legal steps as B. The three events after LOCKDOWN were rejected. The trace does not grow. The echoed `/mission_state` is `LOCKDOWN`.

## Conclusion

LOCKDOWN has no outgoing arrow. A new glimpse, a miss, and a completed goal are mission noise. The coordinator keeps the robot in place.
