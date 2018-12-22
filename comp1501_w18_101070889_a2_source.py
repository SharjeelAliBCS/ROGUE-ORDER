# -*- coding: utf-8 -*-
import pygame
import random
import math
import csv
import random

from pygame.locals import *

# the window is the actual window onto which the camera view is resized and blitted
window_wid = 1000
window_hgt = 500

# the frame rate is the number of frames per second that will be displayed and although
# we could (and should) measure the amount of time elapsed, for the sake of simplicity
# we will make the (not unreasonable) assumption that this "delta time" is always 1/fps
frame_rate = 30
delta_time = 1 / frame_rate

# constants for designating the different games states

#Loads a text file
def load_text(file_name):
	file_hndl = open(file_name, "r")
	file_data = file_hndl.read()
	file_hndl.close()
	return file_data.upper()

#Saves a text file
def save_text(file_name, file_data):
	file_hndl = open(file_name, "w")
	file_hndl.write(file_data)
	file_hndl.close()

#Loads a CSV file
def readCSV(csv_file_name, is_map):

	with open(csv_file_name) as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		row_data = []
		
		i = 0
		for row in readCSV:
			if is_map:
				row_data.append(row)
			if i >0 and not is_map:	
				row_data.append(row)
			i+=1
		
	return row_data

#Handles circle-line collision
def detect_collision_line_circ(u, v):

        # unpack u; a line is an ordered pair of points and a point is an ordered pair of co-ordinates
        (u_sol, u_eol) = u
        (u_sol_x, u_sol_y) = u_sol
        (u_eol_x, u_eol_y) = u_eol

        # unpack v; a circle is a center point and a radius (and a point is still an ordered pair of co-ordinates)
        (v_ctr, v_rad) = v
        (v_ctr_x, v_ctr_y) = v_ctr

        # the equation for all points on the line segment u can be considered u = u_sol + t * (u_eol - u_sol), for t in [0, 1]
        # the center of the circle and the nearest point on the line segment (that which we are trying to find) define a line 
        # that is is perpendicular to the line segment u (i.e., the dot product will be 0); in other words, it suffices to take
        # the equation v_ctr - (u_sol + t * (u_eol - u_sol)) · (u_evol - u_sol) and solve for t
        
        t = ((v_ctr_x - u_sol_x) * (u_eol_x - u_sol_x) + (v_ctr_y - u_sol_y) * (u_eol_y - u_sol_y)) / ((u_eol_x - u_sol_x) ** 2 + (u_eol_y - u_sol_y) ** 2)

        # this t can be used to find the nearest point w on the infinite line between u_sol and u_sol, but the line is not 
        # infinite so it is necessary to restrict t to a value in [0, 1]
        t = max(min(t, 1), 0)
        
        # so the nearest point on the line segment, w, is defined as
        w_x = u_sol_x + t * (u_eol_x - u_sol_x)
        w_y = u_sol_y + t * (u_eol_y - u_sol_y)
        
        # Euclidean distance squared between w and v_ctr
        d_sqr = (w_x - v_ctr_x) ** 2 + (w_y - v_ctr_y) ** 2
        
        # if the Eucliean distance squared is less than the radius squared
        if (d_sqr <= v_rad ** 2):
        
                # the line collides
                return True  # the point of collision is (int(w_x), int(w_y))
                
        else:
        
                # the line does not collide
                return False

        # visit http://ericleong.me/research/circle-line/ for a good supplementary resource on collision detection

#Gets user input
def game_loop_inputs(gameData):
       

        for event in pygame.event.get():
    
                # Handle [x] Press
                if event.type == pygame.QUIT:
                        sys.exit(0)
                # Handle Key Presses
   
                if event.type == pygame.KEYDOWN:   
                        
                        if event.key == pygame.K_SPACE:
                                if not gameData["circle_hitbox"]["last_stand"]:
                                        gameData["circle_hitbox"]["jump"] = True
                        
                        if event.key == pygame.K_a:
                                gameData["circle_hitbox"]["direction"] = "LEFT"
                                gameData["circle_hitbox"]["last_key"] = "LEFT"
                        
                        if event.key == pygame.K_d:
                                gameData["circle_hitbox"]["direction"] = "RIGHT"
                                gameData["circle_hitbox"]["last_key"] = "RIGHT"
                        
                        if event.key == pygame.K_LSHIFT:
                                gameData["circle_hitbox"]["aim_gun"] = True

                        if event.key == pygame.K_RETURN:
                                if gameData["state"]["MENU"]:  
                                        gameData = resume_menu(gameData)
                                elif  gameData["state"]["TITLE"]:
                                        gameData["state"]["TITLE"] = False
                                        gameData["state"]["GAME"] = True
                                        gameData["music_on"] = False
                                        gameData["new_game"] = True
                                        
                                elif gameData["state"]["GAMEOVER"]:
                                        gameData["state"]["GAMEOVER"] = False
                                        gameData["state"]["GAME"] = True
                                        gameData["music_on"] = False
                                        gameData["new_game"] = True
                                        if gameData["level"][2]["state"]:
                                                gameData["circle_hitbox"]["x_relative"] = 0

                                elif gameData["state"]["PAUSE"]: 
                                        if gameData["menu_options"]["NEW"]:
                                               gameData = resume_pause(gameData)

                                        if gameData["menu_options"]["RESUME"]:
                                                gameData["state"]["GAME"] = False
                                                gameData["state"]["PAUSE"] = False
                                                gameData["music_on"] = False
                                                gameData["state"]["MENU"] = True
                                                gameData["new_game"] = True
                                                gameData= get_variables(gameData)
                                                gameData["new_level"] = True
                                                gameData["menu_options"]["CONTROL_WINDOW"] = False
                                             

                                else:
                                        gameData["circle_hitbox"]["shoot"] = True
                                        gameData["circle_hitbox"]["skip"] = True
                                        gameData["sprites"]["chest"]["open"] = True

                                        if gameData["sprites"]["ending_on"]:  
                                                gameData["sprites"]["ending_fade"] = False

                                        if gameData["level"][4] and gameData["sprites"]["Characters"]["Leader"]["x_cord"] <=700:
                                                gameData["sprites"]["dialog"]["leader"]["counter"] = 55*40

                        if event.key == pygame.K_ESCAPE:

                                if gameData["state"]["MENU"]:     
                                      
                                        if gameData["menu_options"]["CONTROL_WINDOW"]:
                                                gameData["menu_options"]["CONTROLS"] = False
                                                gameData["menu_options"]["CONTROL_WINDOW"] = False
                                        else:
                                                sys.exit(0)
                                elif gameData["state"]["PAUSE"]:
                                        gameData= resume_pause(gameData)
      
                                elif gameData["state"]["GAME"] or gameData["level"][4]:
                                       
                                        gameData["pause_on"] = True
                                        gameData["state"]["PAUSE"] = True

                                elif gameData["state"]["TITLE"]:
                                        sys.exit(0)
                                elif gameData["state"]["GAMEOVER"]:
                                        gameData["state"]["GAME"] = False
                                        gameData["music_on"] = False
                                        gameData["state"]["MENU"] = True
                                        gameData["new_game"] = True
                                        gameData= get_variables(gameData)

                                
                                
                        if gameData["state"]["MENU"]:
                                if event.key == pygame.K_1:
                                        gameData["sprites"]["player"]["sheet_org"] = get_sprite("graphics/characters/player_sprite1.png", 128, 18)
                                        gameData["sprites_num"] = 1
                                if event.key == pygame.K_2:
                                        gameData["sprites"]["player"]["sheet_org"] = get_sprite("graphics/characters/player_sprite2.png", 128, 18)
                                        gameData["sprites_num"] = 2
                                if event.key == pygame.K_3:
                                        gameData["sprites"]["player"]["sheet_org"] = get_sprite("graphics/characters/player_sprite3.png", 128, 18)
                                        gameData["sprites_num"] = 3
                                if event.key == pygame.K_4:
                                        gameData["sprites"]["player"]["sheet_org"] = get_sprite("graphics/characters/player_sprite4.png", 128, 18)
                                        gameData["sprites_num"] =4
                                if event.key == pygame.K_5:
                                        gameData["sprites"]["player"]["sheet_org"] = get_sprite("graphics/characters/player_sprite5.png", 128, 18)
                                        gameData["sprites_num"] = 5
                                
                                if event.key == pygame.K_UP and not gameData["menu_options"]["CONTROL_WINDOW"]:
                                        pygame.mixer.Channel(2).play(pygame.mixer.Sound('sounds/menu_choice.ogg'))
                                        if not gameData["menu_options"]["counter"] == 0:
                                                gameData["menu_options"]["counter"]-=1
                                        else:
                                                gameData["menu_options"]["counter"] = 2

                                if event.key == pygame.K_DOWN and not gameData["menu_options"]["CONTROL_WINDOW"]:
                                        pygame.mixer.Channel(2).play(pygame.mixer.Sound('sounds/menu_choice.ogg'))
                                        if not gameData["menu_options"]["counter"] ==2:
                                                gameData["menu_options"]["counter"] +=1
                                        else: 
                                                gameData["menu_options"]["counter"] = 0

                        elif gameData["state"]["PAUSE"]:
                                if event.key == pygame.K_UP and not gameData["menu_options"]["CONTROL_WINDOW"]:
                                        pygame.mixer.Channel(2).play(pygame.mixer.Sound('sounds/menu_choice.ogg'))
                                        if not gameData["menu_options"]["counter"] == 0:
                                                gameData["menu_options"]["counter"]-=1
                                        else:
                                                gameData["menu_options"]["counter"] = 1

                                if event.key == pygame.K_DOWN and not gameData["menu_options"]["CONTROL_WINDOW"]:
                                        pygame.mixer.Channel(2).play(pygame.mixer.Sound('sounds/menu_choice.ogg'))
                                        if not gameData["menu_options"]["counter"]+ 1 ==2:
                                                gameData["menu_options"]["counter"] +=1
                                        else:
          
                                                gameData["menu_options"]["counter"] = 0
    
                                
                elif event.type == pygame.KEYUP:
                
                        if event.key == pygame.K_LSHIFT:
                                gameData["circle_hitbox"]["aim_gun"] = False

                        if event.key == pygame.K_a or event.key == pygame.K_d:
                                gameData["circle_hitbox"]["direction"] = "None"
                           
        return gameData
        
#This function is used to resume the game after the pause button is pressed. 
def resume_pause(gameData):
        gameData["state"]["PAUSE"] = False
        gameData["state"]["GAME"] = True
        gameData["OPACITY_SET"] = False
        gameData["pause_on"] = False
        pygame.mixer.Channel(0).unpause()
        return gameData

