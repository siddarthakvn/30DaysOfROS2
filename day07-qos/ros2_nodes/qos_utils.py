#!/usr/bin/env python3
"""Shared QoS helpers for Day 07 compatibility experiments."""

from rclpy.qos import (
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
    QoSProfile,
    QoSReliabilityPolicy,
)


def build_qos(
    depth: int = 10,
    reliability: str = "reliable",
    durability: str = "volatile",
) -> QoSProfile:
    """KEEP_LAST + depth + reliability + durability."""
    rel = reliability.strip().lower()
    if rel in ("reliable", "rel"):
        reliability_policy = QoSReliabilityPolicy.RELIABLE
    elif rel in ("best_effort", "best-effort", "be"):
        reliability_policy = QoSReliabilityPolicy.BEST_EFFORT
    else:
        raise ValueError(
            f"reliability must be 'reliable' or 'best_effort', got {reliability!r}"
        )

    dur = durability.strip().lower().replace("-", "_")
    if dur in ("volatile", "vol"):
        durability_policy = QoSDurabilityPolicy.VOLATILE
    elif dur in ("transient_local", "transientlocal", "tl"):
        durability_policy = QoSDurabilityPolicy.TRANSIENT_LOCAL
    else:
        raise ValueError(
            f"durability must be 'volatile' or 'transient_local', got {durability!r}"
        )

    if depth < 1:
        raise ValueError(f"depth must be >= 1, got {depth}")

    return QoSProfile(
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=depth,
        reliability=reliability_policy,
        durability=durability_policy,
    )
