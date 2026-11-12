# Day 28 — Pixels to map

> **Engineering Question**
>
> **YOLO gives pixels. Nav2 needs map coordinates. How do we connect them?**

---

## The story

A detection box is a place on an image. Nav2 needs a place on the floor.

The bridge has three pieces. Depth turns the pixel into a ray with length. Camera geometry turns that ray into a 3D point in the camera frame. TF2 walks that point into the map frame.

Miss depth, and the same pixel can be a near box or a far box. Miss TF, and the number still lives next to the lens. Miss an updated robot pose, and yesterday’s camera location stamps today’s pixel into the wrong map cell.

---

## What the runs showed

Truth is a box at map `(2.000, 0.000, 0.150)`. The camera sits at `(0.25, 0, 0.30)` in that same frame. The point is published on `/detection/map_point`.

| Case | What was used | Result |
|---|---|---|
| **A** | Pixel + true depth + camera→map TF | `map = (2.000, 0.000, 0.150)`. `err_xy = 0.000 m` |
| **B** | Same pixel, depth guessed as `1.0 m` | `map_x = 1.250`. `err_xy = 0.750 m` |
| **C** | Pixel + depth, no TF | Point stays in `camera_optical`: `(0.000, 0.150, 1.750)`. `err_xy = 2.006 m` |
| **D** | Robot moved `+0.50 m` in x; old TF still used | `map_x = 1.500`. `err_xy = 0.500 m` |

Same box. The pixel alone never named the map cell.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=28` |
| Message | `geometry_msgs/PointStamped` on `/detection/map_point` |

```bash
cd day28-pixels-to-map
source ros2_nodes/env.sh
./run_smoke.sh
```

On a full stack, TF2 carries `camera_optical` → `base_link` → `map`, and depth comes from a depth image or stereo. This day runs the same three steps in one script so the numbers stay reproducible without a live camera.

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | Full pipeline | Pixel becomes the true map point |
| **B** | Wrong depth | Same pixel, 0.75 m short |
| **C** | No TF | The point never leaves the camera |
| **D** | Stale robot pose | New pixel, old transform, 0.50 m error |

Details: `investigations/`.

---

## Key learnings

- A YOLO pixel is a direction in the image. It is not a map pose.
- Depth gives the ray a length. Intrinsics turn that into a camera-frame point.
- TF2 renames that point into `map`. Without it, Nav2 is still looking at the lens.
- A correct pixel with a stale robot pose is still the wrong map cell.

Day 27 puts a detection on a topic. Day 12 named the frames. This day is the bridge between “I see it” and “I can drive to it.”