#This function is used to cycle through the menu options. 
def resume_menu(gameData):
       
        if gameData["menu_options"]["NEW"]:
                gameData["state"]["MENU"] = False
                gameData["state"]["TITLE"] = True
                gameData["music_on"] = False
                save_text("Save/Save.txt", "")
        elif gameData["menu_options"]["RESUME"]:
       
                if gameData["save_data"] == "LEVEL_1":
                    
                        gameData["level"][1]["state"] = True
                        gameData["level"][3]["state"] = False
                        gameData["level"][2]["state"] = False
                      
                if gameData["save_data"] == "LEVEL_2" or gameData["save_data"] == "LEVEL_2_KEY":
                        gameData["level"][1]["state"] = False
                        gameData["level"][2]["state"] = True
                        gameData["level"][3]["state"] = False
                        
                if gameData["save_data"] == "LEVEL_3":
                        gameData["level"][1]["state"] = False
                        gameData["level"][3]["state"] = True
                        gameData["level"][2]["state"] = False

                if gameData["save_data"] =="":
                        gameData["state"]["MENU"] = False
                        gameData["state"]["TITLE"] = True
                
                else:
                        gameData["state"]["MENU"] = False
                        gameData["state"]["GAME"] = True
                        gameData["music_on"] = False

        if gameData["menu_options"]["CONTROLS"]:                     
                gameData["menu_options"]["CONTROL_WINDOW"] = True
        

        return gameData

#This function moves the circle 
def move_circle(gameData):
        velocity_x = 15
        velocity_y = 15
        x, y = gameData["circle_hitbox"]["pos"]
        if (gameData["level"][3]["state"] or gameData["level"][4] or gameData["level"][1]["state"]) and not gameData["circle_hitbox"]["last_stand"]:
        
                if gameData["circle_hitbox"]["direction"] == "LEFT" and x-velocity_x >0:
                        x -= velocity_x
        
                elif gameData["circle_hitbox"]["direction"] == "RIGHT" and x+ velocity_x < window_wid:
                        x+= velocity_x

        if gameData["circle_hitbox"]["last_stand"]:
                gameData["circle_hitbox"]["fall"] = True
             
        if gameData["circle_hitbox"]["jump"]:
                gameData["circle_hitbox"]["jump_height"] += velocity_y

                if gameData["circle_hitbox"]["y_relative"] >=3400:
                        gameData["circle_hitbox"]["fall"] = True
                        gameData["circle_hitbox"]["jump"] = False

                if (gameData["circle_hitbox"]["x_relative"] <=-1460 and gameData["circle_hitbox"]["x_relative"] >= -1515) and y <=270:
                        gameData["circle_hitbox"]["jump"] = False
                        gameData["circle_hitbox"]["fall"] = True
        
                if  gameData["circle_hitbox"]["jump_height"] < 150:
                        gameData["sprites"]["player"]["JUMP_UP"] = True
                        gameData["sprites"]["player"]["JUMP_DOWN"] = False
                        if gameData["level"][1]["state"]:
                                gameData["circle_hitbox"]["y_relative"] += velocity_y
                        else:
                                y -= velocity_y
        
                else:
                        gameData["circle_hitbox"]["fall"] = True
                        gameData["circle_hitbox"]["jump"] = False

        else:
              for i in range(len(gameData["platforms"])):
                if gameData["level"][1]["state"]:
                        if platform_collision(gameData["platforms"][i], gameData) ==2:
                                gameData["circle_hitbox"]["fall"] = True

              gameData["sprites"]["player"]["JUMP_UP"] = False
              gameData["sprites"]["player"]["JUMP_DOWN"] = False  

        if gameData["circle_hitbox"]["fall"]:
                y = fall(gameData, y)
        
        gameData["circle_hitbox"]["pos"] = (x, y)
    
  
        return gameData["circle_hitbox"]

#This function handles the falling action of the circle_hitbox
def fall(gameData, y):
        velocity_x = 10
        if gameData["circle_hitbox"]["y_velocity"]<50:
                gameData["circle_hitbox"]["y_velocity"] += 2
       
        gameData["sprites"]["player"]["JUMP_UP"] = False
        gameData["sprites"]["player"]["JUMP_DOWN"] = True
        
        if gameData["level"][1]["state"]:
                gameData["circle_hitbox"]["y_relative"] -= gameData["circle_hitbox"]["y_velocity"]
                if gameData["circle_hitbox"]["y_relative"] <=0:
                        gameData["circle_hitbox"]["fall"] = False
                        gameData["circle_hitbox"]["y_relative"] = 0
                        gameData["terrain"]["location"] = (gameData["terrain"]["location"][0], 400)

        else:
                y += gameData["circle_hitbox"]["y_velocity"]
        
        
        if y >= gameData["terrain"]["location"][1]-gameData["circle_hitbox"]["rad"]:
               
               
                gameData["circle_hitbox"]["jump_height"] = 0
                y = gameData["terrain"]["location"][1]-gameData["circle_hitbox"]["rad"]
                gameData["circle_hitbox"]["fall"] = False

        for i in range(len(gameData["platforms"])):
                
                if gameData["level"][1]["state"]:
                        if platform_collision(gameData["platforms"][i], gameData) ==1:
                                gameData["sprites"]["player"]["JUMP_DOWN"] = False
                        
                             
                                gameData["circle_hitbox"]["jump_height"] = 0
                                gameData["circle_hitbox"]["fall"] = False
                                gameData["circle_hitbox"]["y_velocity"] = 0
                                break

        return y

#This function handles the collision detection for the platforms encountered in level 1. 
def platform_collision(platform, gameData):
       
        circle_x, circle_y = gameData["circle_hitbox"]["pos"]
        circle_y += gameData["circle_hitbox"]["rad"]
        plat_start_x, plat_start_y = platform["location"]
        plat_start_y +=gameData["circle_hitbox"]["y_relative"]
        plat_end_x = plat_start_x + platform["size"][0]
        plat_end_y = plat_start_y + platform["size"][1]

        if ((circle_y >= plat_start_y and circle_y <= plat_end_y) and (circle_x >= plat_start_x and circle_x <= plat_end_x)):
               
                gameData["circle_hitbox"]["y_relative"] += abs(circle_y-plat_start_y)
                return 1
        if (circle_y >= plat_start_y and circle_y <= plat_end_y) and not (circle_x >= plat_start_x and circle_x <= plat_end_x):
            
                return 2
        else:
                
                return 0

#This function is the "main" update function, handling every other update function here. 
def game_loop_update(gameData):

    if not gameData["circle_hitbox"]["col"]:
        gameData = update_circle_hitbox(gameData)

    if gameData["state"]["MENU"]:
        gameData = update_menu(gameData)
    elif gameData["state"]["GAMEOVER"]:
        gameData = update_gameOver(gameData)
    elif gameData["state"]["PAUSE"]:
 
        gameData = update_pause(gameData)
    elif gameData["state"]["TITLE"]:
        gameData = update_title(gameData)
    elif gameData["state"]["GAME"]:
        
        if gameData["level"][1]["state"]:
                gameData = update_level_1(gameData)
        elif gameData["level"][2]["state"]:
                update_level_2(gameData)
        elif gameData["level"][3]["state"]:
                update_level_3(gameData)
        elif gameData["level"][4]:
                update_level_4(gameData)

        if gameData["circle_hitbox"]["last_stand"] and gameData["circle_hitbox"]["col"]:
                gameData["circle_hitbox"]["health"]["num"]-=1

        else:
                gameData = update_last_stand(gameData)
        
        gameData["circle_hitbox"] = move_circle(gameData)
        gameData["circle_hitbox"]["col"] = False

       
        gameData = update_line(gameData)
        gameData = update_cannons(gameData)
        
        if gameData["level"][3]["state"] and gameData["circle_hitbox"]["health"]["num"] ==1:
                gameData["circle_hitbox"]["last_stand"] = True

        if gameData["circle_hitbox"]["health"]["num"] ==0:
                gameData["cannons"][9]["crosshair"]["exists"] = False
                gameData["cannons"][9]["rocket"]["exists"] = False
                gameData["circle_hitbox"]["dead"] = True
                for i in range(8):
                        gameData["cannons"][i]["rocket"]["exists"] = False
                for j in range(5):
                        gameData["rotating_lines"][j]["exists"] = False

        if gameData["circle_hitbox"]["health"]["num"] == 0 and not gameData["level"][3]["state"] and not gameData["state"]["GAMEOVER"]:
                        gameData["state"]["GAME"] = False
                        gameData["state"]["GAMEOVER"] = True
                        gameData["music_on"] = False
        
        if gameData["pause_on"]:
                        gameData["state"]["GAME"] = False
                        gameData["state"]["PAUSE"] = True
                        gameData["OPACITY_SET"] = False
                                        
        if gameData["sprites"]["fade_out"] >=150 and gameData["sprites"]["ending_on"]:
                save_text("Save/Save.txt", "LEVEL_1")
                sys.exit(0)

        if gameData["circle_hitbox"]["skip"]:
                gameData["circle_hitbox"]["skip"] = False
                gameData["circle_hitbox"]["shoot"] = False
                if  gameData["sprites"]["dialog"]["commander"]["counter"] <31*40:
                        gameData["sprites"]["dialog"]["commander"]["counter"] = 31*40

        
        if gameData["sprites"]["fade_out"] >=120 and not gameData["sprites"]["ending_on"]:
                gameData["sprites"]["ending_fade"] = True
                gameData["sprites"]["ending_on"] = True
                gameData["sprites"]["fade_out"] = 0
          
    return gameData

#This updates the title screen (The prologue that comes up after entering a new game)
def update_title(gameData):
        if gameData["scroll"] >-2500:
                gameData["scroll"]-=4

        if not gameData["music_on"]:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/Midnight.ogg'), loops = -1)
                gameData["music_on"] = True
        return gameData

#This handles the updates for level 1 (Moving up)
def update_level_1(gameData):
        if not gameData["music_on"]:
                gameData["level"]["newObjective"]["counter"] = 0
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/track4.ogg'), loops = -1)
                gameData["music_on"] = True

                for i in range(len(gameData["rotating_lines"])):
                        if i >2:
                                gameData["rotating_lines"][i]["exists"] = False
                        else:
                                gameData["rotating_lines"][i]["exists"] = True
                  
        for i in range(len(gameData["rotating_lines"])):
                gameData["rotating_lines"][i]["ori"] = (window_wid-50, (-(400+i*1200)+gameData["circle_hitbox"]["y_relative"]))   
                
        if  gameData["circle_hitbox"]["y_relative"] >= 3340:
                gameData["sprites"]["player"]["sheet"][0] = gameData["sprites"]["player"]["sheet"][15]

        if  gameData["sprites"]["Characters"]["commander"]["dead"]:
                gameData["level_counter"] +=1
        else:
                save_text("Save/Save.txt", "LEVEL_1")
       
        if gameData["level_counter"] == 100:
                gameData["level"][1]["state"] = False
                gameData["level"][2]["state"] = True
                gameData["new_game"] = True
                gameData["music_on"] = False

        gameData = update_chest(gameData)
        return gameData

