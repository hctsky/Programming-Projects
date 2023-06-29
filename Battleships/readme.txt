Battleship game using Excel and Pandas (and openpyxl)
Created by : Huang ChenTing
Contact: huang.chenting<AT>gmail.com
Date: June 2023


Instructions:
1. There are two files
	a. attacker_map.xlsm
	b. battleships.py

2. Open up attacker file. Use buttons to reset grid to all zeroes, or drop bombs ('1'.)
3. Additional bombs can be placed by manually inputting 1s into the cells.
4. Map size and Ammo count can be changed in VBA under Developer tab. If you change this, you have to change the MAPSIZE variable in the battleships.py file as well.
5. Save and close attacker_map.xlsx file when ready.

6. Run python 3 on battleships.py.

A battleship_map.xlsx file will be generated.

Sheet "Battleships Map" shows the positions of all the ships on the map.
Sheet "Battle Results" shows the positions in which bombs have hit the ships, with darker red cells denoting sunk ships.

The steps for playing is not very intuitive for this, as the attacker file is used first before the ships are generated. The reason is to have my ships accounted for when they are first created, and when I check whether they have been sunk.

I hope this project showcases that I can do a bit of Excel VBA, I can do a bit of Python, and I can learn and use pandas and openpyxl to some extent for simple excel file IO manipulation.

Thank you!
