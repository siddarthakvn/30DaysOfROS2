# C — The tree does the same job, and grows by one link

## Hypothesis

A recovery node with the same leaves produces the same trace. Adding spin and wait adds one link each, because the retry stays inside the recovery node.

## Method

`mode:=tree`.

The root is a recovery node. Its first child is the sequence plan, then follow. Its second child is a fallback whose only recovery is back up. On a failed sequence the fallback runs. If the fallback succeeds, the sequence is ticked again. That is the shape of Nav2's `RecoveryNode`, with one recovery instead of the full round-robin.

The leaves are the same script as B. The grown tree adds spin and wait as two more children of the fallback, and the program counts those links. They are not ticked in this run.

## Result

```text
SUMMARY mode=tree result=SUCCEEDED trace=plan>follow>back_up>plan>follow nodes=6 edges=5 grown_edges=7 added_edges=2
```

The trace matches the state machine, and the run succeeds. Six nodes, five links. Adding spin and wait raises the link count from 5 to 7. Two new links for two recoveries.

`/behavior_tree_log` again had one publisher, node `checklist`, durability `TRANSIENT_LOCAL`. The five status changes are the trace: plan success, follow failure, back up success, plan success, follow success.

## Conclusion

The tree and the state machine take the same steps. The tree grows by one link per recovery, because "try again from the top" is the recovery node's rule rather than a new arrow on every state.
