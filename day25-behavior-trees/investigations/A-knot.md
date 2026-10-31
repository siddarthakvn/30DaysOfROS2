# A — Five boxes, twenty arrows

## Hypothesis

If every behavior in the picture has an arrow to every other behavior, five boxes produce twenty directed arrows, and the drawing still does not say what to do when follow fails.

## Method

`tick.py` with `mode:=knot`.

The boxes are the ones in the hero: PLAN, FOLLOW, CLEAR, SPIN, BACK UP. The program builds a directed edge from each box to each other box and counts them. Nothing is ticked. There is no success rule.

## Result

```text
SUMMARY mode=knot result=NONE trace=- states=5 edges=20 grown_edges=0 added_edges=0
```

Five states. Twenty arrows. Result is NONE because the knot is not a policy.

`/behavior_tree_log` had one publisher, node `checklist`, type `nav2_msgs/msg/BehaviorTreeLog`, durability `TRANSIENT_LOCAL`. The event log is empty.

## Conclusion

A complete set of arrows is the giant state machine. It records that anything might follow anything. It does not record the checklist.
