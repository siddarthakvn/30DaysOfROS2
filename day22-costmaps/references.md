# Day 22 — References

## Primary

1. **Cost values**  
   `/opt/ros/humble/include/nav2_costmap_2d/nav2_costmap_2d/cost_values.hpp`  
   Free is 0. Inscribed inflated is 253. Lethal is 254. Unknown is 255.

2. **InflationLayer::computeCost**  
   `/opt/ros/humble/include/nav2_costmap_2d/nav2_costmap_2d/inflation_layer.hpp`  
   Distance 0 is lethal. Distance inside the inscribed radius is 253. Farther out, `cost = 252 * exp(-cost_scaling_factor * (distance_m - inscribed_radius))`.

3. **Humble bringup defaults**  
   `/opt/ros/humble/share/nav2_bringup/params/nav2_params.yaml`  
   Global costmap plugins: static layer, obstacle layer, inflation layer. Local costmap: rolling 3 m window. `robot_radius` 0.22. `inflation_radius` 0.55. `cost_scaling_factor` 3.0. `obstacle_max_range` 2.5. `raytrace_max_range` 3.0.

4. **NavFn cost scale**  
   `/opt/ros/humble/include/nav2_navfn_planner/navfn.hpp`  
   Costs 253 and 254 are obstacles. Traversable costs become `50 + 0.8 * cost`.

5. **nav2_msgs/Costmap**  
   `/opt/ros/humble/share/nav2_msgs/msg/Costmap.msg`  
   A header, `CostmapMetaData`, and a row-major `uint8[]`. This day publishes that message on `/global_costmap/costmap` and `/local_costmap/costmap`.

6. **Nav2 costmap configuration**  
   https://docs.nav2.org/configuration/packages/costmap-2d.html

## This machine

- ROS 2 Humble
- `nav2_msgs` and `nav2_costmap_2d` headers from `/opt/ros/humble`
- `ROS_DOMAIN_ID=220`

## Related days

- Day 15 — a scan is a set of ranges, and a range can outlive the thing that returned it
- Day 19 — an occupancy grid is the map. A costmap is that grid plus a cost for the body
- Day 21 — the planner writes a `nav_msgs/Path` before anything becomes speed
