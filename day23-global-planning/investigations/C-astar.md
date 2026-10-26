# C — A* keeps the same length and opens fewer cells

## Hypothesis

Adding the straight-line distance still left keeps the path shortest and opens far fewer cells than Dijkstra.

## Method

`mode:=astar`.

The same grid, the same steps, the same parent rule. The score is the distance walked plus the straight-line distance from that cell to B. That added term never exceeds the distance still left, so the first time B is finished the walked length is still shortest.

## Result

```text
SUMMARY mode=astar reached=1 expanded=832 free_cells=4284 path_poses=61 path_length_m=7.49 straight_m=7.00 line_wall_hits=10
```

The search opened 832 of 4284 free cells. The path is 61 poses and 7.49 m, the same length Dijkstra returned. The cell list is not the same list: a grid can hold more than one route of that length. The ASCII map in `assets/C_astar.log` shows the `+` cells as a ribbon from A toward B, not a flood.

`/plan` again had one publisher, node `global_planner`, durability `TRANSIENT_LOCAL`.

## Conclusion

A* chooses a shortest path and spends the search on cells that could still be on the way. Here that was 832 cells instead of 3989, and the length stayed 7.49 m.
