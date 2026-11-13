"""One latched sample so a late subscriber still sees the pixel or the point."""

from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy


def latched() -> QoSProfile:
    return QoSProfile(
        depth=1,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.TRANSIENT_LOCAL,
    )
