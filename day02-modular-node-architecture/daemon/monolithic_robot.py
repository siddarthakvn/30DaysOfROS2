import time

print("=" * 50)
print("🤖 MONOLITHIC ROBOT STARTED")
print("=" * 50)

camera_frames = 0

while True:

    print("📷 Camera Module Running")
    time.sleep(1)

    camera_frames += 1

    if camera_frames == 5:
        raise RuntimeError("Camera driver crashed!")

    print("🛰 GPS Module Running")
    time.sleep(1)

    print("🧭 IMU Module Running")
    time.sleep(1)

    print("⚙️ Motor Controller Running")
    time.sleep(1)

    print("-------------------------------------")