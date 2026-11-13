# LinkedIn draft — Day 28

**Question:** YOLO gives pixels. Nav2 needs map coordinates. How do we connect them?

**Hero:** `assets/linkedin/01-hero.jpg`

Numbers below are from `./run_smoke.sh` on this machine. Domain 226. One surveyed box. Depth was given. Nav2 was not asked to drive.

---

The green box is on the screen. The pin is on the floor.

That is Day 28 of #30DaysOfROS2.

YOLO gives pixels. Nav2 needs map coordinates. How do we connect them?

The surveyed box sits at 3.500, 2.200, 0.250 meters. The camera turns it into column 276.522, row 250.870. Depth along the lens is 2.300 m.

Pixel and depth alone. /point_camera, /point_map, and /goal do not exist.

Turn the pixel into a 3D point and label those camera numbers as the map. The point is -0.200, 0.050, 2.300. The goal misses the box by 4.745 m.

Same point, through TF. The camera origin is at 1.200, 2.000, 0.300 in the map. The goal comes back at 3.500, 2.200, 0.250. The error is 0.000 m.

Direction. Distance. Camera pose. Then the pin is a goal.

Day 28 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day28-pixels-to-map

@NVIDIA

#ROS2 #Nav2 #TF2 #ComputerVision #Robotics #NVIDIARobotics
