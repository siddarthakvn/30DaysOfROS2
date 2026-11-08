# Day 27 — References

## Primary

1. **sensor_msgs/Image**  
   http://docs.ros.org/en/humble/p/sensor_msgs/msg/Image.html  
   Height, width, encoding, and a header. `/front/image_raw` in this day is `bgr8` with `frame_id` `front`.

2. **cv_bridge**  
   https://docs.ros.org/en/humble/p/cv_bridge/  
   `cv2_to_imgmsg` in the camera. `imgmsg_to_cv2(..., desired_encoding="bgr8")` in the detector. The model never sees the ROS bytes directly.

3. **vision_msgs/Detection2DArray**  
   http://docs.ros.org/en/humble/p/vision_msgs/msg/Detection2DArray.html  
   http://docs.ros.org/en/humble/p/vision_msgs/msg/Detection2D.html  
   Header plus `Detection2D[]`. Each detection has `ObjectHypothesis` (`class_id`, `score`) and a `BoundingBox2D` (center `Pose2D`, `size_x`, `size_y` in pixels). The message comment says the header should match the source image so another node can sync them. This run copies that header and checks the stamps.

4. **YOLOv8n ONNX**  
   https://github.com/ultralytics/assets/releases/download/v8.4.0/yolov8n.onnx  
   Loaded with `cv2.dnn.readNetFromONNX`. Output shape used here is `(1, 84, 8400)`: box plus 80 COCO scores. Letterbox to 640, then `cv2.dnn.NMSBoxes`. The file is downloaded by `fetch.sh` and gitignored. The Python `ultralytics` package is not required.

5. **The street photo**  
   https://ultralytics.com/images/bus.jpg  
   Downloaded by `fetch.sh` to `assets/frames/street.jpg`. Not committed. A flat gray frame is generated in code for the empty case.

## This machine

- ROS 2 Humble
- `sensor_msgs`, `vision_msgs`, `cv_bridge` from `/opt/ros/humble`
- OpenCV 4.10 DNN
- `ROS_DOMAIN_ID=227`
- One-frame QoS: `RELIABLE` + `TRANSIENT_LOCAL`, depth 1

## Related days

- Day 26 — `SEEN` is the event that leaves SEARCHING for VERIFYING. This day publishes that string and does not run the coordinator.
