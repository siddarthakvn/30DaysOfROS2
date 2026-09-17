# Assets — Day 04

Evidence from runs on 2026-09-16 (domain 40, Fast DDS). GUI screenshots were not captured (no screenshot tool in the run environment); terminal transcripts are the primary evidence.

| File | Contents |
|---|---|
| `00_rmw_pin.txt` | RMW pin (`rmw_fastrtps_cpp`) |
| `00_graph.txt` | Initial `node` / `topic` / `action` list |
| `A0_topic_full_burst.log` | Topic full 5 s burst |
| `A1_topic_stop_publisher.log` | Stop publisher at 2 s |
| `B0_service_complete.log` | Long service happy path |
| `B1_service_client_interrupt.log` | Client SIGINT; server continues |
| `B_server_session.log` | Server session spanning B0/B1 |
| `C0_action_feedback_success.log` | Action SUCCEEDED + feedback |
| `C1_action_cancel.log` | Action CANCELED via `action_cancel_demo.py` |
| `C1_action_cancel_raw.log` | Earlier CLI cancel attempt (did not cancel under SIGINT) |

LinkedIn draft: [linkedin/DRAFT.md](linkedin/DRAFT.md)
