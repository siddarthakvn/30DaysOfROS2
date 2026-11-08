# B — An empty message

## Hypothesis

A frame with no person still produces an image and a detection message. The ear does not say SEEN.

## Method

`scene:=blank`. Three nodes: `front_camera`, `yolo_detector`, `mission_ear`. The frame is flat gray, 640×480, generated in the camera node.

## Result

```text
SUMMARY node=camera scene=blank width=640 height=480 encoding=bgr8 frame=front stamp_sec=1794135799 stamp_nsec=154921476
SUMMARY node=detector scene=blank width=640 height=480 detections=0 persons=0 best_person=0.000 cx=0.0 cy=0.0 sx=0.0 sy=0.0 classes=- frame=front stamp_sec=1794135799 stamp_nsec=154921476 stamp_match=1
SUMMARY node=ear scene=blank seen=0 best_person=0.000 class_id=- threshold=0.50 detections=0 frame=front stamp_sec=1794135799 stamp_nsec=154921476
```

`/front/image_raw` is `sensor_msgs/msg/Image`. Publisher `front_camera`, subscriber `yolo_detector`, both `RELIABLE` and `TRANSIENT_LOCAL`.

The detection echo:

```text
header:
  stamp:
    sec: 1794135799
    nanosec: 154921476
  frame_id: front
detections: []
```

`ros2 topic echo --once /mission_event` returned no `data:` line.

## Conclusion

The graph was up. The message was empty. SEEN stayed unpublished. A missing person is an empty array with the camera stamp, not a silent topic.
