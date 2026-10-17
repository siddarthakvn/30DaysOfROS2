# LinkedIn draft — Day 20

**Hero:** [`01-hero.jpg`](01-hero.jpg)

**Question:** A robot has a map — but how does it know where it is on that map?

---

You wake up blindfolded in your own house.

You have the floor plan in your pocket.
You still do not know which room you are standing in.

That is Day 20 of #30DaysOfROS2.

A robot has a map. How does it know where it is on that map?

I froze the drawing of a small house. Kitchen on the left. Hall in the middle. Bedroom at the top right. The robot was in the kitchen the whole time. I did not tell the program that.

One guess, dropped in the bedroom, copied every step the wheels took. It finished 5.316 m away. Still in the bedroom.

Four hundred guesses, moved only by the wheels, stayed sprinkled through the house. The cloud was 3.304 m wide. About a third of the dots were in the kitchen, which is what a random handful looks like.

Then the laser was allowed to vote. Each guess was kept only if the walls it expected matched the walls the robot felt.

The first vote picked the room. 98.8% of the guesses were in the kitchen, and the place they agreed on was still 2.605 m off. A long kitchen looks alike from both ends.

The next steps broke that tie. The cloud pulled onto the body. Final error 0.030 m. Every surviving guess was in the kitchen.

The drawing never changed. The feet carried the guesses. The laser decided which ones were allowed to stay.

Day 20 / #30DaysOfROS2

https://github.com/siddarthakvn/30DaysOfROS2/tree/main/day20-amcl

#ROS2 #Robotics #AMCL #Localization #BostonDynamics #NVIDIARobotics
