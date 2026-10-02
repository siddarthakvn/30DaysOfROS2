# Interview questions — Day 15

## 1. Why is a perfect simulated lidar a problem?

It repeats the exact distance when nothing moves. A real beam wobbles. A node that looks finished on the exact number can stop and go on a real robot.

## 2. What is one lidar beam?

A direction from the sensor. The reading is how far that beam traveled before it hit a surface. Optional noise is added after that distance.

## 3. What did "no noise" mean in this experiment?

Two scans of a still wall were identical. The largest change was 0.000 m. The center beam read 1.9006 m, which is the wall face.

## 4. What changed when Gaussian noise was turned on?

The wall stayed put and the rate stayed about 5 Hz. The numbers moved. The largest beam-to-beam change in the window was 0.223 m.

## 5. What does update rate change?

How often a new scan exists. Dropping it from 5 Hz to 1 Hz left the distances identical.

## 6. Why can Gazebo be publishing while `ros2 topic echo /lidar` is silent?

The scan is on Gazebo Transport. ROS sees it only after `ros_gz_bridge` copies `gz.msgs.LaserScan` onto `/lidar`.
