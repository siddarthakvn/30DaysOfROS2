#!/usr/bin/env python3
"""Shared QoS helpers for Day 03 overload experiments."""

from rclpy.qos import (
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
    QoSProfile,
    QoSReliabilityPolicy,
)


def build_qos(depth: int, reliability: str) -> QoSProfile:
    """KEEP_LAST + depth + reliability. Durability always VOLATILE."""
    rel = reliability.strip().lower()
    if rel in ("reliable", "rel"):
        reliability_policy = QoSReliabilityPolicy.RELIABLE
    elif rel in ("best_effort", "best-effort", "be"):
        reliability_policy = QoSReliabilityPolicy.BEST_EFFORT
    else:
        raise ValueError(
            f"reliability must be 'reliable' or 'best_effort', got {reliability!r}"
        )

    if depth < 1:
        raise ValueError(f"depth must be >= 1, got {depth}")

    return QoSProfile(
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=depth,
        reliability=reliability_policy,
        durability=QoSDurabilityPolicy.VOLATILE,
    )
