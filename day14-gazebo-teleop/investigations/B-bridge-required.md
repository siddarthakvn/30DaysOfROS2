# Investigation B — Gazebo does not hear ROS by itself

## Hypothesis

**H3:** With Gazebo Harmonic running and no `ros_gz_bridge`, a ROS publisher on `/model/vehicle_blue/cmd_vel` is invisible on Gazebo Transport.

## Setup

- `gz sim -s -r` on `/usr/share/gz/gz-sim8/worlds/diff_drive.sdf`
- `key_twist.py` publishing the forward Twist
- Bridge **not** started

## Actual results

Evidence: [`../assets/B.log`](../assets/B.log)

| Side | Observed |
|---|---|
| ROS | Publisher count **1**, node `key_twist`. Subscription count **0** |
| Gazebo Transport | **No publishers** on `/model/vehicle_blue/cmd_vel`. The diff-drive model is already subscribed as `gz.msgs.Twist` |

## Conclusion

**Supported.** The simulator is waiting for a Gazebo Transport Twist. The ROS publisher is a different network until the bridge joins them.
