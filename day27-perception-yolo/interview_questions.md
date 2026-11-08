# Day 27 — Interview questions

1. YOLOv8 prints a person score of 0.890 in the detector process. Why can the mission node still hear nothing?

2. What does `cv_bridge` convert, and which node in this graph is allowed to call the model?

3. A `Detection2DArray` arrives. Which fields does the ear need before it may publish `SEEN`?

4. Why does the detection header copy the image stamp and `frame_id` instead of taking a new stamp when inference finishes?

5. The blank frame published `detections: []`. Why is that a different failure from investigation A, where the topic was unknown?

6. The array contains a bus at 0.843 and a person at 0.436. Why does only the best person open `SEEN`?

7. This demo latches one image. What would you have to revisit before pointing the same detector at a live camera stream?
