# B — Dijkstra spreads by travel cost

## Hypothesis

Ordering cells by the cost to arrive finds a shortest path, and the search fills most of the free grid before B is finished.

## Method

`mode:=dijkstra`.

Eight-connected steps. A diagonal step is refused when either side cell is a wall. The score of a cell is the distance walked to reach it. There is no guess about B. The first time B is taken off the open set, the parent pointers are a shortest path. This is the NavFn behavior with `use_astar: false`.

## Result

```text
SUMMARY mode=dijkstra reached=1 expanded=3989 free_cells=4284 path_poses=61 path_length_m=7.49 straight_m=7.00 line_wall_hits=10
```

The search opened 3989 of 4284 free cells. The path is 61 poses and 7.49 m, longer than the 7.00 m line because the line crosses a wall. The ASCII map in `assets/B_dijkstra.log` shows `+` across almost the whole room.

## Conclusion

Dijkstra chooses the cheapest route by flooding outward. On this map that flood is almost every free cell.
