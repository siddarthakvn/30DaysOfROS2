# LinkedIn draft — Day 02

**Status:** Draft only. Do not post until Day 02 docs feel final, local git checkpoint is ready, and the GitHub day folder is public (`publish-day.sh` when you choose).

**Curriculum question:** Should every sensor be a separate ROS 2 node?

**Day 03 teaser (locked):** What happens when sensor data is published faster than a robot can process it?

---

## Image order (carousel)

Files live in this folder (`assets/linkedin/`). Upload in this order:

| Slide | File | Caption idea |
|:---:|---|---|
| 1 | `01_monolith_crash.png` | A: one process — camera crash kills everything |
| 2 | `02_daemons_camera_crashed_others_alive.png` | B: four processes — others survive |
| 3 | `03_c1_four_processes_survivors.png` | C1: four ROS nodes / four processes — survivors |
| 4 | `04_c2_composed_shared_fate.png` | C2: four ROS nodes / one process — shared fate |

Optional extras (not in the main four): `optional_A_monolith_running.png`, `optional_B_all_daemons_running.png`. See [README.md](README.md).

**Suggested carousel:** hero (slide 1) → `01` → `02` → `03` → `04`.

---

## ChatGPT prompt — hero / workflow master image (Interstellar block diagram)

Copy everything inside the fence into ChatGPT (image generation). Prefer regenerating until text is sharp.

```text
Create a single LinkedIn carousel hero image (landscape, 16:9, high resolution, sharp readable text).

Tone / style: INTERSTELLAR (film) — dark scientific mission aesthetic.
- Deep black / charcoal void background with faint starfield dust and subtle warm amber rim light (like Miller/Gargantua lighting: sparse gold highlights on darkness)
- Quiet, serious, cinematic — NOT neon cyberpunk, NOT purple glow, NOT glossy 3D robot stock art
- Think: NASA mission schematic projected in a dark control bay; TARS-like geometric clarity; Hans Zimmer silence as visual space
- High contrast ivory/white typography; amber/ochre only for accents, crash marks, and the answer strip
- No emojis, no cute icons, no QR code, no fake phone UI, no busy infographic cards with drop shadows

Purpose: one unified BLOCK DIAGRAM poster for Day 02 of #30DaysOfROS2 — engineering, not marketing.

Layout (strict block-diagram grammar — boxes, lines, arrows on one plane):

TOP TITLE (large, centered, crisp):
"Should every sensor be a separate ROS 2 node?"

SUBTITLE (smaller, muted):
"Day 02 / 30  ·  Ubuntu 22.04  ·  ROS 2 Humble  ·  nodes ≠ processes  ·  fault isolation"

MIDDLE — horizontal system block diagram, three stages left → right, connected by thin amber arrows labeled "experiment":

BLOCK A (left) — title bar: "A  MONOLITH"
- One large rounded rectangle = one OS process
- Inside: four smaller module blocks in a row: Camera | GPS | IMU | Motor
- Camera block has a sharp amber/red X (fault)
- GPS / IMU / Motor blocks are dimmed/grey (dead with the process) — do NOT show them as healthy OK
- Output arrow down to a small red status block: "SPOF — process dies"

BLOCK B (center) — title bar: "B  PROCESSES"
- Four separate process rectangles side by side (four OS boundaries)
- Labels: Camera | GPS | IMU | Motor
- Only Camera has X (crashed); GPS / IMU / Motor stay bright/alive
- Thin lines between them labeled "IPC" or leave unlabeled — do NOT write "ROS 2 DDS" here (this stage is plain OS processes)
- Output status block: "fault contained"

BLOCK C (right) — title bar: "C  ROS 2 NODES"
- Two stacked diagrams sharing the label "same four nodes":
  C1 (top): four process boxes, one node each → Camera X, others alive → tag "survivors"
  C2 (bottom): one process box containing four node blocks → Camera X causes all four marked DOWN → tag "shared fate"
- Tiny annotation: "architecture ≠ deployment"

BOTTOM full-width answer strip (bold, high contrast, amber on black or black on amber):
"Nodes = responsibility   |   Processes = fault isolation   |   Composition = shared fate (by choice)"

FOOTER (tiny, low contrast):
"#30DaysOfROS2  ·  Camera · GPS · IMU · Motor  ·  evidence: daemon/ + ros2_nodes/"

Rules:
- True block diagram: aligned boxes, orthogonal connectors, consistent spacing
- One composition / one scene — not a collage of separate cards
- Text must remain legible when viewed small in a LinkedIn feed
- Safe margins for mobile crop
- No purple gradients, no cream brochure look, no cluttered icon rows

Output: one dark cinematic block-diagram hero suitable as slide 1 of a technical LinkedIn carousel.
```

