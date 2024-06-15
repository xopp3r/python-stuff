import pygame as pg
import random
import json


WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREY = (20,20,20)
LIGHT_GREY = (150, 150, 150)
TTL_TEXT_CLR = (231, 111, 81)
MAIN_TEXT_CLR = (131, 211, 81)
SEC_TEXT_CLR = (112, 58, 58)



class Config:
    def __init__(self) -> None:
        self.update()

    def update(self):
        self.config_file = open('config.json', 'r')
        self.config_file.seek(0)
        self.settings = json.load(self.config_file)
        self.config_file.close()
    
    def get_category(self, option):
        for category_key in self.settings["global"]["metainfo"].keys():
            if option in self.settings["global"]["metainfo"][category_key]:
                return category_key
        raise Exception(f'No {option} option in "metainfo" mentioned')

    def get_players_settings(self):
        return self.settings["players"]
    
    def get_player_controls(self, num, option):
        return self.settings['players'][num]['controls'][option]
    
    def get_player_color(self, num):
        return tuple(self.settings['players'][num]['options']['color'])

    def get_all_settings(self):
        return self.settings

    def get_global_settings(self):
        return self.settings["global"]
    
    def get_global_controls(self):
        return self.settings["global"]["controls"]
    
    def get_global_options(self):
        return self.settings["global"]['options']

    def save(self):
        self.config_file = open('config.json', 'w')
        json.dump(self.settings, self.config_file, indent=4)
        self.config_file.close()
        self.update()

    def change(self, new_value, link): #todo
        match link[0]:
            case "global": self.settings[link[0]][link[1]][link[2]] = new_value
            case "players": self.settings[link[0]][int(link[1])][link[2]][link[3]] = new_value
        self.save()


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
    
    def die(self):
        del self


class Snake(Entity):
    def __init__(self, color, position, direction, num) -> None:
        super().__init__(color, position)
        match direction:
            case 1: self.position.append([position[0], position[1]-1])
            case 2: self.position.append([position[0]-1, position[1]])
            case 3: self.position.append([position[0], position[1]+1])
            case 4: self.position.append([position[0]+1, position[1]])
        self.direction = direction
        self.temp_direction = direction
        self.num = num
        self.dead = False

    def move(self):
        if self.dead: return 0
        if len(self.position) > 1:
            for current_element in range(len(self.position)-1,0,-1):
                self.position[current_element] = self.position[current_element-1][:]
        self.direction = self.temp_direction
        match self.direction:
            case 1: self.position[0][1] += 1 #up
            case 2: self.position[0][0] += 1 #right
            case 3: self.position[0][1] += -1 #down
            case 4: self.position[0][0] += -1 #left
        self.position[0][0] = self.position[0][0]%(SIZEOFMAP*16)
        self.position[0][1] = self.position[0][1]%(SIZEOFMAP*9)

    def turn(self, new_direction):
        if (self.direction - new_direction) % 2 != 0:
            self.temp_direction = new_direction

    def on_collision(self, attaker: Entity):
        attaker.die()

    def die(self):
        self.dead = True

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
        self.text_content = text
        self.text = self.font.render(text, True, self.color)

    def get_text(self):
        return self.text_content

    def set_text(self, text):
        self.text_content = text
        self.text = self.font.render(text, True, self.color)


class PageManager: # page conrtol
    '''
    reference = None   
    def get_reference(cls):
        if cls.reference == None:
            cls.reference = cls()
        return cls.reference            
    '''
    def init(self) -> None:
        self.singleplayerPage = SingleplayerPage()
        self.localMultiplayerPage = LocalMultiplayerPage(NUMOFPLAYERSINLOCAL) 
        self.onlineMultiplayerPage = OnlineMultiplayerPage()     
        self.settingsPage = SettingsPage()
        self.settingsChangePage = SettingsChangePage()

        #nav. pages (require additional .init())
        self.multiplayerTypePage = MultiplayerTypePage()      
        self.gameModePage = GameModePage()
        self.titlePage = TitlePage()
        self.multiplayerTypePage.init()
        self.gameModePage.init()
        self.titlePage.init()

        self.current_page = self.titlePage
        self.previous_page = self.titlePage

    def switch_to(self, page = None):
        if page == None: raise Exception('Invalid page')
        self.previous_page = self.current_page
        self.current_page = page
        page.run()

    def start(self):
        self.current_page.run()