#This handles the updates for level 2 (Moving right)
def update_level_2(gameData):
        
        if gameData["circle_hitbox"]["x_relative"] >=-10000:

                gameData["timer"]["mili_seconds"] +=  gameData["clock"].tick()*50
        
                if gameData["timer"]["mili_seconds"] >=1000:
                        gameData["timer"]["seconds"] +=1
                        gameData["timer"]["mili_seconds"] =0

                gameData["timer"]["time_left"] =100 - gameData["timer"]["seconds"]
        
        if load_text("Save/Save.txt") =="LEVEL_2_KEY":
                gameData["circle_hitbox"]["key"] = True
   
        if gameData["circle_hitbox"]["key"]:
                save_text("Save/Save.txt", "LEVEL_2_KEY")
        else:
                save_text("Save/Save.txt", "LEVEL_2")

        if not gameData["music_on"]:
                gameData["level"]["newObjective"]["counter"] = 0
                for i in range(8):
                        gameData["cannons"][i]["rocket"]["velocity"] =10
                gameData["cannons"][0]["location"] = (-64+gameData["circle_hitbox"]["x_relative"], 300)
                gameData["cannons"][0]["rocket"]["org_location"] = (-64+gameData["circle_hitbox"]["x_relative"], 318)
                gameData["cannons"][0]["rocket"]["location"] = (-64+gameData["circle_hitbox"]["x_relative"], 318)
                gameData["sprites"]["player"]["sheet_org"] = get_sprite("graphics/characters/player_sprite"+ str(gameData["sprites_num"])+".png", 128, 18)
                
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/Escape.ogg'), loops = -1)
                gameData["music_on"] = True
                for i in range(len(gameData["rotating_lines"])):
                        gameData["rotating_lines"][i]["exists"] = True

        if gameData["circle_hitbox"]["direction"] == "LEFT" and gameData["circle_hitbox"]["x_relative"]<0:
                gameData["circle_hitbox"]["x_relative"]+= gameData["velocity"]
        elif gameData["circle_hitbox"]["direction"] == "RIGHT" and gameData["circle_hitbox"]["x_relative"]> -12000:
                if not(gameData["circle_hitbox"]["x_relative"]- gameData["velocity"] <=-1500 and not (gameData["sprites"]["gate"]["health"] == 0 or gameData["sprites"]["gate"]["opened"])):
                        gameData["circle_hitbox"]["x_relative"]-=gameData["velocity"]

        gameData["cannons"][0]["location"] = (-64+gameData["circle_hitbox"]["x_relative"], 300)
        gameData["cannons"][0]["rocket"]["org_location"] = gameData["cannons"][0]["location"][0], gameData["cannons"][0]["location"][1]+18

        if gameData["circle_hitbox"]["x_relative"] <= -12000:
                gameData["level"][2]["state"] = False
                gameData["level"][4] = True
                gameData["new_game"] = True
                gameData["music_on"] = False

        for i in range(len(gameData["rotating_lines"])):
                        gameData["rotating_lines"][i]["ori"] = (gameData["rotating_lines"][i]["location"]+gameData["circle_hitbox"]["x_relative"],gameData["rotating_lines"][i]["ori"][1] )
        
        gameData["building_counter"]+=1
        if gameData["building_counter"] ==20:
                        gameData["building_counter"] = 0

        if gameData["timer"]["time_left"] ==0:
                gameData["state"]["GAME"] = False
                gameData["state"]["GAMEOVER"] = True
                gameData["music_on"] = False

        gameData = update_gate(gameData)
        return gameData

#This handles the updates for level 3 (Survival)
def update_level_3(gameData):
        save_text("Save/Save.txt", "LEVEL_3")
                               
        gameData["timer"]["mili_seconds"] += gameData["clock"].tick()*20

        if gameData["timer"]["mili_seconds"] >=1000:
                gameData["timer"]["seconds"] +=1
                gameData["timer"]["mili_seconds"] =0

        if gameData["new_level"]:
                gameData["timer"]["seconds"] = 0
                gameData["level"]["newObjective"]["counter"] = 0
        
                for i in range(5):
                        gameData["rotating_lines"][i]["ori"] = (window_wid*2, 20)
                        gameData["rotating_lines"][i]["exists"] = False

                gameData["new_level"] = False  
                gameData["rotating_lines"][0]["exists"] = True
                gameData["circle_hitbox"]["health"]["num"] = 4

        gameData["timer"]["seconds"]

        if gameData["timer"]["seconds"] == 30:
                gameData["rotating_lines"][1]["exists"] = True

        if gameData["timer"]["seconds"] == 60:
                gameData["rotating_lines"][2]["exists"] = True

        if gameData["timer"]["seconds"] == 90:
                gameData["rotating_lines"][3]["exists"] = True
        if gameData["timer"]["seconds"] == 120:
                gameData["rotating_lines"][4]["exists"] = True
                                
        gameData["sprites"]["sky"]["counter"] +=1//2
        if not gameData["music_on"]:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/Survive.ogg'), loops = -1)
                
                gameData["music_on"] = True

        return gameData

#This handles the updates for level 4 (Interaction with the supreme leader)
def update_level_4(gameData):
        for i in range(len(gameData["rotating_lines"])):
                gameData["rotating_lines"][i]["exists"] = False

        if not gameData["music_on"]:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/Leader.ogg'), loops = -1)
                gameData["music_on"] = True
                        
        if gameData["sprites"]["dialog"]["leader"]["counter"] >= 55*40:
                gameData["sprites"]["Characters"]["Leader"]["direction"] = "RIGHT"
        
        if gameData["sprites"]["Characters"]["Leader"]["x_cord"] >=1000 and gameData["sprites"]["Characters"]["Leader"]["direction"] == "RIGHT":
                gameData["level"][4] = False
                gameData["level"][3]["state"] = True
                gameData["music_on"] = False
                gameData["new_game"] = True
                gameData["new_level"] = True
        return gameData

#This handles the updates for the menu. 
def update_menu(gameData):
        if not gameData["music_on"]:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/menu2.ogg'), loops = -1)
                gameData["music_on"] = True
        
        if gameData["menu_options"]["counter"] == 0:
                gameData["menu_options"]["NEW"] = True
                gameData["menu_options"]["RESUME"] = False
                gameData["menu_options"]["CONTROLS"] = False
        if gameData["menu_options"]["counter"] == 1:
                gameData["menu_options"]["NEW"] = False
                gameData["menu_options"]["RESUME"] = True
                gameData["menu_options"]["CONTROLS"] = False
        
        if gameData["menu_options"]["counter"] == 2:
                gameData["menu_options"]["NEW"] = False
                gameData["menu_options"]["RESUME"] = False
                gameData["menu_options"]["CONTROLS"] = True
        return gameData

#This handles the updates for the cannons
def update_cannons(gameData):
        if gameData["level"][1]["state"]:
                for i in range(8):
                        update_cannon(gameData["cannons"][i], gameData)
        if  ((gameData["circle_hitbox"]["x_relative"] <=-1500 and gameData["circle_hitbox"]["x_relative"] >=-10000) and gameData["level"][2]["state"]) or (gameData["level"][3]["state"] and not gameData["circle_hitbox"]["dead"]):
                update_airstrike(gameData["cannons"][9], gameData)
                for i in range(8):
                        gameData["cannons"][i]["rocket"]["exists"] = False
                        gameData["cannons"][i]["shoot"] = False
                        gameData["cannons"][i]["counter"] = 0
        else:
                gameData["cannons"][9]["crosshair"]["exists"] = False
                gameData["cannons"][9]["rocket"]["exists"] = False

		

        if gameData["level"][2]["state"]:
                if gameData["circle_hitbox"]["x_relative"] >=-10000:
                        gameData["cannons"][0]["rocket"]["velocity"] =45
                        update_cannon(gameData["cannons"][0], gameData)
                else:
                        pygame.mixer.Channel(0).fadeout(3000)
                        gameData["cannons"][0]["rocket"]["exists"] = False
        return gameData
#This handles the updates for the gameover
def update_gameOver(gameData):
       
        if not gameData["music_on"]:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/GameOver.ogg'))
                pygame.mixer.Channel(5).stop()
                pygame.mixer.Channel(2).stop()
                gameData["music_on"] = True
        
        render_game_over(gameData)
        return gameData
#This handles the update for the chest (That spawns in level 1)
def update_chest(gameData):
        if gameData["sprites"]["chest"]["open"] and gameData["circle_hitbox"]["y_relative"] >=3340 and gameData["circle_hitbox"]["pos"][0] >=800 and gameData["circle_hitbox"]["pos"][0] <=900:
                gameData["sprites"]["chest"]["image"] = gameData["sprites"]["chest"]["sheet"][1]
                gameData["circle_hitbox"]["shoot"] = False
                gameData["circle_hitbox"]["key"] = True
                save_text("Save/Save.txt", "LEVEL_2_KEY")
                      
        else:
             gameData["sprites"]["chest"]["open"] = False  
        return gameData

#This handles the updates for the 3rd level for the lines, meaning it handles the spawining and moving mechanic. 
def update_line_level_3(rotating_line):
        x, y = rotating_line["ori"]
        if x-10 <0:
                rotating_line["direction"] = "RIGHT"
        if x+10>window_wid:
                rotating_line["direction"] = "LEFT"

        if rotating_line["direction"] == "LEFT":
                x -=10
        else:
                x+=10
      
        rotating_line["ori"] = (x, y)

        return rotating_line

#This handles the updates for the gate that you see at the begaining of level 2. 
def update_gate(gameData):
        if not gameData["sprites"]["gate"]["opened"]:
                gameData["sprites"]["gate"]["img"] = gameData["sprites"]["gate"]["spriteB"][abs(gameData["sprites"]["gate"]["health"]-3)]

                if  gameData["circle_hitbox"]["key"] and gameData["circle_hitbox"]["x_relative"]<=-1400:
                        gameData["sprites"]["gate"]["img"] = gameData["sprites"]["gate"]["spriteA"][gameData["sprites"]["gate"]["counter"]]
                        gameData["sprites"]["gate"]["counter"]+=1
                        if gameData["sprites"]["gate"]["counter"] >3:
                                gameData["sprites"]["gate"]["opened"] = True
        else:
                gameData["sprites"]["gate"]["img"] = gameData["sprites"]["gate"]["spriteA"][3]

        return gameData


        return gameData

#This handles the updates for the "last stand", meaning the momment in level 3 where the player is injured, and can't move. 
def update_last_stand(gameData):
        if gameData["circle_hitbox"]["col"]:
                gameData["sprites"]["player"]["sheet"] =  gameData["sprites"]["player"]["sheet_hit"]
                
                if gameData["circle_hitbox"]["health"]["num"] == 1:
                        pygame.mixer.Channel(3).play(pygame.mixer.Sound('sounds/die1.ogg'))
                else:
                        pygame.mixer.Channel(3).play(pygame.mixer.Sound('sounds/hit2.ogg'))
               
                gameData["circle_hitbox"]["health"]["num"]-=1
        else:
        
                gameData["sprites"]["player"]["sheet"] =  gameData["sprites"]["player"]["sheet_org"] 
        return gameData