Save the result as:

`day02-modular-node-architecture/assets/linkedin/hero-workflow-nodes-vs-processes.png`

(Replace the previous light infographic hero.)

Then upload order: **hero → 01 → 02 → 03 → 04**.

---

## Post copy (paste-ready)

🚀 Should every sensor in a robot be its own ROS 2 node?

Camera.
GPS.
IMU.
Motor Controller.

At first, it seems easier to put everything into one Python program.
Less code.
Less files.
Less complexity.

But what actually happens when one module crashes?

That was today's engineering question.

Instead of accepting ROS 2's modular architecture as a best practice, I tested why it exists — and what “node” really guarantees.

🔬 Investigation A — Monolithic Architecture

I built a simple robotic application where Camera, GPS, IMU, and Motor Controller all ran inside a single Python program.

Then I intentionally crashed the Camera module.

Observation:
The entire application terminated immediately.
GPS stopped. IMU stopped. Motor Controller stopped.

One software failure shut down the complete robot.
That's a Single Point of Failure.

🔬 Investigation B — Fault Isolation via Processes

I split the same robot into four independent OS processes (daemons).

Then I crashed only the Camera daemon.

Result:
❌ Camera stopped
✅ GPS kept running
✅ IMU kept running
✅ Motor Controller kept running

Isolation worked — because each subsystem had its own process.

🔬 Investigation C — Node Boundary vs Process Boundary

Here's the part most tutorials skip.

ROS 2 is organised around *nodes*, not processes.
So does a separate node automatically isolate faults?

I ran the same four ROS 2 nodes two ways:

C1 — 4 nodes / 4 processes
Camera exited. GPS, IMU, and Motor kept ticking.

C2 — 4 nodes / 1 process (composed)
Same nodes. Same fault.
One shared PID.
Camera raised RuntimeError — and the whole container died with it.

Same architecture on the graph.
Opposite reliability.
Because fault isolation came from the process boundary, not the node name.

💡 What I learned today

✅ Monolithic software creates a Single Point of Failure
✅ Independent processes provide Fault Isolation
✅ A ROS 2 node is a unit of responsibility — not automatically a unit of failure
✅ Composition keeps modularity while trading isolation for performance
✅ Yes: sensors should generally be separate nodes — and process layout is a deliberate deploy-time choice

———

Why it matters

On a search-and-rescue robot, a flaky camera driver should not silently take down motor control.

But if you compose that camera into the same process as everything else for performance, you may have drawn isolation on the architecture diagram and lost it at deploy time.

ROS 2 encodes that honestly: architecture (nodes) and deployment (processes) are separate decisions.

———

Full write-up, Expected vs Actual, and screenshots:

https://github.com/siddarthakvn/30DaysOfROS2

Path: day02-modular-node-architecture/

If you reproduce and get a different result (especially with C++ component containers vs this Python composed executor), that is useful signal — share it.

———

From these three experiments, we get the answer to today’s engineering question:

Should every sensor be a separate ROS 2 node?

Yes to separate nodes — for ownership, interfaces, and the option to isolate later.
Fault isolation comes from OS processes, not from the node name alone.
Composition keeps modularity while deliberately sharing fate for performance.
So: separate nodes in general; process layout is a deploy-time engineering choice.

———

Day 02 / 30 ✅

Tomorrow’s question:
What happens when sensor data is published faster than a robot can process it?

#30DaysOfROS2 #ROS2 #Robotics #RobotOperatingSystem #SoftwareArchitecture #EmbeddedSystems #Python #AutonomousSystems #RoboticsEngineering #OpenSource #LearningInPublic #FaultIsolation #Linux
```
