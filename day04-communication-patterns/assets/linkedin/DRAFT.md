# LinkedIn draft — Day 04

**Status:** Draft ready for human edit/post after local git checkpoint and public reveal (`publish-day.sh` when you choose).

**Curriculum question:** When should a robot use a Topic, Service, or Action?

**Day 05 teaser (locked):** How does a robot cancel a task while it is still executing?

---

## Image order (carousel)

Evidence today is primarily terminal transcripts under `assets/` (no GUI screenshot tool in the run environment). Suggested slides:

| Slide | File | Caption idea |
|:---:|---|---|
| 1 | `hero-three-contracts.png` | Hero: Topic / Service / Action — three commitments, one robot |
| 2 | `A1_topic_stop_publisher.log` excerpt | Topic: stop publishing ≠ cancel |
| 3 | `B1_service_client_interrupt.log` excerpt | Service: client gone, server finished 5 s anyway |
| 4 | `C1_action_cancel.log` excerpt | Action: feedback + cancel → CANCELED at θ≈1.02 |

**Carousel:** hero → A1 → B1 → C1.

---

## ChatGPT prompt — hero / master image (Interstellar block diagram)

Copy everything inside the fence into ChatGPT (image generation). Prefer regenerating until text is sharp.

```text
Create a single LinkedIn carousel hero image (landscape, 16:9, high resolution, sharp readable text).

Tone / style: INTERSTELLAR (film) — dark scientific mission aesthetic.
- Deep black / charcoal void background with faint starfield dust and subtle warm amber rim light (Miller/Gargantua: sparse gold on darkness)
- Quiet, serious, cinematic — NOT neon cyberpunk, NOT purple glow, NOT glossy 3D robot stock art, NOT cute turtlesim clipart
- NASA mission schematic in a dark control bay; TARS-like geometric clarity; Hans Zimmer silence as visual space
- High contrast ivory/white typography; amber/ochre ONLY for accents, danger marks, and the bottom answer strip
- No emojis, no QR code, no fake phone UI, no busy marketing cards with drop shadows

Purpose: one unified BLOCK DIAGRAM poster for Day 04 of #30DaysOfROS2.
Core idea (attention grab): Topic, Service, and Action are NOT three APIs — they are THREE COMMITMENTS. Same robot motion. Three contracts. One can be revoked.

Layout (strict block-diagram grammar — boxes, lines, arrows on one plane):

TOP TITLE (large, centered, crisp):
"When should a robot use a Topic, Service, or Action?"

SUBTITLE (smaller, muted):
"Day 04 / 30  ·  Ubuntu 22.04  ·  ROS 2 Humble  ·  same motion  ·  three contracts"

CENTER HOOK (small amber label above the three columns):
"ONE TASK: ROTATE  ·  THREE COMMITMENTS"

MIDDLE — three equal vertical columns side by side (left → right), same robot silhouette / simple differential-drive glyph at the top of EACH column (identical), so the eye compares contracts not robots:

COLUMN 1 — title bar: "TOPIC"
- Big label under title: "STREAM"
- Diagram: Publisher box → thick one-way amber dashed arrow → Topic bus bar → fans out to Subscriber boxes
- Mid-column interrupt mark: scissors / break on the publish arrow labeled "STOP PUBLISHING"
- Bottom status pill (muted, NOT success green): "NO CANCEL PROTOCOL"
- Tiny caption: "silence ≠ revoke"

COLUMN 2 — title bar: "SERVICE"
- Big label under title: "ONE REPLY"
- Diagram: Client box ⇄ single request/response loop to Server box (two-way, short)
- Danger annotation in amber/red: Server keeps a long spinning gear / hourglass WHILE Client is marked DEAD / X
- Arrow from dead client does NOT reach the server work
- Bottom status pill (warning): "CLIENT GONE · WORK CONTINUES"
- Tiny caption: "anti-pattern if long / preemptable"

COLUMN 3 — title bar: "ACTION"  (make this the hero column — slightly brighter rim light)
- Big label under title: "MISSION"
- Diagram: Client → Goal → Server; feedback loop arrows labeled "PROGRESS"; separate cancel arrow in amber labeled "CANCEL"
- Goal state chips in a tiny row: ACCEPTED → EXECUTING → CANCELED
- Bottom status pill (strong amber on black): "REVOKABLE · FEEDBACK · RESULT"
- Tiny caption: "commitment you can take back"

Between columns, thin vertical dividers; small top badges:
  Topic: "many ↔ many"
  Service: "many → one"
  Action: "goal UUID"

BOTTOM full-width answer strip (bold, high contrast, amber on black or black on amber) — the punchline:
"Stream with Topics   ·   Ask quick with Services   ·   Commit behaviors with Actions"

FOOTER (tiny, low contrast):
"#30DaysOfROS2  ·  turtlesim rotate  ·  H1 cancel  ·  H2 feedback  ·  H3 stop≠cancel  ·  evidence: assets/*.log"

Rules:
- True block diagram: aligned boxes, orthogonal connectors, consistent spacing
- One composition / one scene — not a collage of separate cards
- Text must remain legible when viewed small in a LinkedIn feed
- Safe margins for mobile crop
- The emotional hook must read in under 2 seconds: THREE CONTRACTS / ONLY ACTION CAN CANCEL
- No purple gradients, no cream brochure look, no cluttered icon rows, no turtlesim cartoon turtle

Output: one dark cinematic block-diagram hero suitable as slide 1 of a technical LinkedIn carousel.
```

Save the result as:

`day04-communication-patterns/assets/linkedin/hero-three-contracts.png`

Then upload order: **hero → A1 excerpt/slide → B1 → C1**.

---

## Post draft

**Day 04 of #30DaysOfROS2**

**Question:** When should a robot use a Topic, Service, or Action?

I used to treat these as three ways to “send data.”

They are not.

They are three **commitment models**:

- Topic → stream (I don’t wait for you)
- Service → quick ask / one answer
- Action → mission (progress + result + cancel)

**Experiment (turtlesim):** same idea — rotate the turtle — three ways:

1. Topic `cmd_vel` burst → stop the publisher at 2 s  
2. Long Service (anti-pattern) → SIGINT the client mid-call  
3. Action `rotate_absolute` → feedback `remaining`, cancel at 1 s  

**What the logs showed:**

- Topic: no goal lifecycle — stopping the publisher is not a cancel protocol  
- Service: client died; server still ran the full 5 s and returned one response  
- Action: continuous `remaining` feedback; cancel → **`CANCELED`**; turtle stopped mid-turn (`θ≈1.02`, not π)

**Takeaway:**

Stream with Topics. Ask quick questions with Services. Commit behaviors with Actions.

Humble’s rule is blunt: **never** use a Service for long preemptable robot work — that is what Actions are for.

Gazebo teleop comes later (Day 14). Today was about choosing the contract, not the simulator.

#ROS2 #Robotics #Humble #SystemsEngineering
