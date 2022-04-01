N-Puzzle using Pygame (for N=3)
Created by : Huang ChenTing
Contact: huang.chenting<AT>gmail.com
Date: March 2022

How to Open:
1. Run Python 3 on npuzzle.py, with pygame module imported.

Controls / Instructions:
RMOUSECLICK - shuffle puzzle tiles
A - use A* to solve the N-puzzle
H - A* will solve the solution, but only show 25% of the steps, as a hint to the player (will solve if there is only one step left)

To load your own custom image, simply place your image file in the same folder as the npuzzle.py file. The filename has to be "image.jpg". PNG files will cause the tiles numbers to show up incorrectly.

Disclaimer:
Credit to DLC Energy's youtube video below.
https://www.youtube.com/watch?v=afC3dq9MeJg
https://www.youtube.com/watch?v=70tiJI5mVds

I used the youtube videos for reference on how to do the sliding animation and how to use Pygame.image.subsurface to load the image onto the puzzle tiles.

Note that this implementation might have a small bug with checking of the legal tile placement, especially obvious for when N=2 for a 2x2 (or 4-puzzle.)

Also note that manhattan distance heuristic is not efficient for 4x4 (15-puzzle.)

So this demo is best for N=3 , 3x3, or 8-puzzle.

Thank you!
