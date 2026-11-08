# Day 27 — The box became a message

> **Engineering Question**
>
> **Running YOLO is easy — but how do you make perception part of a ROS 2 system?**

---

## The story

A detector can draw a box and still leave the rest of the robot deaf. The box has to become a message another node can subscribe to.

Three nodes, one frame at a time:

- **Camera.** `front_camera` publishes `sensor_msgs/Image` on `/front/image_raw`. Frame id `front`. Encoding `bgr8`. It does not know what is in the picture.
- **Detector.** `yolo_detector` takes that image through `cv_bridge`, runs YOLOv8n with OpenCV DNN, and publishes `vision_msgs/Detection2DArray` on `/detections`. The detection header is the image header.
- **Ear.** `mission_ear` reads `/detections`. It publishes `SEEN` on `/mission_event` only when the best `class_id` is `person` and the score is at least 0.50.

The same street photo is used twice. Once the boxes stay inside the detector process. Once they are published. A flat gray frame goes through the full graph so an empty message can be told apart from a person.

The street photo and the `yolov8n.onnx` weights are downloaded by `fetch.sh` and are not in git. The scores below are from `./run_smoke.sh` on this machine. The 0.92 drawn on the hero image is the picture, not this run.

---

## What the runs showed

Domain `227`. Score line for SEEN is `0.50`. The street frame is 810×1080. The blank frame is 640×480.

| Case | What ran | Best person | `/mission_event` |
|---|---|---|---|
| **A** screen | YOLO in one process. No publishers | **0.890** | topics unknown |
| **B** blank | camera, detector, ear | **0.000** | echo returned no data |
| **C** street | camera, detector, ear | **0.890** | `data: SEEN` |

A found the same four people and one bus as C, and published none of them. `/front/image_raw`, `/detections`, and `/mission_event` were unknown topics.

B published a real image and a real detection message. The array was empty. `stamp_match=1` on frame `front`. `seen=0`.

C published five detections on that same stamp: person 0.890, person 0.883, person 0.878, bus 0.843, person 0.436. The ear said SEEN because the best person is 0.890. The bus does not count. The 0.436 person is in the message and is under the line.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=227` |
| Vision | `cv_bridge`, OpenCV DNN, YOLOv8n ONNX (`ultralytics/assets` v8.4.0) |
| Messages | `sensor_msgs/Image`, `vision_msgs/Detection2DArray`, `std_msgs/String` |

```bash
cd day27-perception-yolo
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=227
```

---

## Quick start

Weights and the street photo download into gitignored folders:

```bash
cd day27-perception-yolo
./fetch.sh
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=227
```

One frame on the wire:

```bash
python3 ros2_nodes/camera.py --ros-args -p scene:=street
python3 ros2_nodes/detector.py --ros-args -p scene:=street
python3 ros2_nodes/ear.py --ros-args -p scene:=street
```

`scene` is `street` or `blank`.

All three investigations:

```bash
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | Boxes drawn, nothing published | Best person 0.890. Three topics unknown |
| **B** | Gray frame through the whole graph | Empty detection array. No SEEN |
| **C** | Street frame through the whole graph | Same stamp. Echo `SEEN` |

Details: `investigations/`.

---

## Key learnings

- A score inside the detector process is not a ROS message. In A the best person was already 0.890, and `ros2 topic info` reported all three topics unknown.
- `cv_bridge` is the step from `sensor_msgs/Image` (`bgr8`) to the array YOLOv8n reads. The camera node never calls the model.
- `/detections` is `vision_msgs/Detection2DArray`. Each box has `class_id`, `score`, and a `BoundingBox2D` center and size in pixels. This demo puts the COCO name in `class_id` so the ear can read it without a side table.
- The detection header copies the image stamp and `frame_id`. In B and C, camera, detector, and ear printed the same `stamp_sec`, `stamp_nsec`, and `frame=front`. `stamp_match=1`.
- SEEN is a filter on that message: `class_id` person and score at least 0.50. The bus at 0.843 stayed in the array and did not become the event. The person at 0.436 stayed in the array and is under the line.
- An empty `Detection2DArray` is still a message. In B the echo showed `detections: []` and `/mission_event` had no data. Quiet is a result, not a missing node.
- The image and the detections are latched (`RELIABLE`, `TRANSIENT_LOCAL`, depth 1) because this experiment publishes one frame and then echoes it. A streaming camera is a different QoS choice. This run did not measure that.
- Day 26's coordinator accepts the string `SEEN`. This day publishes that string. It does not run the coordinator.

Day 26 decided which mission events are legal. Day 27 is how a camera frame becomes the event those rules can hear.
