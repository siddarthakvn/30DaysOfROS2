# References — Day 01

Official resources used while studying and validating **Day 01 – Distributed Discovery in ROS 2** (Humble-first).

---

## Official ROS 2 documentation

| Topic | URL |
|---|---|
| ROS 2 docs hub | https://docs.ros.org/en/humble/ |
| Concepts index | https://docs.ros.org/en/humble/Concepts.html |
| Nodes | https://docs.ros.org/en/humble/Concepts/Basic/About-Nodes.html |
| Discovery | https://docs.ros.org/en/humble/Concepts/Basic/About-Discovery.html |
| Different middleware vendors (RMW) | https://docs.ros.org/en/humble/Concepts/Intermediate/About-Different-Middleware-Vendors.html |
| Domain ID | https://docs.ros.org/en/humble/Concepts/Intermediate/About-Domain-ID.html |
| ROS on DDS (design) | https://design.ros2.org/articles/ros_on_dds.html |
| Fast DDS | https://fast-dds.docs.eprosima.com/ |

---

## Commands used

```bash
ros2 doctor --report | grep -i rmw

printenv ROS_DOMAIN_ID RMW_IMPLEMENTATION

ros2 run demo_nodes_cpp talker
ros2 run demo_nodes_cpp listener

ros2 daemon stop
ros2 node list
ros2 topic list
ros2 topic info /chatter

watch -n 1 ros2 node list
```

---

## Notes

- Concepts here are based on official Humble docs plus the three localhost experiments in this folder.
- RMW page corrected to the Humble **middleware vendors** concept page (not a non-existent `Advanced/About-Middleware-Implementations` path).
- No third-party tutorials were copied into this documentation.
