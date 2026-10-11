# LinkedIn draft — Day 18

**Question:** Wheel odometry drifts and IMUs drift — so how does a robot estimate its pose?

---

Wheel odometry drifts and IMUs drift — so how does a robot estimate its pose?

It does not pick a favorite sensor and throw the other one away. It keeps one guess.

The wheels are like counting steps. If each step is a little long, the total is long. The IMU is like feeling a turn. A tiny bias is nothing for a second. After a while that bias is a wrong heading, and a wrong heading turns a straight drive into a curve.

So the robot slides its guess forward, then nudges it. The nudge is stronger when the sensor is trustworthy. That trust number is the covariance.

I ran the same 10 seconds of straight driving three ways. Truth was 10 m, heading unchanged.

- Wheels only, 10% fast: the guess landed at 10.999 m. Heading error was 0.79°.
- Gyro only, a bias of 0.02 rad/s: the heading walked to 11.46° and the path bent 0.998 m sideways.
- Both together: the wheel yaw rate taught the filter the gyro bias (0.0186, truth 0.020). Heading stayed at 0.80°. Distance was still 11.000 m.

The filter covered the gyro’s weak spot. It did not grow a new ruler. Wheel size was still the only distance measurement.

One more trap. Two heading readings, 0° and 11.46°, both claiming to be almost certain, did not meet in the middle. The guess snapped between them 19 times. A tiny covariance can mean “I am sure,” including when I am sure and wrong.

Day 18 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day18-ekf-localization

#30DaysOfROS2 #BostonDynamics #NVIDIARobotics #ROS2 #SensorFusion #Robotics
