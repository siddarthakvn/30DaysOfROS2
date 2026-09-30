# LinkedIn draft — Day 14

**Question:** I pressed one keyboard key. How did that make a simulated robot move?

When you paste this into LinkedIn, delete the words `@Boston Dynamics`, type `@`, and choose the **Boston Dynamics** company page. A pasted name does not notify them. The mention does.

---

I pressed one key.

The robot moved.

The key did not touch a motor.

That is Day 14 of #30DaysOfROS2.

**I pressed one keyboard key. How did that make a simulated robot move?**

`i` is not a joint command.
It is a body velocity.

`teleop_twist_keyboard` writes a `Twist` on `/cmd_vel`:

• forward key → `linear.x = 0.5` m/s  
• turn key → `angular.z = 1.0` rad/s  
• stop key → both back to zero  

Gazebo does not subscribe to that ROS topic.

I watched it. ROS had a publisher. Gazebo Transport had **no publisher** on `/model/vehicle_blue/cmd_vel`. The diff-drive model was already waiting on the other side of a different network.

`ros_gz_bridge` is the crossing.

ROS `Twist` in.
Gazebo `Twist` out.
Then the plugin splits one forward speed and one yaw rate across two wheels.

On this machine that is Gazebo Harmonic, not the Fortress example in the Humble tutorial. Same contract. Different message package: `gz.msgs.Twist`.

Measured:

• key `i` → pose **x = 0 → 1.71 m**  
• after a real stop, `linear.y = 0.5` → **x and y stay put**  

A diff-drive robot cannot strafe. The message can still say `linear.y`. The plugin spends `linear.x` and `angular.z`.

This is the same idea behind a real mobile base. @Boston Dynamics publishes a ROS driver for Spot where base teleop is still a body-velocity command. The keyboard is the teaching version. The robot never sees the key.

One key.
One Twist.
Two wheels.

Day 14 / #30DaysOfROS2

Repo: https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day14-gazebo-teleop

#ROS2 #Robotics #Gazebo #Teleop #Spot #BostonDynamics #30DaysOfROS2
