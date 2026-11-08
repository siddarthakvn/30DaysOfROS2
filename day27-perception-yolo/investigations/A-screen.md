# A — Boxes on the screen

## Hypothesis

YOLOv8n can score a person in-process and still leave `/detections` and `/mission_event` unpublished.

## Method

`screen.py` reads the street photo, runs YOLOv8n, and prints the count. It creates no node and no publisher.

Then `ros2 topic info` on `/front/image_raw`, `/detections`, and `/mission_event`.

## Result

```text
SUMMARY node=screen scene=street width=810 height=1080 detections=5 persons=4 best_person=0.890 published=0 seen=0
```

```text
Unknown topic '/front/image_raw'
Unknown topic '/detections'
Unknown topic '/mission_event'
```

The model did run. Four people, best score 0.890, on an 810×1080 frame. Nothing was published.

## Conclusion

A drawn box is not a detection the rest of the graph can hear. The score already existed. The topics did not.
