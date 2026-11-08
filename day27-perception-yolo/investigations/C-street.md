# C — The mission hears SEEN

## Hypothesis

The same photo as A, published as an image, becomes a `Detection2DArray` whose header matches the image. A person at or above 0.50 becomes the string `SEEN`.

## Method

`scene:=street`. Same three nodes as B. The photo is the Ultralytics `bus.jpg` sample, downloaded by `fetch.sh`, 810×1080.

## Result

```text
SUMMARY node=camera scene=street width=810 height=1080 encoding=bgr8 frame=front stamp_sec=1794135809 stamp_nsec=545232586
SUMMARY node=detector scene=street width=810 height=1080 detections=5 persons=4 best_person=0.890 cx=740.2 cy=630.1 sx=139.5 sy=499.1 classes=person,person,person,bus,person frame=front stamp_sec=1794135809 stamp_nsec=545232586 stamp_match=1
SUMMARY node=ear scene=street seen=1 best_person=0.890 class_id=person threshold=0.50 detections=5 frame=front stamp_sec=1794135809 stamp_nsec=545232586
```

The echoed array, in score order:

| id | class_id | score |
|---|---|---|
| person-0 | person | 0.8902072310447693 |
| person-1 | person | 0.8832789659500122 |
| person-2 | person | 0.87844318151474 |
| bus-3 | bus | 0.8433693647384644 |
| person-4 | person | 0.43630853295326233 |

The best box center is `(740.18, 630.10)` pixels, size `139.47 × 499.09`. Every detection header uses stamp `1794135809.545232586` and `frame_id: front`, the same header as `/front/image_raw`.

`/mission_event`:

```text
data: SEEN
```

## Conclusion

The mission did not read the window. It read one detection message. Three person scores clear 0.50. The bus at 0.843 does not. The person at 0.436 is in the array and under the line. SEEN fires because the best person is 0.890, on the camera stamp.
