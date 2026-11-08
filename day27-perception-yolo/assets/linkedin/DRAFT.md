# LinkedIn draft — Day 27

**Question:** Running YOLO is easy — but how do you make perception part of a ROS 2 system?

**Hero:** `assets/linkedin/01-hero.jpg`

Numbers below are from `./run_smoke.sh` on this machine. Domain 227. The 0.92 on the hero is the drawing. The run measured 0.890.

---

The model found four people. The mission heard one word.

That is Day 27 of #30DaysOfROS2.

Running YOLO is easy. How do you make perception part of a ROS 2 system?

Same photo. Three graphs.

Drawn in one process. Best person score 0.890. Four people, one bus. /front/image_raw, /detections, and /mission_event were unknown topics. Nothing was published.

Gray frame, full graph. The image topic is sensor_msgs/Image, frame front. The detection message is an empty array, and it carries that same stamp. The mission echo has no data. SEEN stays 0.

Street frame, full graph. 810 by 1080, bgr8. The detector copies the camera stamp. Five boxes come back: person 0.890, person 0.883, person 0.878, bus 0.843, person 0.436. The echoed mission event is SEEN.

The bus is louder than the line and still does not count. The 0.436 person stays in the message and stays under 0.50. SEEN is the best person, on the camera stamp, on a topic another node can subscribe to.

A box in a window is not a message. An empty message is not a person.

Day 27 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day27-perception-yolo

#ROS2 #ComputerVision #YOLOv8 #Robotics #cv_bridge
