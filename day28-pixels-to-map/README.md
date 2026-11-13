# Day 28 — The pin is on the floor

> **Engineering Question**
>
> **YOLO gives pixels. Nav2 needs map coordinates. How do we connect them?**

---

## The story

A box in the picture is a column and a row. Nav2 plans in meters, in the `map` frame. Three facts turn the pixel into a goal.

- **Lens.** `sensor_msgs/CameraInfo` and `image_geometry` turn the pixel into a ray in `camera_optical_frame`.
- **Depth.** Optical-axis Z picks the point along that ray. This run is given that depth. It does not estimate it from the picture.
- **Camera pose.** TF2 carries the point from `camera_optical_frame` through `camera_link` and `base_link` into `map`.

The surveyed box is at `(3.500, 2.200, 0.250)` m. The robot base is at `(1.00, 2.00, 0.00)`, facing `+x`. The camera link is `0.20` m forward and `0.30` m up. The optical frame uses the usual image axes: x right, y down, z forward.

Same pixel in every run. Column `276.522`, row `250.870`. Depth `2.300` m.

---

## What the runs showed

Domain `226`. Intrinsics `fx = fy = 500`, principal point `(320, 240)`, image `640×480`, no distortion.

| Case | What ran | Published goal | Error |
|---|---|---|---|
| **A** pixel | camera, pixel, depth | none | no map point |
| **B** origin | ray, then the camera numbers labeled `map` | `(-0.200, 0.050, 2.300)` | **4.745 m** |
| **C** map | ray, then TF into `map` | `(3.500, 2.200, 0.250)` | **0.000 m** |

A echoed the pixel and the depth. `/point_camera`, `/point_map`, and `/goal` were unknown topics.

B and C both recover the camera-frame point `(-0.200, 0.050, 2.300)`. B publishes those numbers with `frame_id: map` and `used_tf=0`. The goal is `4.744997` m from the box. C looks up `map → camera_optical_frame`. The camera origin in the map is `(1.200, 2.000, 0.300)`. The goal lands on the surveyed box. `error_m=0.000000`.

`tf2_echo map camera_optical_frame` reported translation `[1.200, 2.000, 0.300]` and quaternion `[-0.500, 0.500, -0.500, 0.500]`.

The pixel, the camera point, the map point, and the goal share one stamp. In C that stamp is `1794543239.032370236`.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=226` |
| Geometry | `image_geometry`, `tf2_ros` |
| Messages | `sensor_msgs/CameraInfo`, `geometry_msgs/PointStamped`, `geometry_msgs/PoseStamped` |

```bash
cd day28-pixels-to-map
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=226
```

---

## Quick start

The chain that lands on the box:

```bash
cd day28-pixels-to-map
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=226

python3 ros2_nodes/scene.py
python3 ros2_nodes/ray.py
python3 ros2_nodes/placer.py --ros-args -p mode:=map
```

`mode` is `map` or `origin`.

All three investigations:

```bash
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | Pixel and depth only | Column 276.522, row 250.870. No goal |
| **B** | Camera point written as a map point | Goal 4.745 m from the box |
| **C** | Same point through TF | Goal on the box. Error 0.000 m |

Details: `investigations/`.

---

## Key learnings

- A pixel is a direction once the camera model is known. Column `276.522` and row `250.870` become the ray that `image_geometry` turns into `(-0.200, 0.050, 2.300)` m at depth `2.300`.
- That point is still in `camera_optical_frame`. Publishing it with `frame_id: map` does not move it. In B the goal sat at the camera numbers and missed the box by `4.744997` m.
- TF is the step onto the map. The optical frame's origin is at `(1.200, 2.000, 0.300)` in the map: the base at `(1.00, 2.00, 0.00)` plus the camera offset `(0.20, 0.00, 0.30)`. After that transform the goal is `(3.500, 2.200, 0.250)`.
- The optical rotation in the echo is `-90, 0, -90` degrees. Image x is right and image y is down. The robot's x is forward. The static transform is what connects them.
- Depth here is Z along the optical axis, supplied as `/depth`. A range along the ray is a different number. This day does not compute depth from a picture.
- The zero error is a round trip through a camera and a TF tree we defined. It shows the chain is consistent. It does not show a detector finding a box in a photo, and it does not send `NavigateToPose`.
- `/goal` is a latched `geometry_msgs/PoseStamped` in `map`. Day 21 is what happens after a goal is sent. This day stops when the goal exists.

Day 27 made a detection the mission can hear. Day 28 turns one pixel of that kind of detection into a coordinate Nav2 can take as a goal.
