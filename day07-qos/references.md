# References — Day 07 QoS

| Source | URL / path |
|---|---|
| Quality of Service settings (Humble) | https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html |
| QoS design article | https://design.ros2.org/articles/qos.html |
| Lossy-network QoS demo | https://docs.ros.org/en/humble/Tutorials/Demos/Quality-of-Service.html |
| Fast DDS standard QoS policies | https://fast-dds.docs.eprosima.com/en/latest/fastdds/dds_layer/core/policy/standardQosPolicies.html |
| Default / sensor profiles (local Humble) | `/opt/ros/humble/include/rmw/rmw/qos_profiles.h` |
| Day 01 discovery | `../day01-distributed-discovery/` |
| Day 03 queues / backpressure | `../day03-topics-and-backpressure/` |

## Profile cheat sheet (Humble `rmw`)

| Profile | History | Depth | Reliability | Durability |
|---|---|---|---|---|
| default | KEEP_LAST | 10 | RELIABLE | VOLATILE |
| sensor_data | KEEP_LAST | 5 | BEST_EFFORT | VOLATILE |
| services_default | KEEP_LAST | 10 | RELIABLE | VOLATILE |
| parameters | KEEP_LAST | 1000 | RELIABLE | VOLATILE |
| system_default | SYSTEM_DEFAULT | — | SYSTEM_DEFAULT | SYSTEM_DEFAULT |
