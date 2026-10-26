# Day 23 — References

## Primary

1. **NavFn and `use_astar`**  
   `/opt/ros/humble/share/nav2_bringup/params/nav2_params.yaml` sets `use_astar: false` on the `NavfnPlanner` plugin.  
   `/opt/ros/humble/include/nav2_navfn_planner/navfn_planner.hpp` holds `use_astar_`.  
   With the flag off, NavFn spreads a potential by cost. With the flag on, the expansion prefers cells toward the goal. This day runs those two orderings on one grid.

2. **Dijkstra**  
   Edsger Dijkstra, "A Note on Two Problems in Connexion with Graphs," Numerische Mathematik, 1959. Expand the unsettled cell with the smallest cost to arrive.

3. **A\***  
   Peter Hart, Nils Nilsson, Bertram Raphael, "A Formal Basis for the Heuristic Determination of Minimum Cost Paths," IEEE Transactions on Systems Science and Cybernetics, 1968. Add a heuristic that never exceeds the remaining cost, and the first time the goal is settled the path is optimal.

4. **nav_msgs/Path**  
   http://docs.ros.org/en/humble/p/nav_msgs/msg/Path.html  
   A header and a sequence of poses. Published latched on `/plan`.

5. **Nav2 planner server**  
   https://docs.nav2.org/configuration/packages/navfn_planner.html

## This machine

- ROS 2 Humble
- `nav_msgs` from `/opt/ros/humble`
- `ROS_DOMAIN_ID=230`

## Related days

- Day 21 — a goal becomes a path before it becomes speed
- Day 22 — the costmap is the room the planner believes. Today the search runs on that room
