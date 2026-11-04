# LinkedIn draft — Day 26

**Question:** How should a rescue robot transition from SEARCHING to VERIFYING to LOCKDOWN?

**Hero:** `assets/linkedin/01-hero.jpg`

Numbers below are from `./run_smoke.sh` on this machine. Domain 228. The events are the inputs. What was counted is which transitions the coordinator accepted.

---

It saw a shape in the doorway.

That is not a rescue yet.

That is Day 26 of #30DaysOfROS2.

How should a rescue robot transition from SEARCHING to VERIFYING to LOCKDOWN?

The coordinator has three arrows. Seen. Held. Missed.

Seen, then missed. The trace is SEARCHING, VERIFYING, SEARCHING. A confirm offered after that is refused. Lockdown is never entered. The robot may search again.

Seen, then held. The trace is SEARCHING, VERIFYING, LOCKDOWN. Nothing is refused. Navigation is no longer allowed.

Then three more events arrive: seen, missed, and a finished navigation goal. All three are refused. The echoed mission state stays LOCKDOWN.

A glimpse opens a check. A held check opens lockdown. Lockdown has no way back to the hallway.

Day 26 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day26-mission-fsm

#ROS2 #Nav2 #Robotics #Autonomy #BostonDynamics #NVIDIARobotics
