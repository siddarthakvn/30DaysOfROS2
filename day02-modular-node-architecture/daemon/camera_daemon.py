import time

print("=" * 50)
print("[INFO] Camera Daemon Started")
print("=" * 50)

frame = 0

while True:

    frame += 1

    print(f"[Camera] Capturing Frame {frame}")

    time.sleep(1)

    if frame == 38:
        raise RuntimeError("Camera Sensor Failure")