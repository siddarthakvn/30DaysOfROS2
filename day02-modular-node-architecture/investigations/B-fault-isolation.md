# Investigation B — Fault Isolation Through Independent Processes

## Engineering Question

Can independent software modules continue operating even if one module crashes?

---

## Hypothesis

If each robotic subsystem executes as an independent process, then a failure in one process should not terminate the remaining processes.

---

## Experimental Setup

Four independent Python programs were created to simulate a modular robotic system.

The following daemons were executed simultaneously:

- Camera Daemon
- GPS Daemon
- IMU Daemon
- Motor Daemon

Each daemon was executed in its own terminal window, representing independent operating system processes.

---

## Procedure

1. Launch all four daemons simultaneously.
2. Verify that each daemon executes independently.
3. Intentionally generate an exception inside the Camera Daemon.
4. Observe the behaviour of the remaining daemons.

---

## Observations

Before the failure:

- Camera Daemon was running.
- GPS Daemon was running.
- IMU Daemon was running.
- Motor Daemon was running.

After the Camera Daemon crashed:

- Camera Daemon terminated.
- GPS Daemon continued running.
- IMU Daemon continued running.
- Motor Daemon continued running.

The remaining daemons were completely unaffected by the Camera Daemon failure.

Screenshots:

- `expB_all_daemons_running.png`
- `expB_camera_crashed_others_alive.png`

---

## Analysis

Unlike the monolithic architecture demonstrated in Investigation A, each subsystem was executed as an independent operating system process.

Since every daemon had its own execution context and memory space, the operating system isolated the failure to only the Camera Daemon.

This behaviour demonstrates **Fault Isolation**, where failures are contained within the affected module instead of propagating throughout the entire robotic system.

This architectural principle significantly improves the robustness and reliability of robotic software.

---

## Conclusion

Independent processes provide fault isolation.

A software failure inside one subsystem does not terminate unrelated subsystems, allowing the robotic system to continue operating despite partial failures.

This modular architecture is one of the fundamental design principles adopted by ROS 2.

---

## Real Robotics Connection

Consider an autonomous search and rescue robot equipped with multiple sensors.

If the camera driver unexpectedly crashes:

- IMU data can still be published.
- GPS localisation can continue.
- Motor control can remain operational.
- The robot can safely stop, switch to an alternative sensing strategy, or notify an operator instead of shutting down completely.

This level of reliability is only possible because the robot is designed as a collection of independent modules rather than one monolithic application.

---

## Key Takeaways

- Each subsystem should have a single responsibility.
- Independent processes improve software reliability.
- Faults remain isolated to the affected module.
- Modular architectures are easier to maintain and extend.
- ROS 2 adopts this design philosophy by organising robotic applications into independent nodes.