# B — The state machine does the job in six arrows

## Hypothesis

The plan / follow / back-up job can be written as a handful of edges. Each added recovery then needs its own failure link and its own arrow back to plan.

## Method

`mode:=machine`.

States are PLAN, FOLLOW, BACK_UP, DONE, and FAILED. Edges:

- PLAN ok → FOLLOW, PLAN fail → FAILED
- FOLLOW ok → DONE, FOLLOW fail → BACK_UP
- BACK_UP ok → PLAN, BACK_UP fail → FAILED

The leaves are scripted. Plan succeeds. The first follow fails. Back up succeeds. The second follow succeeds. The runner looks up each `(state, ok/fail)` edge and takes it.

The grown graph adds SPIN and WAIT in front of FAILED. The program builds that edge list and counts the difference. Those two extra leaves are not ticked in this run.

## Result

```text
SUMMARY mode=machine result=SUCCEEDED trace=plan>follow>back_up>plan>follow states=5 edges=6 grown_edges=10 added_edges=4
```

The trace is plan, follow, back up, plan, follow. The run succeeds. Six edges describe it. Adding spin and wait raises the edge count from 6 to 10. Four new arrows for two recoveries: each one gets a failure link and a success arrow back to PLAN.

## Conclusion

The state machine can do the job. The retry is a copied edge on the recovery, so every new recovery adds two arrows.
