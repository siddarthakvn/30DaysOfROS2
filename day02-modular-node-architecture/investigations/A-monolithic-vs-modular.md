# Investigation A — Monolithic Robot Architecture

## Engineering Question

What happens if an entire robotic system is implemented as a single program?

---

## Hypothesis

If all robot functionalities execute inside one program, then a failure in one module should terminate the entire application.

---

## Experimental Setup

A Python program named `monolithic_robot.py` was created to simulate a robot consisting of:

- Camera Module
- GPS Module
- IMU Module
- Motor Controller

All modules execute sequentially inside a single process.

---

## Procedure

1. Execute the monolithic robot program.
2. Observe the normal execution of all modules.
3. Intentionally generate an exception inside the Camera Module.
4. Observe the behaviour of the remaining modules.

---

## Observations

Before the failure:

- Camera Module was running.
- GPS Module was running.
- IMU Module was running.
- Motor Controller was running.

After the Camera Module generated an exception:

- Python terminated the application.
- GPS stopped.
- IMU stopped.
- Motor Controller stopped.
- The entire robotic software exited.

Screenshots:

- `expA_monolithic_running.png`
- `expA_monolithic_crash.png`

---

## Analysis

Since every subsystem existed inside a single process, an unhandled exception terminated the entire application.

This architecture creates a **Single Point of Failure**, where the reliability of the complete robotic system depends on a single executable.

---

## Conclusion

Monolithic robotic software is difficult to maintain and is vulnerable to complete system failure when one module crashes.

---

## Real Robotics Connection

Imagine an autonomous delivery robot where the camera driver crashes.

In a monolithic architecture:

- Navigation stops.
- Motor control stops.
- Sensor processing stops.
- The robot becomes completely non-functional.

This demonstrates why modern robotic systems avoid monolithic software designs.

---

## Key Takeaways

- One application controls every subsystem.
- One software failure stops the entire robot.
- Monolithic architectures introduce a Single Point of Failure.
- Large robotic systems require modular software design.