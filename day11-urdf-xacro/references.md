# Day 11 — References

## Primary (ROS 2 Humble)

1. **URDF — Main** (Humble)  
   https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/URDF-Main.html  
   - URDF describes robot geometry and organization as XML

2. **Building a Visual Robot Model with URDF from Scratch** (Humble)  
   https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Building-a-Visual-Robot-Model-with-URDF-from-Scratch.html  
   - Links need joints + origins to be placed correctly

3. **Building a Movable Robot Model with URDF** (Humble)  
   https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Building-a-Movable-Robot-Model-with-URDF.html  
   - Joint types (`fixed`, `revolute`, `continuous`, …)

4. **Using Xacro to Clean Up a URDF File** (Humble)  
   https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Using-Xacro-to-Clean-Up-a-URDF-File.html  
   - Macros / properties; expand to URDF at load time

5. **robot_state_publisher**  
   https://docs.ros.org/en/humble/p/robot_state_publisher/  
   - Consumes URDF (`robot_description`) + `joint_states` → TF

## Related series days

- Day 09 — parameters (`robot_description` is a large string parameter)
- Day 10 — launch loads description into the graph
- Day 12 — TF frames (`base_link`, `odom`, `map`)
- Day 13 — who publishes the transform tree
