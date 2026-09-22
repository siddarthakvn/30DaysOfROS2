# Day 09 — References

## Primary (ROS 2 Humble)

1. **About Parameters**  
   https://docs.ros.org/en/humble/Concepts/Basic/About-Parameters.html  
   https://github.com/ros2/ros2_documentation/blob/humble/source/Concepts/Basic/About-Parameters.rst

2. **Understanding parameters (CLI tutorial)**  
   https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Parameters/Understanding-ROS2-Parameters.html

3. **Passing ROS arguments / YAML params files**  
   https://docs.ros.org/en/humble/How-To-Guides/Node-arguments.html

4. **Using `ros2 param`**  
   https://docs.ros.org/en/humble/How-To-Guides/Using-ros2-param.html

5. **Migrating Parameters (ROS 1 → ROS 2)**  
   https://docs.ros.org/en/humble/How-To-Guides/Migrating-from-ROS1/Migrating-Parameters.html  
   - Per-node parameters vs ROS 1 global parameter server  
   - `set_parameters_atomically` vs partial `set_parameters`

## Notes

- On-set callbacks must be side-effect free; react after accept via parameter events / live `get_parameter`.
- CLI values are YAML-typed (`off` may parse as bool).
