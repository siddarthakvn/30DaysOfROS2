# Interview questions — Day 17

## 1. Why does a robot oscillate around a target angle?

P turns hard while the gap is large, so the heading builds turn speed. At the target, P is zero and does not cancel that speed. The nose crosses, the error flips, and P turns back.

## 2. What did the P-only run do?

Gain 4, no D, heading that remembers turn rate, target 90°. It crossed five times, went 90° past the target, and finished near 176°.

## 3. What did adding D change?

The same P and the same plant. D gain 4. Zero crossings. Final heading 90.00°.

## 4. Why did the same P settle when turn rate was not stored?

There was no leftover turn speed at the target. The command and the turn rate dropped together as the gap closed.

## 5. What is I for, if it was not the cause here?

A gap that remains after P has done what it can. It can also push past the target if the sum has been growing. It was left at 0 in this day so the wobble could be traced to P and stored turn rate.
