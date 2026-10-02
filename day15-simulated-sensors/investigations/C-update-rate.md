# Investigation C — How often a new scan exists

## Question

Does `update_rate` change the distance, or only how often a scan arrives?

## Setup

`worlds/wall_slow.sdf` is the perfect sensor again, with `<update_rate>1</update_rate>` instead of 5.

## Expected

Ranges stay identical. The message rate drops from about 5 Hz to about 1 Hz.

## Actual

`assets/C_slow.log`:

```text
SUMMARY scans=4 hz=0.99 max_abs_diff_m=0.000000 center_mean_m=1.9006
```

Same center distance as Investigation A. Same zero difference. About one scan per second.

## Conclusion

Rate and noise are different knobs. Slowing the sensor did not add error. Adding noise in Investigation B did not change the rate.
