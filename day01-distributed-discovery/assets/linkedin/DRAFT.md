# LinkedIn draft — Day 01

**Status:** Draft only. Do not post until (1) Day 01 docs feel final to you, (2) local git checkpoint is what you want, (3) you have run `./scripts/publish-day.sh 1` (or equivalent) so the GitHub link is live.

**Curriculum question:** How do ROS 2 nodes find each other without a ROS Master?

**Day 02 teaser (locked):** Should every sensor be a separate ROS 2 node?

---

## Image order (carousel)

| Slide | File | Caption idea (short) |
|:---:|---|---|
| 1 | `assets/linkedin/hero-q-a-diagram.png` | Hero: question → no Master → DDS/RMW → same vs different `ROS_DOMAIN_ID` |
| 2 | `assets/expA_talker_without_listener.png` + `assets/expA_listener_joined.png` | A: talker alone → listener joins; matching `/chatter` counts |
| 3 | `assets/expB_independent_ros_graphs.png` | B: domain 10 → `/talker`; domain 20 → `/listener` (`ros2 daemon stop`) |
| 4 | `assets/expC_before_listener.png` → `expC_after_listener_joined.png` → `expC_after_listener_exit.png` | C: graph join/leave; talker never restarts |

Do not lead with `middleware_verification.png` on LinkedIn.

---

## ChatGPT prompt — hero image

Copy everything inside the fence into ChatGPT (image generation):

```text
Create a single LinkedIn carousel hero image (landscape, 16:9, high resolution, sharp text).

Purpose: technical engineering poster for a ROS 2 series post — NOT a marketing flyer, NOT a dashboard, NOT an infographic with many cards.

Composition (one unified scene):
- Top / hero: large readable title exactly:
  "How do ROS 2 nodes find each other without a ROS Master?"
- Subtitle under it in smaller text:
  "Day 01 / 30  ·  Ubuntu 22.04  ·  ROS 2 Humble  ·  Fast DDS (rmw_fastrtps_cpp)  ·  localhost"

Middle: two-column contrast on the same background plane (no floating cards, no drop shadows stacks):

LEFT column labeled "ROS 1":
- Central box: "ROS Master (roscore)"
- Two smaller node boxes connected only through the Master
- Caption: "Centralized discovery"

RIGHT column labeled "ROS 2":
- Two peer node boxes: "talker" and "listener"
- Direct peer link labeled "DDS discovery via RMW"
- Small note: "same ROS_DOMAIN_ID"
- Caption: "Distributed discovery"

Bottom answer strip (full width, high contrast, bold):
"Same ROS_DOMAIN_ID → discover    |    Different ROS_DOMAIN_ID → silent isolation"

Tiny footer:
"#30DaysOfROS2  ·  no Master  ·  RMW → Fast DDS  ·  evidence: demo_nodes_cpp"

Style:
- Dark charcoal / deep navy technical background with subtle grid or circuit texture (not neon purple glow)
- Clean sans-serif engineering typography, high contrast white/light gray text
- Teal or amber accent for arrows and the answer strip only
- Minimal icons (nodes as rounded rectangles, not cute robots)
- No emojis, no 3D glossy balloons, no stock photo of a robot, no QR code, no fake UI chrome
- Text must be crisp and legible at LinkedIn feed size
- Leave safe margin so nothing is cropped on mobile

Output: one polished diagram image suitable as slide 1 of a technical LinkedIn carousel.
```

Save the result as:

`day01-distributed-discovery/assets/linkedin/hero-q-a-diagram.png`

---

## Post copy (more technical)

