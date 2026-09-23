# Day 10 — Interview Questions

## How do you bring up an entire robot with one command?

Use **`ros2 launch`** with a launch description that starts the needed processes and applies namespaces, parameters, remappings, and optional includes/conditions.

## Namespace vs remapping?

**Namespace** prefixes a whole tree (`/robot1/...`). **Remapping** rewires specific interface names. Both are static for the node lifetime.

## Does launch wait until nodes are ready?

**No** by default. Process started ≠ application ready. Use timers, lifecycle, or explicit waits when order matters.
