# Investigation C — Predict, then correct the gyro bias

## Question

If the filter slides the guess with the fast wheel speed and the biased gyro, and the wheel yaw rate is allowed to correct the bias, which error goes away?

## Setup

Same wheel samples as A. Same gyro as B. State is `x`, `y`, yaw, and gyro bias. Each step predicts with wheel speed 1.10 m/s and yaw rate `gyro − bias`. The wheel yaw-rate sample then corrects that bias. Measurement variance is `0.05²`.

## Expected

Bias moves toward 0.02 rad/s. Heading stays near the wheel-only heading. Distance stays near 11 m.

## Actual

`assets/C_ekf.log`:

```text
SUMMARY case=ekf x=10.9999 y=0.0766 yaw_deg=0.80 err_x=0.9999 err_y=0.0766 err_yaw_deg=0.80 bias=0.0186 yaw_var=0.0503 frame=odom child=base_link
```

Bias estimate is 0.0186 rad/s. Heading error is 0.80°, close to the wheel-only 0.79°, and far from the gyro-only 11.46°. Along-track error is still 1.000 m.

## Conclusion

The wheel yaw rate made the gyro bias observable, so the heading stopped walking. The wheel scale was still the only distance measurement, so the position stayed long.
