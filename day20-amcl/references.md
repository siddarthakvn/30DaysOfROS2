# Day 20 — References

## Primary

1. **Nav2 AMCL**  
   https://docs.nav2.org/configuration/packages/configuring-amcl.html  
   Adaptive Monte Carlo Localization. A cloud of pose guesses is moved by odometry and weighted by the laser against a frozen occupancy grid. This day runs that loop on a scripted house so each guess can be counted. It does not launch the Nav2 lifecycle node.

2. **nav_msgs/OccupancyGrid**  
   http://docs.ros.org/en/humble/p/nav_msgs/msg/OccupancyGrid.html  
   The floor plan. Published latched on `/map`.

3. **geometry_msgs/PoseArray**  
   http://docs.ros.org/en/humble/p/geometry_msgs/msg/PoseArray.html  
   The paper dots. Published on `/particle_cloud`.

4. **Probabilistic Robotics — Thrun, Burgard, Fox**  
   Monte Carlo localization. Predict with the motion model, weight with the beam model, resample.

## This machine

- ROS 2 Humble
- `nav_msgs` and `geometry_msgs` from `/opt/ros/humble`
- `ROS_DOMAIN_ID=200`
- `nav2_amcl` is installed on this machine and is the production version of this loop

## Related days

- Day 12 — `map` is the frame the floor plan lives in
- Day 19 — the grid is drawn by lining scans up and painting cells. Today that grid is an input