class Page: # parent class for pages    
    def check_input(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == config.settings["global"]["controls"]["quit"]: pg.quit()
                #elif event.key == pg.K_TAB: pageManager.switch_to(pageManager.previous_page)
                else: self.handle_input(event.key)

    def run(self): 
        while pageManager.current_page == self:
            self.check_input() # buttons
            self.process_logic() # logic
            self.render_page() # render
            clock.tick(FPS)

    def process_logic(self): pass # no default logic

    def handle_input(self): 
        raise Exception('The handle_input() method is not implemented in the subclass') # additional buttons actions

    def render_page(self): 
        raise Exception('The render_page() method is not implemented in the subclass')


class NavigationPage(Page):
    def init(self, title, options) -> None:
        if len(options) > 9: raise Exception('len(options) > 9')
        self.title_text = Text(20, TTL_TEXT_CLR, title)
        self.options = []
        for i in range(len(options)):
            self.options.append([Text(10, MAIN_TEXT_CLR, (f'[{i+1}]: {options[i][0]}')), options[i][1]])   
    
    def handle_input(self, button):
        for i in range(len(self.options)):
            if button == getattr(pg, 'K_'+str(i+1)): pageManager.switch_to(self.options[i][1])

    def render_page(self):
        screen.fill(BLACK)
        screen.blit(self.title_text.text, (200, 300))
        for i in range(len(self.options)):
            screen.blit(self.options[i][0].text, (200, 450+(100*i)))
        pg.display.flip()



class TitlePage(NavigationPage):
    def init(self) -> None:
        super().init(TITLE, [
                            ['Play', pageManager.gameModePage],
                            ['Settings', pageManager.settingsPage]
                           ])
        

class GameModePage(NavigationPage):
    def init(self) -> None:
        super().init('Choose gamemode', [
                            ['Multiplayer', pageManager.multiplayerTypePage],
                            ['Singleplayer', pageManager.singleplayerPage],
                            ['Back', pageManager.titlePage]
                           ])


class MultiplayerTypePage(NavigationPage):
    def init(self) -> None:
        super().init('Choose multiplayer type', [
                            ['Local multiplayer', pageManager.localMultiplayerPage],
                            ['Online multiplayer', pageManager.onlineMultiplayerPage],
                            ['Back', pageManager.gameModePage]
                           ])

        
class SingleplayerPage(Page):
    def __init__(self) -> None:
        self.snakes = [Snake(config.get_player_color(0), rand_tile(), rand_direction(), 0)]
        self.game = Game(self.snakes)

    def handle_input(self, button):
        for i in range(len(self.snakes)): # match-case doesn't work)
            if button   == config.get_player_controls(i,'up'):    self.snakes[i].turn(3)
            elif button == config.get_player_controls(i,'right'): self.snakes[i].turn(2)
            elif button == config.get_player_controls(i,'down'):  self.snakes[i].turn(1)
            elif button == config.get_player_controls(i,'left'):  self.snakes[i].turn(4)
            elif button == config.get_global_controls()['grow'] and config.get_global_options()["debug_mode"]:   self.snakes[i].grow()
            elif button == config.get_global_controls()['die'] and config.get_global_options()["debug_mode"]:    self.snakes[i].die() 
            
 
    def process_logic(self):
        if len(self.game.players_remain()) <= 0: 
            self.__init__()
            pageManager.switch_to(pageManager.titlePage)
        self.game.next_frame()

    def render_page(self):
        self.game.render()


class LocalMultiplayerPage(Page): 
    def __init__(self, num_of_players) -> None:
        self.snakes = []
        for i in range(num_of_players):
            self.snakes.append(Snake(config.get_player_color(i), rand_tile(), rand_direction(), i))
        self.game = Game(self.snakes)

    def handle_input(self, button):
        for i in range(len(self.snakes)):
            if button   == config.get_player_controls(i,'up'):    self.snakes[i].turn(3)
            elif button == config.get_player_controls(i,'right'): self.snakes[i].turn(2)
            elif button == config.get_player_controls(i,'down'):  self.snakes[i].turn(1)
            elif button == config.get_player_controls(i,'left'):  self.snakes[i].turn(4)
            elif button == config.get_global_controls()['grow'] and config.get_global_options()["debug_mode"]:   self.snakes[i].grow()
            elif button == config.get_global_controls()['die'] and config.get_global_options()["debug_mode"]:    self.snakes[i].die() 

    def process_logic(self):
        if len(self.game.players_remain()) <= 1:
            if len(self.game.players_remain()) == 1:  print(config.settings["players"][self.game.players_remain()[0].num]["options"]["name"], 'won')
            if len(self.game.players_remain()) == 0:  print('No one won)')
            self.__init__(len(self.snakes))
            pageManager.switch_to(pageManager.titlePage)
        self.game.next_frame()

    def render_page(self):
        self.game.render()


class OnlineMultiplayerPage(Page): pass #WIP


class Game():
    def __init__(self, snakes) -> None:
        self.snakes = snakes
        self.food = Food(RED, rand_tile())

    def get_enetities(self):
        return self.snakes + [self.food]

    def next_frame(self):
        for snake in self.snakes:
            snake.move()
        for snake in self.snakes:
            self.check_collision(snake, self.get_enetities())
        if len(self.snakes) == 0:
            pageManager.switch_to(pageManager.gameModePage)

    def check_collision(self, checker, entities):
        head_tile = checker.get_position()[0]
        entities.remove(checker)
        if head_tile in checker.get_position()[1:]:
            checker.die()
        for entity in entities:
            if head_tile in entity.get_position(): 
                entity.on_collision(checker)
                
    def render(self):
        self.render_bg()
        for current_obj in self.get_enetities():
            for current_element in current_obj.get_position():
                screen.blit(current_obj.get_tile(), (current_element[0]*SIZEOFTILE, current_element[1]*SIZEOFTILE))  
        pg.display.flip()             

    def render_bg(self):
        screen.fill(BLACK)
        for x in range(SIZEOFMAP*16+1):
            pg.draw.line(screen, GREY ,[x*SIZEOFTILE,0], [x*SIZEOFTILE,RESOLUTION*9], 1)
        for y in range(SIZEOFMAP*9+1):
            pg.draw.line(screen, GREY ,[0,y*SIZEOFTILE], [RESOLUTION*16,y*SIZEOFTILE], 1)   

    def players_remain(self):
        alive = []
        for snake in self.snakes:
            if not snake.dead: alive.append(snake)
        return alive


class SettingsPage(Page):
    def __init__(self) -> None:
        self.title_text = Text(20, TTL_TEXT_CLR, 'Settings')
        self.go_back_text = Text(5, MAIN_TEXT_CLR, '[1] Exit    |    [2] Scroll up    |    [3] Scroll down    |    [4] Change')
        self.pointer = 0
        self.display_offset = 0
        self.pointer_img = Text(7, RED, '>')
        self.update_text()
        
    def update_text(self):
        self.settings_options = []
        self.settings_options.append([Text(6, WHITE, 'Global'), None])
        self.parse_option(config.get_global_settings(), 'global/')
        for player_num in range(len(config.get_players_settings())):
            self.settings_options.append([Text(6, WHITE, f'Player {player_num + 1}'), None])
            self.parse_option(config.get_players_settings()[player_num], f'players/{player_num}/')
        self.settings_options.append([Text(7, WHITE, 'Create another player profile'), 'new'])

    def parse_option(self, category, link):
        for option in category["options"].keys():
            self.settings_options.append([Text(5, LIGHT_GREY, f'{option} :    {category["options"][option]}'),  f'{link}options/{option}'])
        for control in category["controls"].keys():
            self.settings_options.append([Text(5, LIGHT_GREY, f'{control} :    {pg.key.name(category["controls"][control])}'), f'{link}controls/{control}'])

    def handle_input(self, button):
        match button:
            case pg.K_1: pageManager.switch_to(pageManager.titlePage)
            case pg.K_2: self.scroll(-1)
            case pg.K_3: self.scroll(1)
            case pg.K_4: self.change(self.settings_options[self.pointer+self.display_offset][1]) 

    def change(self, link):
        if link == None:
            return 
        if link == 'new':
            config.settings["players"].append({
            "options": {
                "name": "noname",
                "color": [
                    100,
                    100,
                    100
                ]
            },
            "controls": {
                "up": 0,
                "right": 0,
                "left": 0,
                "down": 0
            }})
            config.save()
            config.update()
            self.update_text()
            return
        pageManager.settingsChangePage.start(link) 

    def render_page(self):
        screen.fill(BLACK)
        screen.blit(self.title_text.text, (200, 50))
        screen.blit(self.go_back_text.text, (200, 200))
        screen.blit(self.pointer_img.text, (200, 239 + 50 * self.pointer))
        i = 0
        for displaying_option in range(self.display_offset, self.display_offset + LINES_PER_PAGE):
            screen.blit(self.settings_options[displaying_option][0].text, (250, 250 + 50 * i ))
            i += 1
        pg.display.flip()

    def scroll(self, lines):
        if 0 <= self.pointer + lines < LINES_PER_PAGE:
            self.pointer += lines
        else:
            if len(self.settings_options) - LINES_PER_PAGE >= self.display_offset + lines >= 0: 
                self.display_offset += lines


class SettingsChangePage(Page): # redo
    def __init__(self) -> None:
        self.change_text = {
            "buttons": Text(15, WHITE, 'Press new button'),
            "numbers": Text(15, WHITE, 'Write a number'),
            "tuples": Text(15, WHITE, 'Write a sequence of numbers'),
            "boolians": Text(15, WHITE, 'Write 0 or 1'),
            "text": Text(15, WHITE, 'Write something')
        }

    def handle_input(self, button):
        if self.page_preset == 'buttons':
            self.change_value(button)
            self.submit()

        if button == pg.K_RETURN: 
            match self.page_preset:
                case 'text': self.change_value(self.input_text.get_text())
                case 'numbers': self.change_value(int(self.input_text.get_text()))
                case 'tuples': self.change_value( tuple(map(int, self.input_text.get_text().split())) ) 
                case 'boolians': self.change_value( bool(int(self.input_text.get_text())) )
            self.submit()

        match button:
            case pg.K_BACKSPACE: self.input_text.set_text( self.input_text.get_text()[:-1] ) 
            case pg.K_SPACE: self.input_text.set_text( self.input_text.get_text() + ' ' ) 
            case _: self.input_text.set_text( self.input_text.get_text() + str(pg.key.name(button)) ) 

    def start(self, link):
        self.input_text = Text(text='')
        self.link = link.split('/')
        self.page_preset = config.get_category(self.link[-1])
        pageManager.switch_to(pageManager.settingsChangePage)

    def change_value(self, new_key):
        config.change(new_key, self.link) 

    def submit(self):
        config.update()
        pageManager.settingsPage.update_text()
        pageManager.switch_to(pageManager.settingsPage) 

    def render_page(self):
        screen.fill(BLACK)
        screen.blit(self.change_text[self.page_preset].text, (300, 100))
        screen.blit(self.input_text.text, (300, 300))

        pg.display.flip()



def rand_tile(padding = 3):
    return [padding + round(random.random()*(SIZEOFMAP*16-(2*padding))), 
            padding + round(random.random()*(SIZEOFMAP*9-(2*padding)))]

def rand_color():
    return (round(random.random()*150) + 105, 
            round(random.random()*150) + 105, 
            round(random.random()*150) + 105)

def rand_direction():
    return round(random.random()*3) + 1



config = Config()
TITLE = config.settings["global"]['metainfo']['TITLE']
SIZEOFMAP = config.get_global_options()['size_of_a_map']
RESOLUTION = config.get_global_options()['resolution'] # 120: 1080p / 160: 1440p
FPS = config.get_global_options()['fps']
NUMOFPLAYERSINLOCAL = config.get_global_options()['num_of_local_players']
SIZEOFTILE = RESOLUTION//SIZEOFMAP
SF = (RESOLUTION*9)//100 # scale factor [1% of screen height in px]
LINES_PER_PAGE = 16

pg.init()
pg.display.set_caption(TITLE)
screen = pg.display.set_mode((RESOLUTION*16,RESOLUTION*9))
save = SaveFile('results.txt')
clock = pg.time.Clock()



pageManager = PageManager()
pageManager.init()
pageManager.start()

