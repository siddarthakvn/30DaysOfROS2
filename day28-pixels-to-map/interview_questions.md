# Interview questions — Day 28

## 1. YOLO gives a pixel. Why can Nav2 not use that directly?

Nav2 plans in meters on a map. A pixel is a location on an image. Those are different spaces.

## 2. What three pieces turn a pixel into a map point?

Depth for distance. Camera intrinsics for a 3D point in the camera frame. TF2 to walk that point into `map`.

## 3. What did the wrong-depth run show?

Same pixel as the good run. Depth forced to 1.0 m. Map error became 0.75 m. The box in the image did not move. The distance did.

## 4. What happens if you skip TF?

The point stays in `camera_optical`. In this run that was `(0.000, 0.150, 1.750)`, about 2 m away from the true map pose.

## 5. The robot moved 0.5 m and the pixel updated. Why was the map point still wrong?

The code still used the old camera→map transform. New image, stale pose, 0.50 m map error.
