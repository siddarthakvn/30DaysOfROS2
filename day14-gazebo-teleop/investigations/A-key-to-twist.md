# Investigation A — The key is a Twist

## Hypothesis

**H1 / H2:** The forward key sets `linear.x > 0` and `angular.z = 0`. A turn key sets `angular.z`. Stop sets both to 0. The publisher does not emit joint commands.

## Setup

`key_twist.py` imports `moveBindings` from the installed `teleop_twist_keyboard` (default speed `0.5`, turn `1.0`).

| Key | Binding |
|---|---|
| `i` | forward |
| `j` | yaw |
| `k` | not in the map, so stop |

## Actual results

Evidence: [`../assets/A.log`](../assets/A.log)

| Key | Published Twist | Echoed Twist |
|---|---|---|
| `i` | `linear.x=0.500` `angular.z=0.000` | same |
| `j` | `linear.x=0.000` `angular.z=1.000` | same |
| `k` | all zeros | all zeros |

## Conclusion

**Supported.** The key selects a body velocity. Nothing in this step turns a wheel.
