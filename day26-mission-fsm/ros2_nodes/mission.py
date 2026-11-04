#!/usr/bin/env python3
"""How a rescue mission is allowed to change state.

SEARCHING sees something and becomes VERIFYING. A second look that holds
becomes LOCKDOWN. A second look that misses returns to SEARCHING. Nothing
else is an edge. LOCKDOWN has no way out.

The events are the inputs. What is counted is which transitions the
coordinator accepts.
"""

from __future__ import annotations

# (state, event) -> next state. Three arrows, matching the picture.
EDGES = {
    ("SEARCHING", "SEEN"): "VERIFYING",
    ("VERIFYING", "HELD"): "LOCKDOWN",
    ("VERIFYING", "MISSED"): "SEARCHING",
}

SCRIPTS = {
    # A glimpse, a miss, then a confirm with no second look. The confirm is refused.
    "missed": ("SEEN", "MISSED", "HELD"),
    # A glimpse, then the second look holds.
    "held": ("SEEN", "HELD"),
    # Legal entry, then three events that must not leave LOCKDOWN.
    "stay": ("SEEN", "HELD", "SEEN", "MISSED", "GOAL_DONE"),
}


def navigate_allowed(state: str) -> bool:
    """The coordinator lends Nav2 to the search only."""
    return state == "SEARCHING"


def run(mode: str) -> dict:
    events = SCRIPTS[mode]
    state = "SEARCHING"
    trace = [state]
    legal = 0
    rejected = 0
    for event in events:
        nxt = EDGES.get((state, event))
        if nxt is None:
            rejected += 1
            continue
        legal += 1
        state = nxt
        trace.append(state)
    return {
        "mode": mode,
        "final": state,
        "trace": ">".join(trace),
        "legal": legal,
        "rejected": rejected,
        "lockdown": int("LOCKDOWN" in trace),
        "navigate_allowed": int(navigate_allowed(state)),
        "edges": len(EDGES),
        "events": ">".join(events),
    }


def summary_line(result: dict) -> str:
    return (
        f"SUMMARY mode={result['mode']} "
        f"final={result['final']} "
        f"trace={result['trace']} "
        f"events={result['events']} "
        f"legal={result['legal']} "
        f"rejected={result['rejected']} "
        f"lockdown={result['lockdown']} "
        f"navigate_allowed={result['navigate_allowed']} "
        f"edges={result['edges']}"
    )


if __name__ == "__main__":
    for name in ("missed", "held", "stay"):
        print(summary_line(run(name)), flush=True)
