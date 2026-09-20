# LinkedIn draft — Day 07

**Status:** Ready to post after you reveal this day publicly (`publish-day.sh` when you choose).

**Curriculum question:** Can the wrong QoS policy silently break a robotic system?

**Alternate:** Why can two ROS 2 nodes be connected, yet messages still never arrive?

**Day 08 teaser:** What happens when one callback blocks an entire ROS 2 node?

---

## Copy-paste post

My nodes found each other.
My messages never did.

That’s the silent failure I was hunting.

Publisher: alive. Publishing.
Subscriber: alive. Waiting.
Topic: in the graph.
Discovery: working.

And the stream? Dead quiet.

Not because the network failed.
Not because the callback was slow.
Because they never really matched.

ROS 2 doesn’t only ask:
“Are you on the same topic?”

It also asks:
“Do your QoS contracts agree?”

Same topic.
Wrong reliability.
No data path.

BEST_EFFORT on one side.
RELIABLE on the other.
They can see each other…
and still refuse to talk.

That is how a robot breaks without crashing:

- `ros2 topic list` looks fine
- nodes look fine
- logs look mostly fine
- your perception pipeline just… never starts

So today’s question isn’t “What is QoS?”

It’s this:

Can the wrong QoS policy silently break a robotic system?

Yes.
Because discovery finds nodes.
QoS decides whether they’re allowed to exchange data.

Bigger queue was Day 03’s trap.
Wrong QoS is Day 07’s trap:

You feel connected.
You’re not.

Day 07 / #30DaysOfROS2

Evidence:
https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day07-qos

Tomorrow: if one callback freezes… what happens to the rest of the node?

Have you ever stared at a “live” topic that published forever and received nothing?

---

## Hero image prompt

```text
Editorial robotics photography, clean and realistic, not sci-fi.
A small wheeled lab robot on a workbench next to an open laptop.
On the laptop screen: a simple ROS graph with two nodes connected by a dashed topic line, and a clear red X or broken link in the middle of that line.
Between the robot’s camera and the laptop, a few floating message packets are stalled mid-air, never arriving.
Warm workshop lighting, shallow depth of field, subtle cable clutter, whiteboard with “QoS?” faintly visible in the background.
Muted industrial colors: charcoal, steel blue, soft amber light. No neon, no holograms, no futuristic city, no glossy CGI robot.
Photorealistic, LinkedIn hero banner crop, 16:9, high detail, serious engineering mood.
```
