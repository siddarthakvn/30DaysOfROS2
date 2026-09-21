# Day 08 — References

## Primary (ROS 2 Humble)

1. **About Executors** — ROS 2 Concepts (Humble)  
   https://docs.ros.org/en/humble/Concepts/Intermediate/About-Executors.html  
   Source RST: https://github.com/ros2/ros2_documentation/blob/humble/source/Concepts/Intermediate/About-Executors.rst  
   - Executor invokes callbacks using OS threads  
   - Messages remain in middleware until taken (not a separate client-library queue)  
   - Wait set reports binary readiness; overload → round-robin-like selection  
   - MultiThreaded parallelism is gated by callback groups  

2. **Using Callback Groups** — ROS 2 How-To Guide (Humble)  
   https://docs.ros.org/en/humble/How-To-Guides/Using-callback-groups.html  
   Source RST: https://github.com/ros2/ros2_documentation/blob/humble/source/How-To-Guides/Using-callback-groups.rst  
   - MutuallyExclusive vs Reentrant  
   - Default group is MutuallyExclusive  
   - Different groups may run in parallel  
   - Shared MutEx + MultiThreaded ≈ single-threaded concurrency  
   - Sync service calls can deadlock inside the wrong group layout  

3. **rclpy executors / callback groups (Humble)**  
   https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/executors.py  
   https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/callback_groups.py  
   - `SingleThreadedExecutor` runs callbacks on the spin thread  
   - `MultiThreadedExecutor` uses a `ThreadPoolExecutor`  
   - `MutuallyExclusiveCallbackGroup` allows only one active entity  

## Supporting

4. Casini et al., *Response-Time Analysis of ROS 2 Processing Chains under Reservation-Based Scheduling*, ECRTS 2019 — cited from the official Executors page for scheduling semantics under overload.

5. Day 02 / 03 / 07 of this series — process vs node isolation; topic backlog/staleness; QoS matching vs silence.

## Notes

- Prefer the Humble docs above over generic blog tutorials when citing behavior.  
- This experiment uses `time.sleep` as a controllable stand-in for blocking work (I/O or long compute). CPU-bound work has the same **scheduling** effect on the occupied thread/group, plus additional core contention.
