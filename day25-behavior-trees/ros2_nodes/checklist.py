#!/usr/bin/env python3
"""Why a checklist beats a knot of arrows.

The job is the one from yesterday: plan, follow, and if follow fails, recover
and try again. The first follow fails. Back up succeeds. The second follow
succeeds.

knot     the picture. Five behaviors, an arrow each way between every pair.
machine  the same job as an explicit state machine. Retry is a copied edge.
tree     the same job as a recovery node. Retry is one rule at the root.

Adding a recovery is measured on both graphs. The leaf results are the inputs.
The thing being counted is the control structure.
"""

from __future__ import annotations

PICTURE = ("PLAN", "FOLLOW", "CLEAR", "SPIN", "BACK_UP")
ONE = ("BACK_UP",)
THREE = ("BACK_UP", "SPIN", "WAIT")


class World:
    """Scripted leaves. The first follow fails. Only BACK_UP succeeds."""

    def __init__(self) -> None:
        self.follow_fails_left = 1
        self.actions: list[tuple[str, str]] = []

    def plan(self) -> bool:
        self.actions.append(("plan", "SUCCESS"))
        return True

    def follow(self) -> bool:
        if self.follow_fails_left:
            self.follow_fails_left -= 1
            self.actions.append(("follow", "FAILURE"))
            return False
        self.actions.append(("follow", "SUCCESS"))
        return True

    def recovery(self, name: str) -> bool:
        ok = name == "BACK_UP"
        self.actions.append((name.lower(), "SUCCESS" if ok else "FAILURE"))
        return ok


def knot_edges() -> list[tuple[str, str]]:
    return [(a, b) for a in PICTURE for b in PICTURE if a != b]


def fsm_edges(recoveries: tuple[str, ...]) -> list[tuple[str, str, str]]:
    edges = [
        ("PLAN", "ok", "FOLLOW"),
        ("PLAN", "fail", "FAILED"),
        ("FOLLOW", "ok", "DONE"),
        ("FOLLOW", "fail", recoveries[0]),
    ]
    for current, nxt in zip(recoveries, recoveries[1:]):
        edges.append((current, "ok", "PLAN"))
        edges.append((current, "fail", nxt))
    last = recoveries[-1]
    edges.append((last, "ok", "PLAN"))
    edges.append((last, "fail", "FAILED"))
    return edges


def fsm_states(edges: list[tuple[str, str, str]]) -> list[str]:
    found: list[str] = []
    for src, _event, dst in edges:
        for name in (src, dst):
            if name not in found:
                found.append(name)
    return found


def run_fsm(recoveries: tuple[str, ...]) -> tuple[str, list[tuple[str, str]], list[tuple[str, str, str]]]:
    edges = fsm_edges(recoveries)
    table = {(src, event): dst for src, event, dst in edges}
    world = World()
    state = "PLAN"
    for _ in range(12):
        if state in ("DONE", "FAILED"):
            break
        if state == "PLAN":
            ok = world.plan()
        elif state == "FOLLOW":
            ok = world.follow()
        else:
            ok = world.recovery(state)
        state = table[(state, "ok" if ok else "fail")]
    result = "SUCCEEDED" if state == "DONE" else "FAILED"
    return result, world.actions, edges


def bt_parts(recoveries: tuple[str, ...]) -> tuple[list[str], list[tuple[str, str]]]:
    nodes = ["recovery", "sequence", "plan", "follow", "fallback"]
    nodes.extend(name.lower() for name in recoveries)
    edges = [
        ("recovery", "sequence"),
        ("sequence", "plan"),
        ("sequence", "follow"),
        ("recovery", "fallback"),
    ]
    edges.extend(("fallback", name.lower()) for name in recoveries)
    return nodes, edges


def run_bt(recoveries: tuple[str, ...]) -> tuple[str, list[tuple[str, str]], list[str], list[tuple[str, str]]]:
    """Recovery node: tick the sequence, and on failure tick the fallback, then the sequence again."""
    world = World()
    nodes, edges = bt_parts(recoveries)

    def sequence() -> bool:
        if not world.plan():
            return False
        return world.follow()

    def fallback() -> bool:
        for name in recoveries:
            if world.recovery(name):
                return True
        return False

    ok = False
    for _ in range(len(recoveries) + 1):
        if sequence():
            ok = True
            break
        if not fallback():
            break
    return ("SUCCEEDED" if ok else "FAILED"), world.actions, nodes, edges


def _trace(actions: list[tuple[str, str]]) -> str:
    return ">".join(name for name, _status in actions)


def run(mode: str) -> dict:
    if mode == "knot":
        edges = knot_edges()
        return {
            "mode": mode,
            "result": "NONE",
            "actions": [],
            "trace": "-",
            "units": len(PICTURE),
            "unit_name": "states",
            "edges": len(edges),
            "grown_edges": 0,
            "added_edges": 0,
            "statuses": [],
        }
    if mode == "machine":
        result, actions, edges = run_fsm(ONE)
        grown = fsm_edges(THREE)
        return {
            "mode": mode,
            "result": result,
            "actions": actions,
            "trace": _trace(actions),
            "units": len(fsm_states(edges)),
            "unit_name": "states",
            "edges": len(edges),
            "grown_edges": len(grown),
            "added_edges": len(grown) - len(edges),
            "statuses": actions,
        }
    if mode == "tree":
        result, actions, nodes, edges = run_bt(ONE)
        _grown_nodes, grown_edges = bt_parts(THREE)
        return {
            "mode": mode,
            "result": result,
            "actions": actions,
            "trace": _trace(actions),
            "units": len(nodes),
            "unit_name": "nodes",
            "edges": len(edges),
            "grown_edges": len(grown_edges),
            "added_edges": len(grown_edges) - len(edges),
            "statuses": actions,
        }
    raise ValueError(mode)


def summary_line(result: dict) -> str:
    return (
        f"SUMMARY mode={result['mode']} "
        f"result={result['result']} "
        f"trace={result['trace']} "
        f"{result['unit_name']}={result['units']} "
        f"edges={result['edges']} "
        f"grown_edges={result['grown_edges']} "
        f"added_edges={result['added_edges']}"
    )


if __name__ == "__main__":
    for name in ("knot", "machine", "tree"):
        print(summary_line(run(name)), flush=True)
