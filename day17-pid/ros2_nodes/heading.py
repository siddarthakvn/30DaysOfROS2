#!/usr/bin/env python3
"""Heading plant and a small PID, used by the Day 17 cases."""

from __future__ import annotations

import math


def wrap(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def simulate(
    kp: float,
    kd: float,
    ki: float,
    plant: str,
    target: float,
    seconds: float,
    dt: float = 0.01,
) -> dict:
    """Step a heading toward target.

    plant "inertia": command is angular acceleration, so turn rate is remembered.
    plant "instant": turn rate equals the command immediately.
    """
    if plant not in ("inertia", "instant"):
        raise ValueError(f"unknown plant {plant!r}")
    if dt <= 0.0 or seconds < 0.0:
        raise ValueError("dt must be > 0 and seconds >= 0")

    yaw = 0.0
    rate = 0.0
    integral = 0.0
    prev_error = wrap(target - yaw)
    crossings = 0
    past = 0.0
    steps = int(round(seconds / dt))

    for _ in range(steps):
        error = wrap(target - yaw)
        if prev_error * error < 0.0:
            crossings += 1
        integral += error * dt
        if plant == "inertia":
            # D uses turn rate, which is what carries the heading past the target.
            accel = kp * error + ki * integral - kd * rate
            rate += accel * dt
        else:
            rate = kp * error
        yaw += rate * dt
        past = max(past, yaw - target)
        prev_error = error

    final_error = wrap(target - yaw)
    return {
        "crossings": crossings,
        "yaw_deg": math.degrees(yaw),
        "error_deg": math.degrees(final_error),
        "past_deg": math.degrees(past),
        "rate": rate,
    }
