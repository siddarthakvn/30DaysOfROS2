# Day 19 — References

## Primary

1. **nav_msgs/OccupancyGrid**  
   http://docs.ros.org/en/humble/p/nav_msgs/msg/OccupancyGrid.html  
   The map is a grid. Each cell is unknown (`-1`), free (`0`), or occupied (`100`). This day publishes that message on `/map` with transient-local durability so a late subscriber still receives it.

2. **sensor_msgs/LaserScan**  
   http://docs.ros.org/en/humble/p/sensor_msgs/msg/LaserScan.html  
   One sweep: `angle_min`, `angle_increment`, and a range per beam.

3. **slam_toolbox**  
   https://github.com/SteveMacenski/slam_toolbox  
   The Humble package that runs this loop on a live `/scan`: match the scan, update the pose, write the occupancy grid. This day uses a tiny search in a scripted room so each number can be checked by hand.

4. **Probabilistic Robotics — Thrun, Burgard, Fox**  
   Occupancy-grid mapping and scan matching. A beam marks free space up to the return and occupied space at the return. The pose used to place that beam decides whether the wall stays put.

## This machine

- ROS 2 Humble
- `nav_msgs` and `sensor_msgs` from `/opt/ros/humble`
- `ROS_DOMAIN_ID=190`

## Related days

- Day 12 — `map` is the frame the grid lives in
- Day 15 — a scan is a set of ranges, and a perfect scan is still only a scan
- Day 18 (curriculum) — wheel pose drifts, which is the error Investigation B paints with
