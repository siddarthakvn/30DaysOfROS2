#!/usr/bin/env python3
"""Draw boxes in this process. Publish nothing."""

from __future__ import annotations

from yolo import best_person, detect, load_net, load_scene


def main() -> None:
    scene = "street"
    image = load_scene(scene)
    rows = detect(image, load_net())
    person = best_person(rows)
    score = 0.0 if person is None else person["score"]
    print(
        "SUMMARY "
        f"node=screen scene={scene} width={image.shape[1]} height={image.shape[0]} "
        f"detections={len(rows)} persons={sum(1 for row in rows if row['name'] == 'person')} "
        f"best_person={score:.3f} published=0 seen=0",
        flush=True,
    )
    print(f"READY node=screen scene={scene}", flush=True)


if __name__ == "__main__":
    main()
