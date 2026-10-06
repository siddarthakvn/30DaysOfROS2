# Interview questions — Day 16

## 1. How does wheel rotation become a robot position?

Each wheel's contact speed is its spin rate times its radius. The average of the two speeds is forward speed. Their difference, divided by the track width, is yaw rate. Add that motion up over time and you get `x`, `y`, and yaw.

## 2. What happens if both wheels spin the same way?

The robot drives straight. In this run, 5 rad/s on a 0.10 m wheel for 2 s became `x = 1.000` m and yaw `0°`.

## 3. What happens if the wheels spin opposite ways?

The center stays put and the heading changes. Forward speed is zero. Yaw rate is not.

## 4. Why can world `y` change while body sideways speed stays zero?

After a turn, "forward" is no longer along world `x`. The wheels are still driving forward in the body. They are not sliding sideways.

## 5. Why does a wrong wheel radius matter?

The same spin is multiplied by the wrong radius, so every step of the sum is scaled. Here a 0.11 m radius instead of 0.10 m turned a 1.000 m straight run into 1.100 m.

## 6. Is odometry the map position?

No. It is the wheel sum in the `odom` frame. REP-105 says that pose may drift. A later correction belongs in `map`, not as a jump inside `odom`.
