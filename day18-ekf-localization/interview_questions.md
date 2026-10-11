# Interview questions — Day 18

## 1. Both the wheels and the IMU drift. How does the robot still estimate its pose?

It keeps one guess. It slides that guess forward with the motion it has, then nudges it when a measurement arrives. How hard it nudges depends on the covariance. A small number means trust that measurement. A large number means almost ignore it.

## 2. What did the wheels alone do in this run?

Ten seconds at a speed that was 10% high. The sum landed at 10.999 m instead of 10 m. Heading error was 0.79°.

## 3. What did the gyro alone do?

It reported 0.02 rad/s while the robot was not turning. After 10 s the heading was 11.46° off and the path had bent 0.998 m sideways.

## 4. What did the filter fix, and what did it leave wrong?

It learned a gyro bias of 0.0186 rad/s, close to the true 0.020, so the heading stayed at 0.80°. Distance was still about 11 m. A gyro does not measure wheel size.

## 5. Why is a tiny covariance not always good news?

Two yaw readings, 0° and 11.46°, both with variance `1e-6`, made the guess snap between them 19 times. The variance at the end was still `1e-6`. Sure and wrong can happen together.
