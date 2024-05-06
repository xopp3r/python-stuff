import pygame as pg
import random
from abc import abstractmethod

DEBUG_MODE = True # allows you to grow by 'q' and suicide by 'tab'
SIZEOFMAP = 5 
RESOLUTION = 120 # 120: 1080p / 160: 1440p
FPS = 15
SIZEOFTILE = RESOLUTION//SIZEOFMAP
SF = (RESOLUTION*9)//100 # scale factor [1% of screen height in px]
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

    def pull_best_score(self):
        self.file.seek(0)
        self.maxscore = 0
        for line in self.file.readlines():
            self.maxscore = max(self.maxscore, int(line))
        return self.maxscore
    
    def check_for_record(self, current_score):
        self.file.write(str(current_score) + '\n')
        maxscore = max(current_score, maxscore)

    def close_file(self):
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
        self.dead = False

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
    '''
    def check_collision(self, entities):
        head_tile = self.position[0]
        entities.remove(self)
        if head_tile in self.get_position()[1:]:
            self.die()
        for entity in entities:
            if head_tile in entity.get_position(): 
                entity.on_collision(self)
    '''
    def on_collision(attaker: Entity):
        attaker.die()

    def die(self):
        self.dead = False

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
    def __init__(self, size = 5, color = WHITE, text = 'placeholder') -> None:
        self.color = color
        self.font = pg.font.Font(None, SF*size)
        self.text = self.font.render(text, True, self.color)

    def change_text(self, text):
        self.text = self.font.render(text, True, self.color)


class PageManager: # page conrtol
    def __init__(self, start_page) -> None:
        self.current_page = start_page
        self.previous_page = start_page

    def switch_to(self, page = None):
        if page == None: raise Exception('Invalid page given')
        self.previous_page = self.current_page
        self.current_page = page
        page.run()

    def switch_to_previous(self):
        self.switch_to(self.previous_page)

    def start(self):
        self.current_page.run()


class Page: # parent class for pages
    def __init__(self) -> None:
        pass

    def check_input(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE: pg.quit()
                elif event.key == pg.K_TAB: pageManager.switch_to_previous()
                else: self.handle_input(event.key)

    def run(self): 
        while pageManager.current_page == self:
            self.check_input() # buttons
            self.process_logic() # logic
            self.render_page() # render
            clock.tick(FPS)

    def process_logic(self): pass # no default logic

    def handle_input(self): raise Exception('handle_input() method not implemented in a subclass') # additional buttons actions
    
    def render_page(self): raise Exception('render_page() method not implemented in a subclass')


class TitlePage(Page):
    def __init__(self) -> None:
        self.title_text = Text(20, TTL_TEXT_CLR,'The snake game v.5')
        self.start_text = Text(10, MAIN_TEXT_CLR, 'Press A key to start')
        self.settings_text = Text(10, MAIN_TEXT_CLR, 'Press D key to go to settings')


    def handle_input(self, button):
        match button:
            case pg.K_a: pageManager.switch_to(gameModePage)
            case pg.K_d: pageManager.switch_to(settingsPage)

    def render_page(self):
        screen.fill(BLACK)
        screen.blit(self.title_text.text, (200, 300))
        screen.blit(self.start_text.text, (200, 500))
        screen.blit(self.settings_text.text, (200, 600))
        pg.display.flip()



class GameModePage(Page):
    def __init__(self) -> None:
        self.title_text = Text(20, TTL_TEXT_CLR,'Choose gamemode')
        self.singleplayer_text = Text(10, MAIN_TEXT_CLR, 'Press A key for multiplayer')
        self.multiplayer_text = Text(10, MAIN_TEXT_CLR, 'Press D key for singleplayer')
        self.go_back_text = Text(5, MAIN_TEXT_CLR, 'Press Q key to go back')

    def handle_input(self, button):
        match button:
            case pg.K_q: pageManager.switch_to(titlePage)
            case pg.K_a: pageManager.switch_to(multiplayerTypePage)
            case pg.K_d: pageManager.switch_to(singleplayerPage)

    def render_page(self):
        screen.fill(BLACK)
        screen.blit(self.title_text.text, (200, 300))
        screen.blit(self.singleplayer_text.text, (200, 500))
        screen.blit(self.multiplayer_text.text, (200, 600))
        screen.blit(self.go_back_text.text, (200, 700))
        pg.display.flip()


class SettingsPage(Page):
    def __init__(self) -> None:
        self.title_text = Text(20, TTL_TEXT_CLR,'Settings')
        self.placeholder_text = Text(10, MAIN_TEXT_CLR, 'WIP')
        self.go_back_text = Text(5, MAIN_TEXT_CLR, 'Press Q key to go back')

    def handle_input(self, button):
        match button:
            case pg.K_q: pageManager.switch_to(titlePage)


    def render_page(self):
        screen.fill(BLACK)
        screen.blit(self.title_text.text, (200, 300))
        screen.blit(self.placeholder_text.text, (200, 500))
        screen.blit(self.go_back_text.text, (200, 600))
        pg.display.flip()


class MultiplayerTypePage(Page):
    def __init__(self) -> None:
        self.title_text = Text(20, TTL_TEXT_CLR,'Choose multiplayer type')
        self.localMultiplayer_text = Text(10, MAIN_TEXT_CLR, 'Press A key for local multiplayer')
        self.onlineMultiplayer_text = Text(10, MAIN_TEXT_CLR, 'Press D key for online multiplayer')
        self.go_back_text = Text(5, MAIN_TEXT_CLR, 'Press Q key to go back')

    def handle_input(self, button):
        match button:
            case pg.K_q: pageManager.switch_to(gameModePage)
            case pg.K_a: pageManager.switch_to(localMultiplayerPage)
            case pg.K_d: pageManager.switch_to(onlineMultiplayerPage)

    def render_page(self):
        screen.fill(BLACK)
        screen.blit(self.title_text.text, (200, 300))
        screen.blit(self.localMultiplayer_text.text, (200, 500))
        screen.blit(self.onlineMultiplayer_text.text, (200, 600))
        screen.blit(self.go_back_text.text, (200, 700))
        pg.display.flip()




class GamePage(Page): pass
class LocalMultiplayerPage(Page): pass
class OnlineMultiplayerPage(Page): pass
class SingleplayerPage(Page): pass



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


class Game: # legacy
    def __init__(self) -> None:
        self.snakes = [ Snake( WHITE, rand_tile(), 1+round( 3*random.random() ) ) ]
        self.food = Food(RED, rand_tile())
        self.ui = UI()
        self.render = Render(self)
        self.running = False
        self.exited = False

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
pg.display.set_caption('The snake game v.5')
screen = pg.display.set_mode((RESOLUTION*16,RESOLUTION*9))
save = SaveFile('results.txt')
clock = pg.time.Clock()

titlePage = TitlePage()
pageManager = PageManager(titlePage)
settingsPage = SettingsPage()
gameModePage = GameModePage()
gamePage = GamePage()
multiplayerTypePage = MultiplayerTypePage()
singleplayerPageingleplayerPage = SingleplayerPage()
singleplayerPage = SingleplayerPage()
localMultiplayerPage = LocalMultiplayerPage()
onlineMultiplayerPage = OnlineMultiplayerPage()



pageManager.start()
