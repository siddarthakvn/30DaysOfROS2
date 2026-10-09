# Day 17 — References

## Primary

1. **control_toolbox::Pid — ROS 2 Humble**  
   https://control.ros.org/humble/doc/api/classcontrol__toolbox_1_1Pid.html  
   Command is P + I + D. Error is desired minus measured. D uses the change in error over the time step. I accumulates and can be clamped (anti-windup). This day's script uses that split of jobs. D is applied to turn rate, which is the stored speed that carries the heading past the target.

2. **A heading with inertia**  
   With no damping, acceleration proportional to angle error is a harmonic oscillator: the mass (here, turn rate) coasts through the setpoint. Derivative gain is the damper.

## This repository

- Day 16 — wheel speeds become a heading. This day commands the turn that heading should make.

## Limit

The plant is a one-angle simulation, not a robot with wheel slip, delay, or a noisy gyro. I is left at 0 so the swing can be attributed to P and stored turn rate.
