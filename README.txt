/**********************************************************************
ROGUE ORDER
Developer: Sharjeel Ali 
Last Updated: Feb 17, 2018
Requirements: Python 3 and the pygame library
Info: A 2D based platformer game built using python for a university
	    game development project. 
How to run: Type the following into the command shell: 
            "python 3 comp1501_w18_101070889_a2_source.py
/**********************************************************************

Some important points I would like to address:
1. As each level is different, and obviously you will not have time to spend on trying to complete each one legitimately, here is what you will need to change to make your life easier in the source file:

1. Infinite health:
	In line 784, for the update_last_stand(gameData) function, change the following:
		gameData["circle_hitbox"]["health"]["num"]-=1
	to:
		if gameData["level"][3]["state"]:
                        gameData["circle_hitbox"]["health"]["num"]-=1

2. I have found one glitch, that due to time constraints, I could not solve:
	The glitch is related to the "RESUME" button on the menu. What should happen, is that whatever level you left off on, if you exit and reload the game, the level should resume. This works fine, however, manually changing  save.txt file in the Saves folder to "LEVEL_2", "LEVEL_2_KEY", or "LEVEL_3" will not work for some reason. However, it works fine on desktop (Where I actually made my game), just not virtualbox . So to fix this issue, and resume from any level do the following:

	1. Play level 1: 
		Just hit new game in the menu
	2. Play level 2:
		In get_variables(gameData), do the following:
			Assign: gameData["level"][1]["state"] = False
			Assign: gameData["level"][2]["state"] = True
		In Saves/save.txt file, type "LEVEL_2"

	3. Play level 3:
		In get_variables(gameData), do the following:
			Assign: gameData["level"][1]["state"] = False
			Assign: gameData["level"][3]["state"] = True
		In Saves/save.txt file, type "LEVEL_3"

If not even this works (I tested it, and it should work), then simply turn on infinite health and spend a minute finishing level 1 to access the next levels. 

3. To make things easier, the "key" is located at the end of level 1, in the commander's office. After he's done, quickly run to the right and hit enter once you are near the chest. This will prompt the save file to become: "LEVEL_2_KEY". Doing so automatically opens the door at the start of level 2, instead of relying on the rockets to blow it up. 



4. Audio: The game relies on audio, so please turn it on if you could. 

