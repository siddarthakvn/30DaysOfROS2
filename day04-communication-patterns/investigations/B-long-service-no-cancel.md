# Investigation B — Long-running Service (anti-pattern)

## Hypothesis (H1, H2)

A multi-second rotate implemented as a **Service** has:

- no mid-flight feedback to the client
- no cancel protocol

Official Humble docs: services should never be used for longer-running / preemptable work — prefer an Action.

## Setup

- `turtlesim_node`
- `long_rotate_server.py` — `std_srvs/Trigger` on `/long_rotate` (blocks in callback while publishing `cmd_vel`)
- `long_rotate_client.py`

## Procedure

See `ros2_nodes/run_B.sh`.

### B0 — Complete call

```bash
# Terminal 2
python3 long_rotate_server.py --ros-args -p duration_sec:=5.0

# Terminal 3
python3 long_rotate_client.py
```

### B1 — Ctrl+C client at ~2 s

Start the client, interrupt it mid-wait. Watch whether the **server** keeps publishing until `duration_sec` ends.

## Expected

- Client blocks until one response (B0)
- Server logs `SPIN` lines; client sees only the final `RESPONSE`
- B1: client exit ≠ server cancel (confirm server/turtle behavior from logs)

## Actual

Observed 2026-09-16 · Fast DDS · domain 40 · logs under `assets/`.

| Run | Observation | Evidence |
|---|---|---|
| B0 | Client blocked ~5.03 s; **one** response `success=True message='finished after 5.03s published=100...'`. Server logged `SPIN` every second; client received **no** mid-flight messages. | `assets/B0_service_complete.log`, `assets/B_server_session.log` |
| B1 | Client SIGINT ~1.4 s after call start (`Client interrupted — server may STILL be rotating`). Server continued `SPIN n=40…80` and `SERVICE DONE finished after 5.00s published=99` — full duration completed **after** client death. Pose later `theta≈-1.28`. | `assets/B1_service_client_interrupt.log` |

## Analysis

H1 and H2 hold for the Service path: the client gets a single terminal response (B0) and killing the client does **not** cancel server-side work (B1). That is exactly why Humble forbids long preemptable Services — there is no revoke contract.
