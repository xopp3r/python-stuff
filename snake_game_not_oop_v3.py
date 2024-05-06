import pygame as pg
import random

CHEATS = True #allows you to grow by 'q' and suicide by 'tab'
SIZEOFMAP = 5 #
RESOLUTION = 160 # 120: 1080p / 160: 1440p
FPS = 15 
SIZEOFTILE = RESOLUTION//SIZEOFMAP
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREY = (20,20,20)
TTL_TEXT_CLR = (231, 111, 81)
MAIN_TEXT_CLR = (131, 211, 81)
SEC_TEXT_CLR = (112, 58, 58)


class save_file:
    def __init__(self,file):
        self.file = open(file,'a+')
    def get_best_score(self):
        maxs = 0
        self.file.seek(0)
        for lines in self.file.readlines():
            maxs = max(maxs,int(lines))
        return maxs
    def max_score(self, current_score):
        global maxscore 
        self.file.write(str(current_score)+'\n')
        maxscore = max(current_score,maxscore)
        return maxscore
    def close(self):
        self.file.close()

class entity:
    def __init__(self, color = WHITE):
        self.element = pg.Surface((SIZEOFTILE,SIZEOFTILE))
        self.element.fill(color)
    def change_color(self,color):
        self.element.fill(color)
    def set_position(self, tile: list[int]):
        self.position = [tile]

class snake(entity):
    def __init__(self, color):
        super().__init__(color)
        self.position = []
    def move(self):
        if len(self.position) > 1:
            for current_element in range(len(self.position)-1,0,-1):
                self.position[current_element] = self.position[current_element-1][:]
        match self.direction:
            case 0: self.position[0][0] += 1
            case 1: self.position[0][1] += 1
            case 2: self.position[0][0] += -1
            case 3: self.position[0][1] += -1
        self.position[0][0],self.position[0][1] = self.position[0][0]%(SIZEOFMAP*16),self.position[0][1]%(SIZEOFMAP*9)
    def grow(self):
        self.position.append([-1,-1])
    def turn(self,new_direction):
        if (self.direction - new_direction) % 2 != 0: # проверка на то, что не движется в противоположную сторону
            self.direction = new_direction
    def tile_check(self,food):
        if self.position[0] in self.position[1:]: 
            Game.get_ready_to_game()
        if self.position[0] in food.position: 
            self.grow()
            food.remove(self.position[0])
            food.add(1)
    def set_direction(self,direction):
        self.direction = direction
    def get_score(self): return len(self.position) - 1 if self.position else 0


class food(entity):
    def __init__(self, color):
        super().__init__(color)
    def add(self, amount): 
        for _ in range(amount):
            self.position.append(rand_tile())
    def remove(self, tile):
        self.position.remove(tile)
    

class game:
    def __init__(self, snake, food):
        self.snake = snake
        self.food = food
    def get_ready_to_game(self):
        self.running = False
        print(self.snake.get_score(), 'is your score') # переделать
        self.snake.set_position(rand_tile())
        self.snake.set_direction(round(random.random()*3))       
        self.food.set_position(rand_tile())
        screen.blit(title_text.text, (RESOLUTION*3,RESOLUTION*3))
        screen.blit(start_text.text, (RESOLUTION*3,RESOLUTION*3 + RESOLUTION*1.5))
        maxscore_text.change_text('Max score: ' + str(save.max_score(self.snake.get_score())))
        screen.blit(maxscore_text.text, (180,10))
        pg.display.update()
    def render(self):
        game.backgroung()
        for object in [self.snake, self.food]:
            for current_element in object.position:
                screen.blit(object.element, (current_element[0]*SIZEOFTILE, current_element[1]*SIZEOFTILE))  
        score_text.change_text('Score: ' + str(self.snake.get_score()))
        screen.blit(score_text.text, (10,10))
        pg.display.flip()
    def backgroung():
        screen.fill(BLACK)
        for x in range(SIZEOFMAP*16+1):
            pg.draw.line(screen, GREY ,[x*SIZEOFTILE,0], [x*SIZEOFTILE,RESOLUTION*9], 1)
        for y in range(SIZEOFMAP*9+1):
            pg.draw.line(screen, GREY ,[0,y*SIZEOFTILE], [RESOLUTION*16,y*SIZEOFTILE], 1)


class text:
    def __init__(self,size = 5, color = WHITE ,text = 'test-text'):
        self.color = color
        self.font = pg.font.Font(None, ((RESOLUTION*16)//100)*size, )
        self.text = self.font.render(text, True, color)
    def change_text(self, text):
        self.text = text
        self.text = self.font.render(text, True, self.color)

def rand_tile(padding = 3):
    return [padding + round(random.random()*(SIZEOFMAP*16-(2*padding))), 
            padding + round(random.random()*(SIZEOFMAP*9-(2*padding)))]

def buttons_check(game: game, snake: snake):
    global exited

    switch_snake_direction_to = -1
    for event in pg.event.get():
        if event.type == pg.QUIT: pg.quit()
        if event.type == pg.KEYDOWN:
            match event.key:
                case pg.K_ESCAPE: exited = True
                case pg.K_w: switch_snake_direction_to = 3
                case pg.K_d: switch_snake_direction_to = 0
                case pg.K_s: switch_snake_direction_to = 1
                case pg.K_a: switch_snake_direction_to = 2
                case pg.K_q : 
                    if CHEATS: game.snake.grow() # можно?
                case pg.K_TAB : 
                    if CHEATS: game.get_ready_to_game()
    if switch_snake_direction_to != -1: snake.turn(switch_snake_direction_to)





pg.init()
pg.font.init()
save = save_file('results.txt')
title_text = text(10,TTL_TEXT_CLR,'The snake game')
start_text = text(5, MAIN_TEXT_CLR, 'Press any key to start')
score_text = text(2, MAIN_TEXT_CLR, '')
maxscore_text = text(2, MAIN_TEXT_CLR, '')
screen = pg.display.set_mode((RESOLUTION*16,RESOLUTION*9))
pg.display.set_caption('The snake game v.3')
clock = pg.time.Clock()
exited = False
maxscore = save.get_best_score()

Snake1 = snake(WHITE)
Food = food(RED)
File = save_file('results.txt')
Game = game(Snake1,Food)

Game.get_ready_to_game()
while not exited:
    while not Game.running and not exited:
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: exited = True
            if event.type == pg.KEYDOWN: Game.running = True
        clock.tick(FPS)

    while Game.running and not exited:
        buttons_check(Game, Snake1)
        Snake1.move()
        Snake1.tile_check(Food)
        if Game.running: Game.render()
        clock.tick(FPS)

File.close()
pg.quit()
