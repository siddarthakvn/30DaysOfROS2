# Investigation B — The same wall, with noise

## Question

Does Gaussian range noise change the reading while the wall stays put?

## Setup

`worlds/wall_noisy.sdf` is the same rig as Investigation A, plus:

```xml
<noise>
  <type>gaussian</type>
  <mean>0.0</mean>
  <stddev>0.05</stddev>
</noise>
```

Update rate stays 5 Hz.

## Expected

The center beam stays near 1.90 m. Consecutive scans are no longer identical.

## Actual

`assets/B_noisy.log`:

```text
SUMMARY scans=15 hz=4.96 max_abs_diff_m=0.222997 center_mean_m=1.9043
```

The rate did not change. The largest jump on any beam, from one scan to the next, was 0.223 m. The center of the scan stayed on the wall.

0.223 m is the worst beam in the window, not the typical error. The standard deviation asked for was 0.05 m. A few beams in a 3 second window land farther out than that. That is what a Gaussian tail looks like.

## Conclusion

The wall did not move. The number did. A stop rule written against an exact 1.90 m scan is now looking at a moving number.
