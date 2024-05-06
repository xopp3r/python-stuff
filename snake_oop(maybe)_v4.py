import pygame as pg
import random

CHEATS = True #allows you to grow by 'q' and suicide by 'tab'
SIZEOFMAP = 5 #
RESOLUTION = 160 # 120: 1080p / 160: 1440p
FPS = 15
SIZEOFTILE = RESOLUTION//SIZEOFMAP
SF = (RESOLUTION*9)//100 # scale factor [% of screen height]
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREY = (20,20,20)
TTL_TEXT_CLR = (231, 111, 81)
MAIN_TEXT_CLR = (131, 211, 81)
SEC_TEXT_CLR = (112, 58, 58)


class SaveFile:
    def __init__(self, file):
        self.file = open(file, 'a+')
    def get_best_score(self):
        self.file.seek(0)
        maxscr = 0
        for line in self.file.readlines():
            maxscr = max(maxscr, int(line))
        return maxscr
    def try_set_max_score(self, current_score):
        global maxscore 
        self.file.write(str(current_score) + '\n')
        maxscore = max(current_score, maxscore)
    def close(self):
        self.file.close()


class Entity:
    def __init__(self, color, position) -> None:
        self.color = color
        self.position = [position]
        self.tile = pg.Surface((SIZEOFTILE,SIZEOFTILE))
        self.tile.fill(color)
    def get_position(self):
        return self.position
    def get_color(self):
        return self.color
    def get_tile(self):
        return self.tile


class Snake(Entity):
    def __init__(self, color, position, direction) -> None:
        super().__init__(color, position)
        self.direction = direction
        self.alive = True
    def move(self):
        if len(self.position) > 1:
            for current_element in range(len(self.position)-1,0,-1):
                self.position[current_element] = self.position[current_element-1][:]
        match self.direction:
            case 1: self.position[0][0] += 1
            case 2: self.position[0][1] += 1
            case 3: self.position[0][0] += -1
            case 4: self.position[0][1] += -1
        self.position[0][0] = self.position[0][0]%(SIZEOFMAP*16)
        self.position[0][1] = self.position[0][1]%(SIZEOFMAP*9)
    def turn(self, new_direction):
        if (self.direction - new_direction) % 2 != 0:
            self.direction = new_direction
    def check_collision(self, entities):
        head_tile = self.position[0]
        entities.remove(self)
        if head_tile in self.get_position()[1:]:
            self.die()
        for entity in entities:
            if head_tile in entity.get_position(): 
                entity.on_collision(self)
    def on_collision(attaker: Entity):
        attaker.die()
    def die(self):
        self.alive = False
    def grow(self):
        self.position.append([-1,-1])
    def get_score(self):
        return len(self.position) - 1


class Food(Entity):
    def __init__(self, color, position) -> None:
        super().__init__(color, position)
    def on_collision(self, attaker):
        attaker.grow()
        self.position.remove(attaker.get_position()[0])
        self.add_position(rand_tile())
    def add_position(self, tile):
        self.position.append(tile)


class Text:
    def __init__(self, size = 5, color = WHITE ,text = 'test-text') -> None:
        self.color = color
        self.font = pg.font.Font(None, SF*size)
        self.text = self.font.render(text, True, self.color)
    def change_text(self, text):
        self.text = self.font.render(text, True, self.color)



class UI:
    def __init__(self) -> None:
        self.title_text = Text(20,TTL_TEXT_CLR,'The snake game')
        self.start_text = Text(10, MAIN_TEXT_CLR, 'Press any key to start')
        self.score_text = Text(4, MAIN_TEXT_CLR)
        self.maxscore_text = Text(4, MAIN_TEXT_CLR)
    def update_score(self, new_score):
        self.score_text.change_text('Score: ' + str(new_score))
    def update_max_score(self, new_max_score):
        save.try_set_max_score(new_max_score)
        self.maxscore_text.change_text('Max score: ' + str(maxscore))
        

class Render:
    def __init__(self, game) -> None:
        self.game = game
        self.ui = game.ui
    def render(self):
        self.background()
        for object in self.game.get_objects_for_render():
            for current_element in object.get_position():
                screen.blit(object.get_tile(), (current_element[0]*SIZEOFTILE, current_element[1]*SIZEOFTILE))  
        self.render_ui()
        pg.display.flip() 
 

    def render_ui(self):
        self.ui.update_score(self.game.snakes[0].get_score())
        screen.blit(self.ui.score_text.text, (10,10))

    def show_start_screen(self):
        self.ui.update_max_score(self.game.snakes[0].get_score())
        screen.blit(self.ui.maxscore_text.text, (240,10))
        screen.blit(self.ui.title_text.text, (RESOLUTION*3,RESOLUTION*3))
        screen.blit(self.ui.start_text.text, (RESOLUTION*3,RESOLUTION*3 + RESOLUTION*1.5))
        pg.display.flip() 

    def background(self):
        screen.fill(BLACK)
        for x in range(SIZEOFMAP*16+1):
            pg.draw.line(screen, GREY ,[x*SIZEOFTILE,0], [x*SIZEOFTILE,RESOLUTION*9], 1)
        for y in range(SIZEOFMAP*9+1):
            pg.draw.line(screen, GREY ,[0,y*SIZEOFTILE], [RESOLUTION*16,y*SIZEOFTILE], 1)



class Game:
    def __init__(self) -> None:
        self.snakes = [ Snake( WHITE, rand_tile(), 1+round( 3*random.random() ) ) ]
        self.food = Food(RED, rand_tile())
        self.ui = UI()
        self.render = Render(self)
        self.running = False
        self.exited = False

    def check_input(self): # исправить в будущем
        switch_snake_direction_to = 0
        for event in pg.event.get():
            if event.type == pg.QUIT: pg.quit()
            if event.type == pg.KEYDOWN:
                match event.key:
                    case pg.K_ESCAPE: pg.quit()
                    case pg.K_w: switch_snake_direction_to = 4
                    case pg.K_d: switch_snake_direction_to = 1
                    case pg.K_s: switch_snake_direction_to = 2
                    case pg.K_a: switch_snake_direction_to = 3
                    case pg.K_q : 
                        if CHEATS: self.snakes[0].grow() 
                    case pg.K_TAB : 
                        if CHEATS: self.game_over()
        if switch_snake_direction_to != 0: self.snakes[0].turn(switch_snake_direction_to)

    def run(self):
            while self.running and not self.exited:
                self.check_input()
                self.next_frame()
                self.render.render()
                clock.tick(FPS)

    def start_screen(self):
        while not self.running and not self.exited:
            self.render.show_start_screen()
            for event in pg.event.get():
                if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    self.running = True
            clock.tick(FPS)

    def play(self):
        self.start_screen()
        self.run()

    def game_over(self):
        self.ui.update_max_score(self.snakes[0].get_score())
        self.running = False
        del self

    def get_objects_for_render(self):
        return [self.food] + self.snakes
    def next_frame(self):
        for snake in self.snakes:
            snake.move()
            snake.check_collision([self.food] + self.snakes)
            if not snake.alive: self.game_over()



def rand_tile(padding = 3):
    return [padding + round(random.random()*(SIZEOFMAP*16-(2*padding))), 
            padding + round(random.random()*(SIZEOFMAP*9-(2*padding)))]








pg.init()
pg.font.init()
pg.display.set_caption('The snake game v.3')
screen = pg.display.set_mode((RESOLUTION*16,RESOLUTION*9))
save = SaveFile('results.txt')
clock = pg.time.Clock()

maxscore = save.get_best_score()


while True:
    game = Game()
    game.play()
