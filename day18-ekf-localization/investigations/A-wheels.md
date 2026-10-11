# Investigation A — Wheels only

## Question

If the wheel speed is 10% high and the wheel yaw rate is only noisy, where does the wheel sum end?

## Setup

Truth is 1.0 m/s straight for 10 s. The wheel speed used in the sum is 1.10 m/s. Wheel yaw rate is zero-mean noise, standard deviation 0.05 rad/s, seed 18. No gyro.

## Expected

Distance near 11 m. Heading stays near 0°.

## Actual

`assets/A_wheels.log`:

```text
SUMMARY case=wheels x=10.9989 y=0.1279 yaw_deg=0.79 err_x=0.9989 err_y=0.1279 err_yaw_deg=0.79 frame=odom child=base_link
```

The sum is 0.999 m too long. Heading error is 0.79°. Sideways error is 0.128 m, from the yaw-rate noise adding up.

## Conclusion

The wheels drift in distance because every step uses the fast speed. They do not walk the heading off, because that noise has no bias.
