# Day 18 — One guess from two drifting sensors

> **Engineering Question**
>
> **Wheel odometry drifts and IMUs drift — so how does a robot estimate its pose?**

---

## The story

The wheels and the IMU are both wrong, and they are wrong in different ways.

Counting wheel speed for 10 seconds of straight driving should land at 10 m. These wheels are 10% fast, so the count lands near 11 m. The heading from the wheels stays near zero, because the yaw-rate noise has no bias.

The gyro says the robot is turning at 0.02 rad/s the whole time. It is not. Integrated alone, that bias becomes 11.46° and almost 1 m of sideways travel.

The filter keeps one guess. It slides that guess forward with the wheel speed and the gyro, and it uses the wheel yaw rate to learn the gyro bias. Heading stays near the wheels. Distance stays near the wheels too. Nothing else in this run measures distance, so the 10% scale error remains.

---

## What the runs showed

Truth is 1.0 m/s straight for 10 s: `x = 10`, `y = 0`, yaw `0°`. The pose is published on `/odometry/filtered` in frame `odom`, child `base_link`.

| Case | What was trusted | Result |
|---|---|---|
| **A** | Wheels only | `x = 10.999 m`, yaw `0.79°`. About 1 m long. Heading stays put. |
| **B** | Gyro only, true speed | yaw `11.46°`, sideways `0.998 m`. The bias became a curve. |
| **C** | EKF: predict from both, correct gyro bias from the wheel yaw rate | yaw `0.80°`, bias estimate `0.0186` (truth `0.020`). `x` is still `11.000 m`. |
| **D** | Two yaw readings, 0° and 11.46°, both with tiny variance | The guess snaps between them **19** times. Variance ends at `1e-6`. |

Same 10 seconds. Fusion fixed the heading walk. It did not invent a ruler.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=180` |
| Message | `nav_msgs/Odometry` on `/odometry/filtered` |

```bash
cd day18-ekf-localization
source ros2_nodes/env.sh
./run_smoke.sh
```

`robot_localization` 3.5.4 is the Humble package whose `ekf_node` runs this predict-then-correct recipe and can publish the `odom` → `base_link` transform. It is not installed on this machine. This day runs a small EKF with the same two steps, so the numbers come from code in this folder.

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | Integrate the fast wheels | Distance is long. Heading is quiet. |
| **B** | Integrate the biased gyro | Heading walks to 11.46°. The path bends sideways. |
| **C** | EKF learns the gyro bias | Heading matches the wheels. The scale error stays. |
| **D** | Two certain, disagreeing yaws | The guess snaps. A tiny variance does not mean it is right. |

Details: `investigations/`.

---

## Key learnings

- A pose estimate is one guess. Slide it forward, then nudge it by how much you trust the new measurement.
- Covariance is that trust. Small means pull hard. Large means almost ignore it.
- The gyro bias was observable because the wheels still reported an unbiased yaw rate. The filter learned `0.0186` rad/s against a true `0.020`.
- A constant wheel-scale error is not fixed by a gyro. Position stayed about 1 m long.
- Two measurements that disagree, both with tiny variance, do not blend. The guess jumps, and the variance can still look tiny.

Day 16 showed a wheel sum can be the wrong distance from the first step. This day asks the gyro to help the heading, and shows what that help does not cover.