```text
Day 01 of #30DaysOfROS2

Engineering question:
How do ROS 2 nodes find each other without a ROS Master?

In ROS 1, discovery depended on a centralized registry: roscore / the ROS Master. Nodes registered publishers and subscribers there. No Master → no graph.

ROS 2 removes that process. Discovery is peer-oriented: client libraries talk through RMW into a DDS implementation. On Humble, the default here was Fast DDS (rmw_fastrtps_cpp). Participants on the same ROS_DOMAIN_ID advertise endpoints; compatible pub/sub pairs match without a central name server.

I verified that with three minimal experiments — not a tutorial walkthrough of Hello World, but a check of the discovery claims.

Stack: Ubuntu 22.04 · ROS 2 Humble · Fast DDS · demo_nodes_cpp talker/listener · single host.

———

Investigation A — Automatic discovery (same domain)

Hypothesis: on ROS_DOMAIN_ID=10, talker and listener discover each other with no Master and no manual peer list.

Procedure:
1. Start talker alone on /chatter
2. Start listener later on the same domain
3. Inspect with ros2 node list / ros2 topic info (same sourced env + same domain)

Observation:
- Talker published with zero subscribers (no wait, no error)
- Listener joined without restarting the talker
- Message sequence numbers matched after join
- Default demo QoS is volatile — late joiners get new samples, not a replay of history

So: discovery + data path worked on one machine without roscore.

———

Investigation B — Domain isolation (one variable changed)

Controlled variable: ROS_DOMAIN_ID only.

Talker → 10
Listener → 20

Same laptop, same Humble install, same RMW, same topic name.

Observation:
- No “I heard …” on the listener
- No crash, no explicit “domain mismatch” error — isolation is silent
- After ros2 daemon stop (required when switching domains for CLI correctness):
  domain 10 → /talker only
  domain 20 → /listener only

Engineering takeaway: ROS_DOMAIN_ID is the DDS domain boundary for discovery. A wrong domain looks like “nothing is publishing,” which is a common debugging trap.

———

Investigation C — Dynamic ROS Graph

Monitored with: watch -n 1 ros2 node list (domain 10)

Sequence:
- talker only → graph shows /talker
- start listener → /talker + /listener
- Ctrl+C listener → /talker again

Talker never restarted. Leave is not necessarily instantaneous — participant liveliness / lease can lag a short time after SIGINT before the CLI view updates. The graph is a live view of discovered participants, not a static Master table.

———

Mental model I am carrying forward

Application (rclcpp/rclpy)
  → rcl
    → rmw
      → Fast DDS
        → distributed discovery + transport

ROS_DOMAIN_ID selects who is even eligible to discover you.
QoS decides how matched endpoints behave (reliability, durability, history) — deeper on Day 07.

Limits of today’s evidence (important):
- localhost only
- Humble Fast DDS default multicast
- no Docker / VPN / multi-subnet / Discovery Server case

Those environments can need extra discovery config. This day does not claim “zero network configuration everywhere.”

———

Why it matters

Discovery architecture decides whether your robot software has a single point of failure for “who is out there,” and how painful bring-up and debugging become.

On a real shared network — lab benches, competition Wi-Fi, warehouse APs — many processes may speak ROS 2. Without domain discipline, fleets and teams can silently see each other’s topics, collide on names, or debug the wrong graph. With the wrong ROS_DOMAIN_ID, you get the opposite failure mode: everything looks healthy locally, and nothing connects.

Dynamic join/leave matters because robots are not batch jobs. Drivers, sensors, autonomy PCs, and teleop clients start in different orders and crash independently. If discovery required a Master that must be up first — or forced a full-system restart when one node dies — modular multi-process robotics becomes fragile.

ROS_DOMAIN_ID is a small environment variable with a large operational effect: it is how you carve independent DDS domains on one physical network. Combined with RMW/DDS discovery, it is part of why ROS 2 can support multi-robot and multi-team deployments without a ROS 1-style central registry — provided you treat domain ID, daemon state, and network constraints as first-class engineering concerns, not afterthoughts.

———

Full write-up, Expected vs Actual, and screenshots:

https://github.com/siddarthakvn/30DaysOfROS2

Path: day01-distributed-discovery/

If you reproduce and get a different result (especially across machines or Docker), that is useful signal — share it.

———

From these three experiments, we get the answer to today’s engineering question:

How do ROS 2 nodes find each other without a ROS Master?

They don’t ask a central registry. On the same ROS_DOMAIN_ID, DDS (behind RMW) does distributed discovery. Different domain → silent isolation. The ROS Graph updates as nodes join and leave — no roscore required.

———

Day 01 / 30 ✅

Tomorrow’s question:
Should every sensor be a separate ROS 2 node?

#30DaysOfROS2 #ROS2 #Robotics #DDS #RMW #RobotOperatingSystem #RoboticsEngineering #LearningInPublic
```

---

## Checklist before you hit Post

- [ ] Hero PNG saved as `assets/linkedin/hero-q-a-diagram.png`
- [ ] Claims match screenshots (no universal “zero config network”)
- [ ] Day 02 line matches curriculum
- [ ] GitHub Day 01 visible on `origin/main` after publish ritual
- [ ] You accept Expected vs Actual honesty notes in A/B