#This handles the updates for the circle_hitbox
def update_circle_hitbox(gameData):

        if gameData["circle_hitbox"]["last_key"] == "LEFT":
                gameData["sprites"]["player"]["img"] = gameData["sprites"]["player"]["sheet"][0]
                gameData["sprites"]["player"]["img"] = pygame.transform.flip(gameData["sprites"]["player"]["img"], True, False)

        else:
                gameData["sprites"]["player"]["img"] = gameData["sprites"]["player"]["sheet"][0]

                if gameData["level"][1]["state"] and gameData["circle_hitbox"]["y_relative"] >= 3340:
                        if gameData["circle_hitbox"]["aim_gun"] and gameData["sprites"]["dialog"]["commander"]["counter"] >=31*40:
                                gameData["sprites"]["player"]["img"] = gameData["sprites"]["player"]["sheet"][16]
                                
                                if gameData["circle_hitbox"]["shoot"]:
                                        gameData["sprites"]["player"]["img"] = gameData["sprites"]["player"]["sheet"][17]
                                        pygame.mixer.music.load("sounds/shot.ogg")
                                        pygame.mixer.music.play()
                                        
                                        if gameData["sprites"]["Characters"]["commander"]["counter"] <30:
                                                gameData["sprites"]["dialog"]["commander"]["counter"] = 45*40
                                                pygame.mixer.Channel(1).play(pygame.mixer.Sound('sounds/shot1.ogg'))
                                        elif gameData["sprites"]["Characters"]["commander"]["counter"] <60:
                                                gameData["sprites"]["dialog"]["commander"]["counter"] = 48*40
                                                pygame.mixer.Channel(1).play(pygame.mixer.Sound('sounds/shot2.ogg'))
                                        elif gameData["sprites"]["Characters"]["commander"]["counter"] <100:
                                                gameData["sprites"]["dialog"]["commander"]["counter"] = 51*40
                                                pygame.mixer.Channel(1).play(pygame.mixer.Sound('sounds/shot3.ogg'))
                                        elif gameData["sprites"]["Characters"]["commander"]["counter"] <140:
                                                gameData["sprites"]["Characters"]["commander"]["dead"] = True
                        
                                
                                        gameData["sprites"]["Characters"]["commander"]["shot"] = True
                                
                                        gameData["circle_hitbox"]["shoot"] = False

        if gameData["circle_hitbox"]["direction"] == "RIGHT":
                gameData["sprites"]["player"]["img"] = gameData["sprites"]["player"]["sheet"][gameData["sprites"]["player"]["counter"]//5]
                gameData["sprites"]["player"]["counter"]+=5
                if gameData["sprites"]["player"]["counter"] >=45:
                        gameData["sprites"]["player"]["counter"] = 5
                
        if gameData["circle_hitbox"]["direction"] == "LEFT":
                
                gameData["sprites"]["player"]["img"] = gameData["sprites"]["player"]["sheet"][gameData["sprites"]["player"]["counter"]//5]    
                gameData["sprites"]["player"]["counter"]+=5
                if gameData["sprites"]["player"]["counter"] >=45:
                        gameData["sprites"]["player"]["counter"] = 5

        if gameData["sprites"]["player"]["JUMP_UP"]:
                gameData["sprites"]["player"]["img"] = gameData["sprites"]["player"]["sheet"][9]

        if gameData["sprites"]["player"]["JUMP_DOWN"]:
                gameData["sprites"]["player"]["img"] = gameData["sprites"]["player"]["sheet"][10]
        
        else:
      
                gameData["sprites"]["player"]["jumpCounter"] = 45

        if  gameData["circle_hitbox"]["last_stand"]:
                
                if gameData["circle_hitbox"]["health"]["num"] ==1:

                        if gameData["circle_hitbox"]["heartbeat"] ==0:
                                pygame.mixer.music.load("sounds/heartbeat.ogg")
                                pygame.mixer.music.set_volume(1)
                                pygame.mixer.music.play(-1)

                                gameData["circle_hitbox"]["heartbeat"] +=1
                
                        if gameData["circle_hitbox"]["last_stand_counter"] <=1:
                                gameData["sprites"]["player"]["img"] = gameData["sprites"]["player"]["sheet"][11]
                        else:
                                gameData["sprites"]["player"]["img"] = gameData["sprites"]["player"]["sheet"][12]
                        gameData["circle_hitbox"]["last_stand_counter"]+=1
                        
                if gameData["circle_hitbox"]["health"]["num"] ==0:
                        pygame.mixer.music.stop()
                
                        if gameData["circle_hitbox"]["dead_counter"] <= 20:
                                gameData["sprites"]["player"]["img"] = gameData["sprites"]["player"]["sheet"][13]

                        else:
                                gameData["sprites"]["player"]["img"] = gameData["sprites"]["player"]["sheet"][14]

                        gameData["circle_hitbox"]["dead_counter"] +=1
                        

        return gameData

#This handles the updates for the lines
def update_line(gameData):
        angle_mutliple = 1
        for i in range(5):
        
                if gameData["rotating_lines"][i]["exists"] and gameData["level"][3]["state"]:
                        gameData["rotating_lines"][i] = update_line_level_3(gameData["rotating_lines"][i])
                # increase the angle of the rotating line
                gameData["rotating_lines"][i]["ang"] = (gameData["rotating_lines"][i]["ang"] + angle_mutliple)
             
                angle_mutliple +=0.3
        
                # the rotating line angle ranges between 90 and 180 degrees
                if gameData["rotating_lines"][i]["ang"] > 180:

                        gameData["rotating_lines"][i]["ang"] = 90
                        
                # the points associated with each line segment must be recalculated as the angle changes
                gameData["rotating_lines"][i]["seg"] = []
                #rotating_line["velocity"] +=1
                
                # consider every line segment length
                for len in gameData["rotating_lines"][i]["len"]:
                # compute the start of the line...
                
                        sol_x = gameData["rotating_lines"][i]["ori"][0] + gameData["rotating_lines"][i]["velocity"] + math.cos(math.radians(gameData["rotating_lines"][i]["ang"])) * window_wid * len[0]
                        sol_y = gameData["rotating_lines"][i]["ori"][1] + math.sin(math.radians(gameData["rotating_lines"][i]["ang"])) * window_wid * len[0]
                                # ...and the end of the line...
                        eol_x = gameData["rotating_lines"][i]["ori"][0] + gameData["rotating_lines"][i]["velocity"] + math.cos(math.radians(gameData["rotating_lines"][i]["ang"])) * window_wid * len[1]
                        eol_y = gameData["rotating_lines"][i]["ori"][1] + math.sin(math.radians(gameData["rotating_lines"][i]["ang"])) * window_wid * len[1]
                                # ...and then add that line to the list
                        gameData["rotating_lines"][i]["seg"].append( ((sol_x, sol_y), (eol_x, eol_y)) )
                 
                # start by assuming that no collisions have occurred
                        
                # consider possible collisions between the circle hitbox and each line segment
                for seg in gameData["rotating_lines"][i]["seg"]:
                
                        # if there is any collision at all, the circle hitbox flag is set
                        if detect_collision_line_circ(seg, (gameData["circle_hitbox"]["pos"], gameData["circle_hitbox"]["rad"])) and gameData["rotating_lines"][i]["exists"]:
                                
                                if gameData["circle_hitbox"]["is_hit_counter"] ==0 and gameData["rotating_lines"][i]["exists"]:
                                        gameData["circle_hitbox"]["col"] = True
                                        
                                        gameData["circle_hitbox"]["is_hit_counter"] +=1
                                
                                break
                
                if gameData["circle_hitbox"]["is_hit_counter"] >=1:
                        gameData["circle_hitbox"]["is_hit_counter"] +=1
                if gameData["circle_hitbox"]["is_hit_counter"] == 100:
                        gameData["circle_hitbox"]["is_hit_counter"]  = 0
        
        return gameData

#This handles the updates for the airstrike (The missles that fall in level 2)
def update_airstrike(airstrike, gameData):
        if  airstrike["counter"] ==0:
                airstrike["crosshair"]["location"] = (random.randint(32, 936)-32, 0)

                if not gameData["circle_hitbox"]["last_stand"]:
                        pygame.mixer.Channel(5).play(pygame.mixer.Sound('sounds/warning.ogg'))
                else:
                        pygame.mixer.Channel(5).stop()
                airstrike["crosshair"]["exists"] = True
                airstrike["counter"]+=1

        if airstrike["crosshair"]["exists"]:
                airstrike["warning_counter"] +=1

        if airstrike["warning_counter"] ==20:
                airstrike["warning_counter"] = 0
                if not gameData["circle_hitbox"]["last_stand"]:
                        pygame.mixer.Channel(5).play(pygame.mixer.Sound('sounds/rocket.ogg'))
                else:
                        pygame.mixer.Channel(5).stop()
                airstrike["crosshair"]["exists"] = False
                airstrike["rocket"]["org_location"] = (gameData["circle_hitbox"]["x_relative"], 0)
                airstrike["rocket"]["location"] = airstrike["crosshair"]["location"][0], 0
                airstrike["rocket"]["exists"] = True

        if airstrike["rocket"]["exists"]:

                x, y = airstrike["rocket"]["location"]
              
                circle_x, circle_y = gameData["circle_hitbox"]["pos"]
                circle_y-= gameData["circle_hitbox"]["rad"]
                circle_x -= gameData["circle_hitbox"]["rad"]
                if airstrike["rocket"]["location"][1]+airstrike["rocket"]["velocity"]>=400:
                        airstrike["rocket"]["exists"] = False
                        airstrike["hit_ground"] = True

                airstrike["rocket"]["location"] = (x, y+ airstrike["rocket"]["velocity"])
                collide_x = x+gameData["circle_hitbox"]["x_relative"]-airstrike["rocket"]["org_location"][0]

                if (collide_x>= circle_x and collide_x<=circle_x+128) and (y+gameData["circle_hitbox"]["y_relative"] >=circle_y+20 and y+gameData["circle_hitbox"]["y_relative"] <= circle_y+128):
                        airstrike["rocket"]["exists"]= False
                     
                        airstrike["hit"] = True
                       
                        gameData["circle_hitbox"]["col"] = True  

                
        airstrike["counter"]+=1

        if airstrike["counter"]==30:
                airstrike["counter"] = 0

        return

#This handles the cannon updates
def update_cannon(cannon, gameData):
        
        x, y = cannon["rocket"]["location"]
        circle_x, circle_y = gameData["circle_hitbox"]["pos"]
        circle_y-= gameData["circle_hitbox"]["rad"]
        circle_x -= gameData["circle_hitbox"]["rad"]

        if (x+120)>= 2000+gameData["circle_hitbox"]["x_relative"] and not gameData["sprites"]["gate"]["health"] ==0 and not gameData["sprites"]["gate"]["opened"]:
                cannon["hit"] = True
                cannon["hitLocation"] = x, y
                cannon["rocket"]["exists"]= False
                gameData["sprites"]["gate"]["health"] -=1
                pygame.mixer.Channel(3).play(pygame.mixer.Sound('sounds/gate.ogg'))
        
        if (x+20>= circle_x and x+20<=circle_x+128) and (y+gameData["circle_hitbox"]["y_relative"] >=circle_y+20 and y+gameData["circle_hitbox"]["y_relative"] <= circle_y+128):
                cannon["rocket"]["exists"]= False
        
                cannon["hit"] = True
                cannon["hitLocation"] = x, y
                gameData["circle_hitbox"]["col"] = True    
        
               
        if (gameData["level"][1]["state"] and cannon["counter"] >=35) or (gameData["level"][2]["state"] and cannon["counter"] >=40):
                cannon["rocket"]["exists"] = True
                cannon["shoot"] = False
                cannon["counter"] = 0
                pygame.mixer.Channel(2).play(pygame.mixer.Sound('sounds/rocket.ogg'))
        
        if cannon["rocket"]["exists"]:
                cannon["rocket"]["location"] = (x+cannon["rocket"]["velocity"], y)
        else:
                cannon["rocket"]["location"] = cannon["rocket"]["org_location"]
                cannon["counter"] +=1
        
        if x >= window_wid:
                cannon["rocket"]["exists"] = False


        return
#This handles the updates to the pause (The counter value dictating whether to resume/quit)
def update_pause(gameData):

        
        gameData["OPACITY_FADE"] = pygame.surface.Surface((window_wid, window_hgt))
        gameData["OPACITY_FADE"].set_alpha(128)
        pygame.mixer.Channel(0).pause()
       
        if gameData["menu_options"]["counter"] == 0:
                gameData["menu_options"]["NEW"] = True
                gameData["menu_options"]["RESUME"] = False
                gameData["menu_options"]["CONTROLS"] = False
        if gameData["menu_options"]["counter"] == 1:
                gameData["menu_options"]["NEW"] = False
                gameData["menu_options"]["RESUME"] = True
                gameData["menu_options"]["CONTROLS"] = False
                        
        return gameData

#This handles the actual commander dialog updates
def render_commander_dialog(gameData):
        if gameData["sprites"]["Characters"]["commander"]["dead"]:
                gameData["level"][1]["text"] = "COMPLETE"
                pygame.mixer.Channel(0).fadeout(3000)
        elif gameData["sprites"]["dialog"]["commander"]["counter"]//40 >=31:
                gameData["level"][1]["text"] = "ASSASSINATE"
                render_useful_text(gameData, "HOLD LEFT SHIFT AND PRESS ENTER TO SHOOT")

        elif gameData["sprites"]["dialog"]["commander"]["counter"]//40 <=31 and not gameData["sprites"]["Characters"]["commander"]["dead"]:
                render_useful_text(gameData, "PRESS ENTER TO SKIP")

        if gameData["sprites"]["dialog"]["commander"]["counter"] <55*40 and not gameData["sprites"]["Characters"]["commander"]["dead"]:
                dialog_c = gameData["sprites"]["dialog"]["commander"]["counter"]
                gameData["sprites_c"] = gameData["sprites"]["Characters"]["commander"]["counter"]
                if not (dialog_c//40 == 44 or dialog_c//40 == 47 or dialog_c//40 == 50 or dialog_c//40 == 54):
                        gameData["sprites"]["dialog"]["commander"]["counter"] +=1

        return gameData
#This is the main render function, responsable for all the other render functions. 
def game_loop_render(gameData):

        if gameData["level"][1]["state"]:
                blit_level_1(gameData)
        elif gameData["level"][2]["state"]:
                blit_level_2(gameData)
        elif gameData["level"][3]["state"]:
                blit_level_3(gameData)
        elif gameData["level"][4]:
                blit_level_4(gameData)

        if gameData["level"][1]["state"] and gameData["circle_hitbox"]["y_relative"] >= 3340:
                
                if gameData["sprites"]["dialog"]["commander"]["counter"] <55*40 and not gameData["sprites"]["Characters"]["commander"]["dead"]:
                        gameData["window"].blit(gameData["sprites"]["dialog"]["commander"]["image"][gameData["sprites"]["dialog"]["commander"]["counter"]//40], (500,0))
                        

        x, y = gameData["terrain"]["size"]
        x_circle, y_circle = gameData["circle_hitbox"]["pos"]

        render_lines(gameData)

        if not gameData["circle_hitbox"]["col"]:
                if  gameData["circle_hitbox"]["last_stand"]:
                        gameData["window"].blit(gameData["sprites"]["player"]["img"], (x_circle-gameData["circle_hitbox"]["rad"], y_circle-gameData["circle_hitbox"]["rad"]))
                else:
                        if gameData["circle_hitbox"]["direction"] == "LEFT" or ( (gameData["sprites"]["player"]["JUMP_UP"] or gameData["sprites"]["player"]["JUMP_DOWN"]) and   gameData["circle_hitbox"]["last_key"] == "LEFT"):   
                                gameData["window"].blit(pygame.transform.flip(gameData["sprites"]["player"]["img"], True, False), (x_circle-gameData["circle_hitbox"]["rad"], y_circle-gameData["circle_hitbox"]["rad"]))
                        else:
                                gameData["window"].blit(gameData["sprites"]["player"]["img"], (x_circle-gameData["circle_hitbox"]["rad"], y_circle-gameData["circle_hitbox"]["rad"]))

        render_cannons(gameData)
                                
        render_objectives(gameData)

        if gameData["circle_hitbox"]["dead_counter"]<=20:
                if gameData["level"][3]["state"]:
                        gameData["window"].blit(gameData["circle_hitbox"]["health"]["sheet"][gameData["circle_hitbox"]["health"]["num"]], (10, 5))
                else:
                        if gameData["circle_hitbox"]["health"]["num"] ==2:
                                gameData["window"].blit(gameData["circle_hitbox"]["health"]["sheet"][4], (10, 5))
                        if gameData["circle_hitbox"]["health"]["num"] ==1:
                                gameData["window"].blit(gameData["circle_hitbox"]["health"]["sheet"][2], (10, 5))
                        if gameData["circle_hitbox"]["health"]["num"] ==0:
                                gameData["window"].blit(gameData["circle_hitbox"]["health"]["sheet"][0], (10, 5))
                
        if gameData["circle_hitbox"]["key"] and gameData["circle_hitbox"]["key_counter"] <=15 and gameData["level"][1]["state"]:
                gameData = render_key(gameData)

        if (gameData["level"][2]["state"] and gameData["circle_hitbox"]["x_relative"] <=-10000) or (gameData["level"][1]["state"] and gameData["sprites"]["Characters"]["commander"]["dead"]):
                if gameData["level"]["complete"]["counter"] <=15:
                        text_x, text_y = gameData["level"]["complete"]["text"].get_size()
                        gameData["window"].blit(gameData["level"]["complete"]["text"], (500-text_x//2,250-text_y//2))
                        gameData["level"][2]["text"] = "COMPLETE"
                        gameData["level"]["complete"]["counter"] +=1

        if gameData["sprites"]["ending_on"]:  
                render_ending(gameData)
                
        elif gameData["circle_hitbox"]["dead_counter"]>20:
                fade_out(gameData)
                pygame.mixer.Channel(0).fadeout(7000)

        if gameData["state"]["MENU"]:
                render_menu(gameData)
        elif gameData["state"]["TITLE"]:
                gameData["window"].blit(gameData["sprites"]["Title"]["image"], (0, gameData["scroll"]))

        elif gameData["state"]["PAUSE"]:
        
                gameData["window"].blit(gameData["OPACITY_FADE"], (0,0))
                gameData["window"].blit(gameData["sprites"]["Pause"]["image"][gameData["menu_options"]["counter"]], (0,0))

#This handles the rendering of the objectives text that appear on the top left.        
def render_objectives(gameData):
        font = pygame.font.SysFont('Times New Roman', 20, True)
        for i in range(1, 4):
                if gameData["level"][i]["state"] and gameData["circle_hitbox"]["dead_counter"]<=20:             
                        if  gameData["level"]["newObjective"]["counter"] <=15:
                                new_objective_font = pygame.font.SysFont('Times New Roman', 30, True)
                                new_objective =  new_objective_font.render("NEW OBJECTIVE ", False, (0, 160, 255))
                                text_x_objective, text_y_objective = new_objective.get_size()
                                gameData["window"].blit(new_objective, (500-text_x_objective//2,175-text_y_objective//2))

                                text_font = pygame.font.SysFont('Times New Roman', 50, True)
                                objective_text = text_font.render(gameData["level"][i]["text"], False, (0, 160, 255))
                                text_x, text_y = objective_text.get_size()
                                gameData["window"].blit(objective_text, (500-text_x//2,text_y_objective +200-text_y//2))

                                gameData["level"]["newObjective"]["counter"] +=1
                        else:
                                text = font.render(("OBJECTIVE: " + gameData["level"][i]["text"]), False, (0,160,255))
                                gameData["window"].blit(text, (10,40))
                        break

#This handles the rendering of the "key found" text that appears once you've unlocked the key.
def render_key(gameData):
        key_font = pygame.font.SysFont('Times New Roman', 30, True)
        text = key_font.render("Exit Key unlocked!", False, (0,160,255))
        text_x, text_y = text.get_size()
        gameData["window"].blit(text, (500-text_x//2,250-text_y//2))
        gameData["circle_hitbox"]["key_counter"] +=1
        return gameData

#This handles the render for the ending (The text that appears)
def render_ending(gameData):
        if gameData["sprites"]["ending_play_music"]:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('music/ending.ogg'))
                
                gameData["sprites"]["ending_play_music"] = False
        gameData["window"].blit(gameData["sprites"]["ending"], (0,0))

        if gameData["sprites"]["ending_counter"] >=400:
                gameData["sprites"]["ending_fade"] = False
                           
        if  gameData["sprites"]["ending_fade"]:
                fade_in(gameData)    

        else:
                pygame.mixer.Channel(0).fadeout(15000)
                fade_out(gameData)
                gameData["circle_hitbox"]["y_relative"] = 0

#This renders the lines             
def render_lines(gameData):
        for i in range(len(gameData["rotating_lines"])):
                if gameData["rotating_lines"][i]["exists"]:
                        rotated_img = pygame.transform.rotate(gameData["sprites"]["laser"]["image"], 360-gameData["rotating_lines"][i]["ang"])
                        center = (gameData["rotating_lines"][i]["ori"][0]+50, gameData["rotating_lines"][i]["ori"][1])
                        if gameData["level"][2]["state"] and i>=1:
                                gameData["window"].blit(gameData["sprites"]["tower"], (gameData["rotating_lines"][i]["ori"][0]+22, gameData["rotating_lines"][i]["ori"][1]))
                        gameData["window"].blit(rotated_img, rotated_img.get_rect(center = center))

#This renders the cannons    
def render_cannons(gameData):
        for i in range(8):
                if  gameData["cannons"][i]["rocket"]["exists"]:
                        gameData["window"].blit(gameData["cannons"][i]["rocket"]["sprite"], (gameData["cannons"][i]["rocket"]["location"][0], gameData["cannons"][i]["rocket"]["location"][1]+gameData["circle_hitbox"]["y_relative"]))

                if gameData["cannons"][i]["hit"]:
                        explosion_image = gameData["cannons"][8]["sheet"][gameData["cannons"][8]["counter"]//5]
                        gameData["window"].blit(explosion_image, (gameData["cannons"][i]["hitLocation"][0], gameData["cannons"][i]["hitLocation"][1]+gameData["circle_hitbox"]["y_relative"])) 
                        gameData["cannons"][8]["counter"]+=5
                        if  gameData["cannons"][8]["counter"] >=20:
                                gameData["cannons"][8]["counter"] = 0
                                gameData["cannons"][i]["hit"] = False
                if not gameData["level"][3]["state"]:
                        gameData["window"].blit(gameData["cannons"][i]["sprite"], (gameData["cannons"][i]["location"][0], gameData["cannons"][i]["location"][1]+gameData["circle_hitbox"]["y_relative"]))

        if (gameData["circle_hitbox"]["x_relative"] <=-1500 and gameData["level"][2]["state"]) or gameData["level"][3]["state"]:
                if gameData["cannons"][9]["crosshair"]["exists"]:
                        gameData["window"].blit(gameData["cannons"][9]["crosshair"]["sprite"], (gameData["cannons"][9]["crosshair"]["location"][0], 0))

                if gameData["cannons"][9]["rocket"]["exists"]:
                       
                        gameData["window"].blit(gameData["cannons"][9]["rocket"]["sprite"], (gameData["cannons"][9]["rocket"]["location"][0]+gameData["circle_hitbox"]["x_relative"]-gameData["cannons"][9]["rocket"]["org_location"][0], gameData["cannons"][9]["rocket"]["location"][1]))

                if gameData["cannons"][9]["hit_ground"]:
                        explosion_image = gameData["cannons"][8]["sheet"][gameData["cannons"][8]["counter"]//5]
                        gameData["window"].blit(explosion_image, (gameData["cannons"][9]["rocket"]["location"][0]+gameData["circle_hitbox"]["x_relative"]-gameData["cannons"][9]["rocket"]["org_location"][0], 320)) 
                        gameData["cannons"][8]["counter"]+=5
                        if gameData["cannons"][8]["counter"] >=20:
                                gameData["cannons"][8]["counter"] = 0
                                gameData["cannons"][9]["hit_ground"] = False

                if  gameData["cannons"][9]["hit"]:
                        explosion_image = gameData["cannons"][8]["sheet"][gameData["cannons"][8]["counter"]//5]
                        gameData["window"].blit(explosion_image, (gameData["cannons"][9]["rocket"]["location"][0]+gameData["circle_hitbox"]["x_relative"]-gameData["cannons"][9]["rocket"]["org_location"][0], gameData["cannons"][9]["rocket"]["location"][1])) 
                        gameData["cannons"][8]["counter"]+=5
                        if  gameData["cannons"][8]["counter"] >=20:
                                gameData["cannons"][8]["counter"] = 0
                                gameData["cannons"][9]["hit"] = False

#This renders the leader that appears in level 4
def render_leader(gameData):
         
        gameData["sprites"]["Characters"]["Leader"]["image"] = gameData["sprites"]["Characters"]["Leader"]["sheet"][gameData["sprites"]["Characters"]["Leader"]["counter"]//5]
        gameData["sprites"]["Characters"]["Leader"]["counter"] +=2


        if gameData["sprites"]["Characters"]["Leader"]["counter"] >=35:
                    gameData["sprites"]["Characters"]["Leader"]["counter"] = 5
        
        if gameData["sprites"]["Characters"]["Leader"]["direction"] == "LEFT":
                if gameData["sprites"]["Characters"]["Leader"]["x_cord"]>=700:
                        gameData["sprites"]["Characters"]["Leader"]["x_cord"]-=3
                else:
                        gameData["sprites"]["Characters"]["Leader"]["image"] = gameData["sprites"]["Characters"]["Leader"]["sheet"][0]
                        render_useful_text(gameData, "PRESS ENTER TO SKIP")
                gameData["window"].blit(pygame.transform.flip(gameData["sprites"]["Characters"]["Leader"]["image"], True, False), (gameData["sprites"]["Characters"]["Leader"]["x_cord"], window_hgt-100-128))
        else:
                gameData["sprites"]["Characters"]["Leader"]["x_cord"]+=3
                pygame.mixer.Channel(0).fadeout(5000)
                gameData["window"].blit(gameData["sprites"]["Characters"]["Leader"]["image"], (gameData["sprites"]["Characters"]["Leader"]["x_cord"], window_hgt-100-128))

#This handles useful text rendering, such as "press _ to skip", etc...
def render_useful_text(gameData, text_string):
        font = pygame.font.SysFont('Times New Roman', 30)
        text = font.render(text_string, False, (0,160,255))
        x, y = text.get_size()
        gameData["window"].blit(text, (window_wid/2-x//2 ,450-y//2))
        
        return 

#This handles the menu rendering. 
def render_menu(gameData):
        if  gameData["menu_options"]["CONTROL_WINDOW"]:
                gameData["window"].blit(gameData["sprites"]["Menu"]["image"][3], (0,0) )
        else:
                gameData["window"].blit(gameData["sprites"]["Menu"]["image"][gameData["menu_options"]["counter"]], (0,0))
#This handles the game over rendering screen. 
def render_game_over(gameData):
    
    gameData["sprites"]["gameOver"]["counter"] +=1
    
    fade = pygame.surface.Surface((window_wid, window_hgt))
    fade.set_alpha(int(gameData["sprites"]["gameOver"]["counter"]*1.5))
    gameData["window"].blit(fade, (0,0))
   
    if gameData["sprites"]["gameOver"]["counter"]*1.5 >=60:
            gameData["sprites"]["gameOver"]["image"].set_alpha(gameData["sprites"]["gameOver"]["counter"]*2-60)
            gameData["window"].blit(gameData["sprites"]["gameOver"]["image"], (window_wid//2- gameData["sprites"]["gameOver"]["size"][0]//2, window_hgt//2-gameData["sprites"]["gameOver"]["size"][1]//2))
    
    alpha = gameData["sprites"]["gameOver"]["image"].get_at((0,0))
    gameData["sprites"]["gameOver"]["image"].set_colorkey(alpha)
     

#This function gets the sprite sheet file, and cuts it up into individual images, which are then added to a list.         
def get_sprite(sheet_file, size, range_num):

        sprite_sheet = []
        sheet = pygame.image.load(sheet_file).convert()

        for i in range(range_num):
                width = size
                height = size
                rect = pygame.Rect(i*width, 0, width, height)
                image = pygame.Surface(rect.size).convert()
                image.blit(sheet, (0,0), rect)
                alpha = image.get_at((0,0))
                image.set_colorkey(alpha)
                image.set_colorkey((255, 255, 255))
                sprite_sheet.append(image)

        return sprite_sheet

#This handles the "fade in" screen 
def fade_in(gameData):
       
                fade = pygame.surface.Surface((window_wid, window_hgt))
                fade.set_alpha(255-gameData["sprites"]["ending_counter"]*2)
                gameData["window"].blit(fade, (0,0))
                gameData["sprites"]["ending_counter"] +=1

#This handles the "fade out" screen
def fade_out(gameData):
       fade = pygame.surface.Surface((window_wid, window_hgt))
       fade.set_alpha(gameData["sprites"]["fade_out"]*3)
       gameData["window"].blit(fade, (0,0))
       gameData["sprites"]["fade_out"] +=1

#This handles the rendering of level 1
def blit_level_1(gameData):
        gameData["terrain"]["location"] = (gameData["terrain"]["location"][0], gameData["terrain"]["location"][1]+gameData["circle_hitbox"]["y_relative"])
        gameData["window"].blit(gameData["sprites"]["sky"]["image"], (gameData["circle_hitbox"]["x_relative"]/100, 0))
        gameData["window"].blit(gameData["sprites"]["sky"]["moon"], (gameData["circle_hitbox"]["x_relative"]/50,  gameData["circle_hitbox"]["y_relative"]//50))
        gameData["window"].blit(gameData["sprites"]["backgroundFar"]["image"], (gameData["circle_hitbox"]["x_relative"]//30,     gameData["circle_hitbox"]["y_relative"]//25))
        gameData["window"].blit(gameData["sprites"]["background"]["image"], (gameData["circle_hitbox"]["x_relative"]//10,    gameData["circle_hitbox"]["y_relative"]//12))
        gameData["window"].blit(gameData["sprites"]["level1"]["image"], (0, -3500+gameData["circle_hitbox"]["y_relative"]))

        gameData["window"].blit(gameData["sprites"]["chest"]["image"], (850, -3021+gameData["circle_hitbox"]["y_relative"]))
      
        for i in range(len(gameData["platforms"])):
                if gameData["platforms"][i]["image_exists"]:
                        gameData["window"].blit(gameData["platforms"][i]["image"], (gameData["platforms"][i]["location"][0],  gameData["platforms"][i]["org"][1] +gameData["circle_hitbox"]["y_relative"]))
             
        if gameData["circle_hitbox"]["y_relative"] >= 3340:
                gameData = render_commander_dialog(gameData)
        render_commander(gameData)

        return

#This handles the rendering of level 2
def blit_level_2(gameData):
        gameData["window"].blit(gameData["sprites"]["sky"]["image"], (gameData["circle_hitbox"]["x_relative"]/100,0))
        gameData["window"].blit(gameData["sprites"]["sky"]["moon"], (gameData["circle_hitbox"]["x_relative"]/50, 0))
        gameData["window"].blit(gameData["sprites"]["backgroundFar"]["image"], (gameData["circle_hitbox"]["x_relative"]//30, 0))
        gameData["window"].blit(gameData["sprites"]["background"]["image"], (gameData["circle_hitbox"]["x_relative"]//10,0))
        gameData["window"].blit(gameData["sprites"]["ground"]["image"], (gameData["circle_hitbox"]["x_relative"],(gameData["terrain"]["location"][1])-84))
        gameData["window"].blit(gameData["sprites"]["sign"]["image"], (9900+ gameData["circle_hitbox"]["x_relative"],0))
        
        if gameData["building_counter"] <10:
                gameData["window"].blit(gameData["sprites"]["building"]["image"]["blue"], (gameData["circle_hitbox"]["x_relative"], 0))
                if gameData["circle_hitbox"]["x_relative"] > -1700:
                        pygame.mixer.music.load("sounds/alarm.ogg")
                        pygame.mixer.music.play()
        
        else:
                gameData["window"].blit(gameData["sprites"]["building"]["image"]["red"], (gameData["circle_hitbox"]["x_relative"], 0))
        gameData["window"].blit(gameData["sprites"]["gate"]["img"], (1974+gameData["circle_hitbox"]["x_relative"], 59))
        renderTime(gameData)
        return

#This handles the rendering of level 3
def blit_level_3(gameData):
        gameData["window"].blit(gameData["sprites"]["sky"]["image"], (gameData["circle_hitbox"]["x_relative"]/100,0))
        gameData["window"].blit(gameData["sprites"]["sky"]["moon"], (gameData["circle_hitbox"]["x_relative"]/50, 0))
        gameData["window"].blit(gameData["sprites"]["backgroundFar"]["image"], (gameData["circle_hitbox"]["x_relative"]//30, 0))
        gameData["window"].blit(gameData["sprites"]["background"]["image"], (gameData["circle_hitbox"]["x_relative"]//10,0))
        gameData["window"].blit(gameData["sprites"]["ground"]["image"], (-10000,(gameData["terrain"]["location"][1])-84))

        if gameData["circle_hitbox"]["dead_counter"]<=20:
                renderTime(gameData)
        return

#This handles the rendering of level 4
def blit_level_4(gameData):
        gameData["window"].blit(gameData["sprites"]["sky"]["image"], (gameData["circle_hitbox"]["x_relative"]/100,0))
        gameData["window"].blit(gameData["sprites"]["sky"]["moon"], (gameData["circle_hitbox"]["x_relative"]/50, 0))
        gameData["window"].blit(gameData["sprites"]["backgroundFar"]["image"], (gameData["circle_hitbox"]["x_relative"]//30, 0))
        gameData["window"].blit(gameData["sprites"]["background"]["image"], (gameData["circle_hitbox"]["x_relative"]//10,0))
        gameData["window"].blit(gameData["sprites"]["ground"]["image"], (gameData["circle_hitbox"]["x_relative"],(gameData["terrain"]["location"][1]-84)))
        render_leader(gameData)
        if gameData["sprites"]["Characters"]["Leader"]["x_cord"] <=700:
                render_dialog(gameData)
        return

#This handles the rendering of the commander in level 1
def render_commander(gameData):
        
        gameData["sprites"]["Characters"]["commander"]["image"] = gameData["sprites"]["Characters"]["commander"]["sheet"][gameData["sprites"]["Characters"]["commander"]["counter"]//10]
        
        if gameData["sprites"]["Characters"]["commander"]["shot"] and gameData["sprites"]["Characters"]["commander"]["counter"] <140:
                
                gameData["sprites"]["Characters"]["commander"]["counter"]+=10

                if gameData["sprites"]["Characters"]["commander"]["counter"] ==30 or gameData["sprites"]["Characters"]["commander"]["counter"] ==60 or gameData["sprites"]["Characters"]["commander"]["counter"] ==100 or gameData["sprites"]["Characters"]["commander"]["counter"] ==140:
                       
                        gameData["sprites"]["Characters"]["commander"]["shot"] = False

        gameData["window"].blit(gameData["sprites"]["Characters"]["commander"]["image"], (gameData["sprites"]["Characters"]["commander"]["location"][0], gameData["sprites"]["Characters"]["commander"]["location"][1]+gameData["circle_hitbox"]["y_relative"]))
        '''
        gameData["sprites"]["Characters"]["commander"]["counter"] +=10
        if gameData["sprites"]["Characters"]["commander"]["counter"] >=150:
                gameData["sprites"]["Characters"]["commander"]["counter"] =0
        '''

#This handles the rendering of dialog
def render_dialog(gameData):
      
        if gameData["sprites"]["dialog"]["leader"]["counter"] <55*40:
                gameData["window"].blit(gameData["sprites"]["dialog"]["leader"]["image"][gameData["sprites"]["dialog"]["leader"]["counter"]//60], (500,0))
                gameData["sprites"]["dialog"]["leader"]["counter"] +=1

#This handles the rendering of time (that appears on the top right, on levels 3, 2)
def renderTime(gameData):
        time = ""
       
        if gameData["level"][2]["state"]:
                time = "TIME REMAINING: " + str(gameData["timer"]["time_left"])
        elif gameData["level"][3]["state"]:
                time = "TIME: " + str(gameData["timer"]["seconds"])

        font = pygame.font.SysFont('Times New Roman', 30, True)
        text = font.render(time, False, (255,255,255))
        x, y = text.get_size()
        
        gameData["window"].blit(text, (900-x,10))

#This handles the variables that don't need to be reset for every new level
def get_variables(gameData):
        
        gameData["level"] = {}
        
        gameData["level"][1] = {}
        gameData["level"][1]["state"] = True
        gameData["level"][2] = {}
        gameData["level"][2]["state"] = False
       
        gameData["level"][3] = {}
        gameData["level"][3]["state"] = False
       
        gameData["level"][4] = False
        gameData["level"][5] = False

        gameData["circle_hitbox"] = {}

        gameData["circle_hitbox"]["x_relative"] = 0

        return gameData

#This handles the variables that need to be reset every level. 
def init_data(gameData):
        gameData["new_game"] = False
        gameData["rotating_lines"] = []
        x_location = 1500
        for i in range (5):
                rotating_line = {}
                rotating_line["ori"] = (window_wid, 30)                 # the "origin" around which the line rotates 
                rotating_line["ang"] = 135                             # the current "angle" of the line
                rotating_line["len"] = [ (0.00, 0.42), (0.70, 1.00) ]  # the "length" intervals that specify the gap(s)
                rotating_line["seg"] = [ ]                             # the individual "segments" (i.e., non-gaps)
                rotating_line["velocity"] = 50
                rotating_line["location"] = x_location
                rotating_line["exists"] = True
                rotating_line["direction"] = "LEFT"
                x_location += 2000
                gameData["rotating_lines"].append(rotating_line)
        
        gameData["terrain"] = {}
        gameData["terrain"]["size"] = (3000, 200)
        gameData["terrain"]["color"] = (100,100,100)
        gameData["terrain"]["location"] = (0, window_hgt - 100)

        gameData["timer"] = {}
        gameData["timer"]["mili_seconds"] = 0
        gameData["timer"]["seconds"] = 0
        gameData["timer"]["time_left"] = 0

        gameData["circle_hitbox"]["rad"] = 64
        gameData["circle_hitbox"]["pos"] = (window_wid // 2, gameData["terrain"]["location"][1]-gameData["circle_hitbox"]["rad"])
        gameData["circle_hitbox"]["col"] = False
        gameData["circle_hitbox"]["direction"] = "None"
        gameData["circle_hitbox"]["jump"] = False
        gameData["circle_hitbox"]["Start_height"] = gameData["terrain"]["location"][1]
        gameData["circle_hitbox"]["jump_height"] = 0
        gameData["circle_hitbox"]["last_key"] = "RIGHT"
        gameData["circle_hitbox"]["Platform"] = "GROUND"
        gameData["circle_hitbox"]["fall"] = False
        gameData["circle_hitbox"]["y_relative"] = 0
        
        gameData["circle_hitbox"]["y_velocity"] = 0
        gameData["circle_hitbox"]["aim_gun"] = False
        gameData["circle_hitbox"]["shoot"] = False
        gameData["circle_hitbox"]["is_hit_counter"] = 0
        gameData["circle_hitbox"]["last_stand"] = False
        gameData["circle_hitbox"]["heartbeat"] = 0

        gameData["circle_hitbox"]["skip"] = False
        
        gameData["circle_hitbox"]["health"] = {}
        gameData["circle_hitbox"]["health"]["num"] = 2
        gameData["circle_hitbox"]["health"]["sheet"] = []
        gameData["circle_hitbox"]["health"]["counter"] = 0
        gameData["circle_hitbox"]["dead"] = False
        gameData["circle_hitbox"]["dead_counter"] = 0
        gameData["circle_hitbox"]["key"] = False
        gameData["circle_hitbox"]["key_counter"] = 0

        

        gameData["pause_on"] = False
        for i in range(5):
                gameData["circle_hitbox"]["health"]["sheet"].append(pygame.image.load("graphics/health/health" + str(i)+".png"))

        gameData["velocity"] = 40
        gameData["level"][3]["text"] = "SURVIVE"
        gameData["level"][1]["text"] = "REPORT TO COMMANDER"
        gameData["level"][2]["text"] = "ESCAPE"

        gameData["cannons"] = []
        for i in range(8):
                cannon = {}
                cannon["size"] =128, 64
                cannon["location"] = (-64, -i*400)
                cannon["sprite"] = pygame.image.load("graphics/cannon/cannon.png")
                alpha = cannon["sprite"].get_at((0,0))
                cannon["sprite"].set_colorkey(alpha)

                cannon["counter"] = 30
                cannon["shoot"] = True
                cannon["rocket"] = {}
                cannon["hit"] = False
                cannon["hitLocation"] = 0,0

                cannon["rocket"]["org_location"] = cannon["location"][0], cannon["location"][1]+18
                cannon["rocket"]["location"] = cannon["rocket"]["org_location"]
        
                cannon["rocket"]["sprite"] = pygame.image.load("graphics/cannon/rocket.png")
                alpha = cannon["rocket"]["sprite"].get_at((0,0))
                cannon["rocket"]["sprite"].set_colorkey(alpha)
                cannon["rocket"]["exists"] = False
                cannon["rocket"]["size"] =  cannon["rocket"]["sprite"].get_at((0,0))
                cannon["rocket"]["velocity"] = 70

                gameData["cannons"].append(cannon)
 
        explosion = {}
        explosion["sheet"] = get_sprite("graphics/cannon/explosion.png", 128, 4)
        explosion["counter"] = 0

        gameData["cannons"].append(explosion)

        airstrike = {}
        airstrike["crosshair"] = {}
        airstrike["hit_ground"] = False
        airstrike["hit"] = False
        airstrike["crosshair"]["exists"] = False
        airstrike["counter"] = 0
        airstrike["warning_counter"] = 0
        airstrike["crosshair"]["location"] = 0,0
        airstrike["crosshair"]["sprite"] = pygame.image.load("graphics/airstrike/crosshair.png")
        alpha = airstrike["crosshair"]["sprite"].get_at((0,0))
        airstrike["crosshair"]["sprite"].set_colorkey(alpha)
        airstrike["rocket"] = {}
        airstrike["rocket"]["org_location"] = cannon["location"][0], cannon["location"][1]+18
        airstrike["rocket"]["location"] = cannon["rocket"]["org_location"]
        airstrike["rocket"]["sprite"] = pygame.image.load("graphics/airstrike/rocket.png")
        alpha = airstrike["rocket"]["sprite"].get_at((0,0))
        airstrike["rocket"]["sprite"].set_colorkey(alpha)

        airstrike["rocket"]["exists"] = False
        airstrike["rocket"]["size"] =  cannon["rocket"]["sprite"].get_at((0,0))
        airstrike["rocket"]["velocity"] = 100
        gameData["cannons"].append(airstrike)

        gameData["sprites"]["background"] = {}
        gameData["sprites"]["background"]["image"] = pygame.image.load("graphics/Backgrounds/background.png")
        gameData["sprites"]["background"]["size"] = gameData["sprites"]["background"]["image"].get_rect().size
        alpha = gameData["sprites"]["background"]["image"].get_at((0,0))
        gameData["sprites"]["background"]["image"].set_colorkey(alpha)

        gameData["sprites"]["backgroundFar"] = {}
        gameData["sprites"]["backgroundFar"]["image"] = pygame.image.load("graphics/Backgrounds/backgroundFar.png")
        gameData["sprites"]["backgroundFar"]["size"] = gameData["sprites"]["backgroundFar"]["image"].get_rect().size
        alpha = gameData["sprites"]["backgroundFar"]["image"].get_at((0,0))
        gameData["sprites"]["backgroundFar"]["image"].set_colorkey(alpha)

        gameData["sprites"]["ending"] = pygame.image.load("graphics/Backgrounds/Ending.png")
        gameData["sprites"]["ending_counter"] = 0
        gameData["sprites"]["ending_fade"] = False
        gameData["sprites"]["ending_on"] = False
        gameData["sprites"]["ending_play_music"] = True

        gameData["sprites"]["sky"] = {}
        gameData["sprites"]["sky"]["image"] = pygame.image.load("graphics/Backgrounds/sky.png")
        gameData["sprites"]["sky"]["size"] = gameData["sprites"]["sky"]["image"].get_rect().size
        gameData["sprites"]["sky"]["moon"] = pygame.image.load("graphics/Backgrounds/Moon.png")
        gameData["sprites"]["sky"]["counter"] = 0
        alpha = gameData["sprites"]["sky"]["moon"].get_at((0,0))
        gameData["sprites"]["sky"]["moon"].set_colorkey(alpha)

        gameData["sprites"]["sign"] = {}
        gameData["sprites"]["sign"]["image"] = pygame.image.load("graphics/Foregrounds/sign.png")
        gameData["sprites"]["sign"]["size"] = gameData["sprites"]["backgroundFar"]["image"].get_rect().size
        alpha =  gameData["sprites"]["sign"]["image"].get_at((0,0))
        gameData["sprites"]["sign"]["image"].set_colorkey(alpha)

        
        gameData["sprites"]["player"]["sheet_hit"] = get_sprite("graphics/characters/player_sprite_hit.png", 128, 18)
        gameData["sprites"]["player"]["sheet"] =  gameData["sprites"]["player"]["sheet_org"]
        gameData["sprites"]["player"]["counter"] = 0
        gameData["sprites"]["player"]["JUMP_UP"] = False
        gameData["sprites"]["player"]["JUMP_DOWN"] = False
        gameData["circle_hitbox"]["last_stand_counter"] = 0

        gameData["sprites"]["Characters"] = {}

        gameData["sprites"]["Characters"]["Target"] = {}
        gameData["sprites"]["Characters"]["Leader"] = {}
        gameData["sprites"]["Characters"]["Leader"]["sheet"] =  get_sprite("graphics/characters/leader/leader.png", 128, 7)
        gameData["sprites"]["Characters"]["Leader"]["counter"] = 0
        gameData["sprites"]["Characters"]["Leader"]["x_cord"] = window_wid
        gameData["sprites"]["Characters"]["Leader"]["direction"] = "LEFT"

        gameData["sprites"]["Characters"]["commander"] = {}
        gameData["sprites"]["Characters"]["commander"]["sheet"] = get_sprite("graphics/characters/Commander/commander_sprite.png", 128, 15)
        gameData["sprites"]["Characters"]["commander"]["counter"] = 0
        gameData["sprites"]["Characters"]["commander"]["location"] = (500, -3070)
      
        gameData["sprites"]["Characters"]["commander"]["shot"] = False
        gameData["sprites"]["Characters"]["commander"]["dead"] = False
        
        
        gameData["sprites"]["ground"] = {}
        gameData["sprites"]["ground"]["image"] = pygame.image.load("graphics/Foregrounds/ground2.png")
        
        gameData["sprites"]["gameOver"] = {}
        gameData["sprites"]["gameOver"]["image"] = pygame.image.load("graphics/GameOver/GameOver.png").convert()
        gameData["sprites"]["gameOver"]["size"] = gameData["sprites"]["gameOver"]["image"].get_rect().size
        gameData["sprites"]["gameOver"]["counter"] = 0
        gameData["sprites"]["gameOver"]["background"] = {}
        gameData["sprites"]["gameOver"]["background"]["image"] = pygame.image.load("graphics/GameOver/black.png").convert()
        
        gameData["sprites"]["building"] = {}
        gameData["sprites"]["building"]["image"] = {}
        gameData["sprites"]["building"]["image"]["blue"] = pygame.image.load("graphics/Foregrounds/startingBuilding1.png")
        gameData["sprites"]["building"]["image"]["red"] = pygame.image.load("graphics/Foregrounds/startingBuilding2.png")

        gameData["sprites"]["chest"] = {}
        gameData["sprites"]["chest"]["sheet"] = get_sprite("graphics/chest/chest.png", 32, 2)
        gameData["sprites"]["chest"]["open"] = False
        gameData["sprites"]["chest"]["image"] =  gameData["sprites"]["chest"]["sheet"][0]
        
        gameData["sprites"]["gate"] = {}
        gameData["sprites"]["gate"]["counter"] = 0
        gameData["sprites"]["gate"]["health"] = 3
        gameData["sprites"]["gate"]["spriteA"] = []
        gameData["sprites"]["gate"]["spriteB"] = []
        gameData["sprites"]["gate"]["isHit"] = False
        gameData["sprites"]["gate"]["opened"] = False
        
        for i in range(4):
                imageA =  pygame.image.load("graphics/gate/gate"+str(i)+".png")
                imageB =  pygame.image.load("graphics/gate/gateB"+str(i)+".png")

                gameData["sprites"]["gate"]["spriteA"].append(imageA)
                gameData["sprites"]["gate"]["spriteB"].append(imageB)

        gameData["sprites"]["Pause"] = {}
        gameData["sprites"]["Pause"]["image"] = []
        gameData["sprites"]["gate"]["img"] = gameData["sprites"]["gate"]["spriteA"][0]
        for i in range(3):
                image = pygame.image.load("graphics/Pause/Pause"+str(i)+".png")
                alpha = image.get_at((0,0))
                image.set_colorkey(alpha)
                gameData["sprites"]["Pause"]["image"].append(image)
        gameData["sprites"]["Pause"]["image"].append(pygame.image.load("graphics/menus/Controls.png"))

        gameData["sprites"]["tower"] = pygame.image.load("graphics/Foregrounds/tower.png")
        alpha =  gameData["sprites"]["tower"].get_at((0,0))
        gameData["sprites"]["tower"].set_colorkey(alpha)


        gameData["sprites"]["laser"] = {}
        gameData["sprites"]["laser"]["image"] = pygame.image.load("graphics/laser/laser.png")
        alpha = gameData["sprites"]["laser"]["image"].get_at((0,0))
        gameData["sprites"]["laser"]["image"].set_colorkey(alpha)
        gameData["sprites"]["laser"]["size"] = gameData["sprites"]["laser"]["image"].get_rect().size

        gameData["sprites"]["level1"] = {}
        gameData["sprites"]["level1"]["image"] = pygame.image.load("graphics/Foregrounds/level1.png")
        alpha = gameData["sprites"]["level1"]["image"].get_at((0,0))
        gameData["sprites"]["level1"]["image"].set_colorkey(alpha)
        gameData["sprites"]["level1"]["size"] = gameData["sprites"]["laser"]["image"].get_rect().size

        gameData["sprites"]["fade_out"] = 0

        gameData["menu_options"] = {}
        gameData["menu_options"]["NEW"] = True
        gameData["menu_options"]["RESUME"] = False
        gameData["menu_options"]["CONTROLS"] = False
        gameData["menu_options"]["CONTROL_WINDOW"] = False
        gameData["menu_options"]["counter"] = 0

        gameData["sprites"]["Menu"]= {}
        gameData["sprites"]["Menu"]["image"] = []
        for i in range(3):
                
                gameData["sprites"]["Menu"]["image"].append( pygame.image.load("graphics/menus/Title_"+ str(i)+ ".png") )
        
        gameData["sprites"]["Menu"]["image"].append( pygame.image.load("graphics/menus/Controls.png") )

        gameData["sprites"]["Title"]= {}
        gameData["sprites"]["Title"]["image"] = pygame.image.load("graphics/Title/TitleText.png")

        gameData["sprites"]["dialog"] = {}
        gameData["sprites"]["dialog"]["leader"] = {}
        gameData["sprites"]["dialog"]["leader"]["counter"] = 0
        gameData["sprites"]["dialog"]["leader"]["image"] = []

        for i in range(55):
                image = pygame.image.load("graphics/chat/leaderDialog/Leader"+str(i)+".png")
                gameData["sprites"]["dialog"]["leader"]["image"].append(image)
        
        gameData["sprites"]["dialog"]["commander"] = {}
        gameData["sprites"]["dialog"]["commander"]["counter"] = 0
        gameData["sprites"]["dialog"]["commander"]["image"] = []

        for i in range(55):
                image = pygame.image.load("graphics/chat/commanderDialog/commander"+str(i)+".png")
                gameData["sprites"]["dialog"]["commander"]["image"].append(image)
        
        
        gameData["level"]["complete"] = {}
        gameData["level"]["complete"]["font"] = pygame.font.SysFont('Times New Roman', 30, True)
        gameData["level"]["complete"]["text"] =  gameData["level"]["complete"]["font"].render("OBJECTIVE: COMPLETE", False, (0,160,255))
        gameData["level"]["complete"]["counter"] = 0
        gameData["level"]["newObjective"] = {}
        gameData["level"]["newObjective"]["counter"] = 0


        gameData["level_counter"] = 0

        gameData["platforms"] = []
        platform_file = readCSV("Save/level1.csv", False)
        
        for i in range(50):
      
                platform = {}
                platform["size"] = 100, 50
                platform["color"] = (255, 255, 255)
                platform["location"] = int(platform_file[i][0]), int(platform_file[i][1])

                platform["num"] = (i+1)
                
                platform["image_exists"] = True
                platform["image"] = pygame.image.load("graphics/platforms/platform.png")
                platform["org"] =  platform["location"]
                gameData["platforms"].append(platform)
        
        gameData["platforms"][49]["location"] = (159, -2941)
        gameData["platforms"][49]["image_exists"] = False
        gameData["platforms"][49]["size"] = (1000, 25)

        gameData["building_counter"] = 0


        return gameData

def main():
        
        # initialize pygames
        pygame.init()

        # this is the initial game state

        gameData = {}
        gameData["clock"] = pygame.time.Clock()
        gameData["window"] = pygame.display.set_mode( (window_wid, window_hgt) )
        pygame.display.set_caption("ROGUE ORDER")

        gameData["new_level"] = True
        gameData["new_game"] = True
        gameData["music_on"] = False
        
        gameData["state"] = {}
        gameData["state"]["MENU"] = True
        gameData["state"]["TITLE"] = False
        gameData["state"]["GAME"] = False
        gameData["state"]["GAMEOVER"] = False
        gameData["state"]["PAUSE"] = False
        gameData["OPACITY_SET"] = False
        
        ticks =pygame.time.get_ticks()
        gameData["platforms"] = {}
       
        gameData["scroll"] = 0
        gameData["sprites"] = {}
        gameData["sprites"]["player"] = {}
        gameData["sprites"]["player"]["sheet_org"] = get_sprite("graphics/characters/player_sprite1.png", 128, 18)

        gameData["sprites_num"] = 1

        gameData["circle_hitbox"] = {}
        gameData["level"] = {}

        gameData= get_variables(gameData)
        
        gameData["circle_hitbox"]["x_relative"] = 0
        while True:

                if not (gameData["state"]["GAMEOVER"] or gameData["state"]["PAUSE"]):
                        gameData["window"].fill( (0,0,0) )

                gameData = game_loop_inputs(gameData)
                gameData["save_data"] = load_text("Save/Save.txt")

                if gameData["new_game"]:
                        game_data = init_data(gameData)  

                gameData = game_loop_update(gameData) 
                if not gameData["state"]["GAMEOVER"]:
                        game_loop_render(gameData)

                pygame.display.flip()
                pygame.display.update()
                gameData["clock"].tick(frame_rate)
                      
if __name__ == "__main__":
        main()
