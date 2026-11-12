# LinkedIn draft — Day 28

**Hero:** [`01-hero.jpg`](01-hero.jpg)

**Question:** YOLO gives pixels. Nav2 needs map coordinates. How do we connect them?

---

YOLO gives pixels. Nav2 needs map coordinates. How do we connect them?

A detection box says the person is at pixel (420, 310). That is useful to a screen. It is useless to a planner. Nav2 does not drive in image space. It needs a place on the map: meters, and a frame it already trusts.

So the gap is not “run YOLO harder.” The gap is geometry.

Three steps close it:

- Depth tells you how far that pixel is from the camera. Without distance, a pixel is only a direction.
- Camera geometry turns that pixel plus distance into a 3D point in the camera frame.
- TF2 walks that point into the map frame: camera → base_link → map. The same point, named in the language Nav2 already uses.

I ran the same box four ways. Truth was map (2.000, 0.000, 0.150).

- Pixel + true depth + TF: landed exactly on the box. Error 0.000 m.
- Same pixel, depth guessed as 1.0 m: map point came out 0.750 m short.
- Pixel + depth, no TF: the point stayed next to the camera. Error about 2.0 m.
- Robot moved 0.50 m, pixel updated, old TF kept: map error was exactly 0.500 m.

Miss any one piece, and the robot is either guessing a distance, guessing a frame, or sending Nav2 a number that still lives on the image.

Day 28 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day28-pixels-to-map

#30DaysOfROS2 #BostonDynamics #NVIDIARobotics #ROS2 #ComputerVision #Robotics
