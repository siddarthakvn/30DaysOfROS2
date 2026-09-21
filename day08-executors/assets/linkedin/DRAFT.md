# LinkedIn draft — Day 08

**Status:** Ready to post after you reveal this day publicly (`publish-day.sh` when you choose).

**Curriculum question:** What happens when one callback blocks an entire ROS 2 node?

**Concrete:** Your LiDAR callback takes 500 ms. Your IMU needs 10 ms. Does the IMU still run?

**Day 09 teaser:** Can I tune a robot without restarting its ROS 2 nodes?

---

## Image

| Slide | File | Caption idea |
|:---:|---|---|
| 1 | *(optional)* | One slow callback. Whole node goes quiet — until callback groups. |

---

## Copy-paste post

My LiDAR callback slept for 500 ms.

My IMU needed 10 ms.

So… did the IMU still run?

That depends less on DDS than most people think.

In ROS 2, the node does not “run” callbacks.
The **executor** does.

On a SingleThreadedExecutor:

- LiDAR starts sleeping
- IMU stops
- control timer stops
- ~500 ms hole in the timeline

Measured:

- IMU `during_lidar = 0`
- IMU `max_gap ≈ 508 ms`

Then I enabled MultiThreadedExecutor.

Nothing changed.

Why?

Everything still shared one MutuallyExclusive callback group.
Threads existed. The group said: only one callback at a time.

Measured again:

- still `during_lidar = 0`
- still `max_gap ≈ 515 ms`

Then I gave IMU, control, and LiDAR **separate** callback groups.

Same 500 ms LiDAR sleep.
Different robot:

- IMU `during_lidar = 200`
- IMU `max_gap ≈ 10.5 ms`
- control kept its 20 ms period
- `max_active_callbacks = 2`

The slow callback was still slow.
The rest of the node got to live.

So today’s question isn’t “What is an executor?”

It’s this:

What happens to an entire ROS 2 node when one callback takes too long?

It can starve — even when topics match and QoS is fine —
unless you design **threads + callback groups** on purpose.

DDS delivers the message.
The executor decides whether anyone is free to handle it.

Day 08 / #30DaysOfROS2

Evidence:
https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day08-executors

---

## Hashtags

#ROS2 #Robotics #DDS #Executors #Concurrency #30DaysOfROS2
