# LinkedIn assets — Day 03

**Post when:** docs final + git checkpoint + GitHub day visible (your call).

Draft copy: [DRAFT.md](DRAFT.md)

## Carousel suggestion

| Order | File | Story |
|:---:|---|---|
| 1 | `hero-reality-queue.png` | Sci-fi hero — reality vs robot understanding |
| 2 | `../B1_depth1.png` | depth 1 → fresher |
| 3 | `../B2_depth10.png` | depth 10 → late |

---

## Hero image prompt (copy into ChatGPT / image gen)

```text
Create a single LinkedIn carousel hero image (landscape 16:9, high resolution, sharp readable text).

Tone: hard sci-fi about REALITY itself — cinematic, cold, serious.
Think: a cracked timeline / light-cone of the present, a robot trying to pause the universe and failing.
NOT neon cyberpunk purple glow, NOT cute robot stock art, NOT busy dashboard cards, NOT emojis, NOT QR codes.

Background: deep void black with faint starfield and a thin luminous “present moment” horizon line cutting across the frame (like a light-sheet of NOW). Subtle volumetric light. High contrast ivory/white typography. One accent color only: cold cyan OR amber — not both.

TOP TITLE (large, crisp, exact text):
"I asked reality to wait. It didn’t."

SUBTITLE (smaller, muted):
"Day 03 / 30  ·  #30DaysOfROS2  ·  topics · queues · staleness"

MIDDLE — one unified experiment diagram (same plane, no floating card stack):

LEFT block labeled "REALITY / SENSOR":
- A rushing stream of frame slabs labeled 1…30… labeled "30 Hz firehose"
- Arrow right: "publishes faster than you think"

CENTER block labeled "ROS 2 QUEUE (KEEP_LAST)":
- Two vertical buffers side by side for contrast:
  - "depth = 1"  → short stack, caption "~3 behind NOW"
  - "depth = 10" → tall stack of older frames fading into grey, caption "~12 behind NOW"
- Small note under center: "buffers → drops oldest → processes the past"

RIGHT block labeled "ROBOT BRAIN":
- A slower processor/core labeled "~10 Hz (100 ms think)"
- Dim ghost silhouette of the robot acting on an OLD frame while the bright NOW line has already moved ahead
- Caption: "busy… but late"

BOTTOM ANSWER STRIP (full width, bold, high contrast):
"Bigger queue ≠ safer  ·  Bigger queue = permission to be late"

Tiny footer:
"What happens when reality produces information faster than your robot can understand it?"

Style rules:
- One composition, engineering-sci-fi schematic, readable at phone feed size
- Sharp text, safe margins, no clutter, no purple gradients, no glossy 3D toys
- Make the contrast between depth 1 (near NOW) and depth 10 (buried in the past) obvious at a glance

Output: one polished hero poster for LinkedIn slide 1.
```

Save result as:

`day03-topics-and-backpressure/assets/linkedin/hero-reality-queue.png`
