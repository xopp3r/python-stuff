import pygame as pg
import random

CHEATS = True #allows you to grow by 'q' and suicide by 'tab'
SIZEOFMAP = 5 #
RESOLUTION = 160 # 120: 1080p / 160: 1440p
FPS = 15 
SIZEOFSNAKEELEMENT = RESOLUTION//SIZEOFMAP
WHITE = (255,255,255)
BLACK = (0,0,0)

def start_game():
    global fps
    global score
    global running
    global snake_position 
    global snake_direction
    global food_position
    fps = FPS 
    running = False
    food_position = []
    snake_position = [rand_tile()]
    snake_direction = round(random.random()*3)    
    score_text = main_font.render('Score: ' + str(score), True, (112, 58, 58))
    screen.blit(score_text, (10,10))
    maxscore_text = main_font.render('Max score: ' + str(previous_results.max_score(score)), True, (112, 58, 58))
    screen.blit(maxscore_text, (10,10 + RESOLUTION//3))
    score = 0
    screen.blit(title_text, (RESOLUTION*3,RESOLUTION*3))
    screen.blit(start_text, (RESOLUTION*3,RESOLUTION*3 + RESOLUTION*1.5))
    food_position = add_food(food_position, 1)
    pg.display.update()

def rand_tile():
    return [2+round(random.random()*(SIZEOFMAP*16-4)),2+round(random.random()*(SIZEOFMAP*9-4))]

def add_food(food_position, a): 
    for _ in range(a):
        food_position.append(rand_tile())
    return food_position

def grow(snake_position):
    global score
    score += 1
    snake_position.append([-1,-1])
    return snake_position

def render():
    screen.fill(BLACK)
    for se in snake_position:
        screen.blit(snake_element, (se[0]*SIZEOFSNAKEELEMENT,se[1]*SIZEOFSNAKEELEMENT))  
    for fe in food_position:
        screen.blit(food_element, (fe[0]*SIZEOFSNAKEELEMENT,fe[1]*SIZEOFSNAKEELEMENT))  
    score_text = main_font.render('Score: ' + str(score), True, (112, 58, 58))
    screen.blit(score_text, (10,10))
    pg.display.flip()

def tile_check():
    global food_position
    global snake_position
    if snake_position[0] in snake_position[1:]: start_game()
    elif snake_position[0] in food_position: 
        snake_position = grow(snake_position)
        food_position.remove(snake_position[0])
        food_position = add_food(food_position, 1)

def buttons_check():
    global snake_position
    global snake_direction
    global fps
    global exited
    switch_snake_direction_to = snake_direction
    for event in pg.event.get():
        if event.type == pg.QUIT:
                pg.quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE: exited = True
            if event.key == pg.K_w: switch_snake_direction_to = 3
            if event.key == pg.K_d: switch_snake_direction_to = 0
            if event.key == pg.K_s: switch_snake_direction_to = 1
            if event.key == pg.K_a: switch_snake_direction_to = 2
            if event.key == pg.K_LSHIFT: fps = 2*FPS
            if event.key == pg.K_q and CHEATS: snake_position = grow(snake_position)
            if event.key == pg.K_TAB and CHEATS: start_game()
        if event.type == pg.KEYUP and event.key == pg.K_LSHIFT: fps = FPS
    if snake_direction != switch_snake_direction_to and (snake_direction - switch_snake_direction_to)%2 != 0:
        snake_direction = switch_snake_direction_to

def move_snake():
    global snake_position
    if len(snake_position) > 1:
        for current_element in range(len(snake_position)-1,0,-1):
            snake_position[current_element] = snake_position[current_element-1][:]
    match snake_direction:
        case 0: snake_position[0][0] += 1
        case 1: snake_position[0][1] += 1
        case 2: snake_position[0][0] += -1
        case 3: snake_position[0][1] += -1
    snake_position[0][0],snake_position[0][1] = snake_position[0][0]%(SIZEOFMAP*16),snake_position[0][1]%(SIZEOFMAP*9)

class previous_results:
    def get_best_score():
        maxs = 0
        file.seek(0)
        for lines in file.readlines():
            maxs = max(maxs,int(lines))
        return maxs
    def max_score(current_score):
        global maxscore 
        file.write(str(current_score)+'\n')
        maxscore = max(current_score,maxscore)
        return maxscore

pg.init()
pg.font.init()
file = open('results.txt','a+')
title_font = pg.font.Font(None, RESOLUTION*2)
main_font = pg.font.Font(None, RESOLUTION//2)
title_text = title_font.render('The snake game', True,(231, 111, 81))
start_text = main_font.render('Press any key to start', True,(131, 211, 81))
screen = pg.display.set_mode((RESOLUTION*16,RESOLUTION*9))
pg.display.set_caption('The snake game v.2')
clock = pg.time.Clock()
snake_element = pg.Surface((SIZEOFSNAKEELEMENT,SIZEOFSNAKEELEMENT))
snake_element.fill(WHITE)
food_element = pg.Surface((SIZEOFSNAKEELEMENT,SIZEOFSNAKEELEMENT))
food_element.fill((255,0,0))
score = 0
exited = False
maxscore = previous_results.get_best_score()

start_game()
while not exited:
    while not running and not exited:
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: exited = True
            if event.type == pg.KEYDOWN: running = True
        clock.tick(FPS)
        
    while running and not exited:
        buttons_check()
        move_snake()
        tile_check()
        if running: render()
        clock.tick(fps)

file.close()
pg.quit()
