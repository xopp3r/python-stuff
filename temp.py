from __future__ import annotations
import numpy as np
import pygame as pg
import os
from abc import abstractmethod, ABC
from random import randint
import opensimplex 
import json



#colors
WHITE = (255,255,255)
GRASS_GREEN = (0,154,23)
BLACK = (0,0,0)
BACKGROUND_COLOR = (32, 59, 39)

#settings
FPS: int = 120
RESOLUTION: int = 1080
MAP_SIZE = 50 #radius
DEBUG_MODE = False #rip performance
SEED = 0 #0: random 
GENERATION_COOF = 7

#sys vars
exited: bool = False
fullscreen: bool = False
SCREEN_RESOLUTION = ((16*RESOLUTION//9, RESOLUTION))



class UI:
    def __init__(self, size: tuple[int, int]) -> None:
        self.resolution = np.array(size)
        self.observers :any = []

    def add_observers(self, obj) -> None: #redo : add types and create interface
        self._notify_observers(obj)

    def _notify_observers(self) -> None:
        for obj in self.observers:
            obj.rescale()

    def rescale(self, size: tuple[int, int]) -> None:
        self.height = size[0]
        self.width = size[1]

        print(f'rescaled to {self.height, self.width}') # todo



class Tile:
    # [0] -> q />
    # [1] -> r \|/
    # [2] -> s <\
    def __init__(self, coordinates:tuple[int,int,int], biome_id: int, color:tuple[int,int,int] = WHITE) -> None: 
        self.position = np.array(coordinates, dtype=np.int16)
        self.biome_id = biome_id
        self.color = color
        self.surface = self.pre_draw_hexagon()
        self.scaled_surface = self.surface
        self.zoom = 1
    
        if DEBUG_MODE:
            self.font = pg.font.Font(None, 20)
            self.text = self.font.render(str(self.position), True, WHITE)

    def rescale(self, zoom:  float) -> pg.Surface:
        if self.zoom == zoom: return self.scaled_surface
        else:
            self.scaled_surface = pg.transform.scale_by(self.surface, zoom)
            self.zoom = zoom
            return self.scaled_surface

    def pre_draw_hexagon(self) -> pg.Surface:
        surface = pg.Surface((200,200), pg.SRCALPHA)
        pg.draw.polygon(surface, self.color, 95*(Tile.vertices()+1), 0)
        return surface

    @staticmethod
    def directions(n:int) -> np.ndarray:
        return np.array([[+1, 0, -1], [+1, -1, 0], [0, -1, +1], [-1, 0, +1], [-1, +1, 0], [0, +1, -1]]) [n]
    
    @staticmethod
    def vertices() -> np.ndarray:
        return np.array([[0, 1], [np.sqrt(3)/2, 0.5], [np.sqrt(3)/2, -0.5], [0, -1], [-np.sqrt(3)/2, -0.5], [-np.sqrt(3)/2, 0.5]])      #flat top
        #return np.array([[1, 0], [0.5, np.sqrt(3)/2], [-0.5, np.sqrt(3)/2], [-1, 0], [-0.5, -np.sqrt(3)/2], [0.5, -np.sqrt(3)/2]])     #pointy top



class Camera:
    def __init__(self, ui: UI) -> None:
        self._ui = ui
        self._position = np.array([0,0], dtype=float)
        self._zoom: float = 1/2
        self._moving: bool = False


    def change_zoom(self, coof: int) -> None:
        if 0.03 <= (self._zoom * 2**(coof/6)) <= 1.5: self._zoom *= 2**(coof/6)

    def get_zoom(self) -> int:
        return self._zoom

    def get_position(self) -> np.ndarray:
        return self._position

    def process_movement(self) -> None:
        if self._moving:
            end_pos = pg.mouse.get_pos()
            self._position += (np.array(self._start_pos) - np.array(end_pos)) / self._zoom 
            self._start_pos = end_pos
           
    def start_movement(self, pos: tuple[int,int]) -> None:
        self._moving = True
        self._start_pos = pos

    def stop_movement(self) -> None:
        self._moving = False



class GameMap:
    def __init__(self, tiles: dict = {}) -> None:
        self.tiles: dict[tuple,Tile] = tiles
    
    def add_tile(self, tile: Tile) -> None:
        self.tiles[tuple(tile.position)] = tile

    def add_tiles(self, tiles: list[Tile]) -> None:
        for tile in tiles:
            self.tiles[tuple(tile.position)] = tile

    def get_tile(self, coordinates: tuple[int,int,int]) -> Tile:
        return self.tiles[tuple(coordinates)]
    
    def neighbors(self, tile: Tile) -> list[Tile]:
        return [self.get_tile(tile.position + tile_direction) for tile_direction in Tile.directions()]

    @staticmethod
    def distanse(tile1: Tile, tile2: Tile) -> int:
        return (abs(tile2.position[0] - tile1.position[0]) + abs(tile2.position[1] - tile1.position[1]) + abs(tile2.position[2] - tile1.position[2])) / 2

    @staticmethod
    def cube_to_xy(cube_coor: np.ndarray) -> np.ndarray:
        return np.matmul( cube_coor[:2], np.array([[np.sqrt(3), 0],[np.sqrt(3)/2, 1.5]]) )

    @staticmethod
    def xy_to_cube(xy_coor: np.ndarray) -> np.ndarray:
        qr =  np.matmul(xy_coor, np.array([[np.sqrt(3)/3, 0],[-1/3, 2/3]]))
        return GameMap.round_cube_coor( np.array([qr[0],qr[1],-sum(qr)]) )

    @staticmethod
    def round_cube_coor(coor: np.ndarray) -> np.ndarray:
        q_diff = coor[0] - round(coor[0])
        r_diff = coor[1] - round(coor[1])
        s_diff = coor[2] - round(coor[2])
        if abs(q_diff) > abs(r_diff) and abs(q_diff) > abs(s_diff):
            return np.array([ -round(coor[1]) - round(coor[2]), round(coor[1]), round(coor[2]) ])
        elif abs(r_diff) > abs(s_diff):
            return np.array([ round(coor[0]), -round(coor[0]) - round(coor[2]), round(coor[2]) ])
        else:
            return np.array([ round(coor[0]), round(coor[1]), -round(coor[0]) - round(coor[1]) ])   
    
    @staticmethod
    def ring(center_tile_pos: tuple[int,int,int], radius: int) -> list[tuple[int,int,int]]:
        if radius <= 0: raise Exception(f'{radius} isnt a valid radius')
        center_tile_pos = np.array(center_tile_pos)
        ring_tiles_pos = []
        current_pos = center_tile_pos + Tile.directions(4)*radius
        for ring_edge in range(6):
            for _ in range(radius):
                ring_tiles_pos.append(tuple(current_pos))
                current_pos += Tile.directions(ring_edge)
        return ring_tiles_pos



class View:
    def __init__(self, ui: UI, camera: Camera, screen: pg.Surface) -> None:
        self.ui = ui
        self.camera = camera
        self.screen = screen

    def draw_hexagones(self, tiles: dict[tuple, Tile]) -> None:
        #for tile in tiles.items():
            #screen_points = ui.resolution//2 + camera.get_zoom() * (100*GameMap.cube_to_xy(tile[1].position) - camera.get_position() - 100)
            #self.screen.blit(tile[1].surface, screen_points)
        self.screen.blits([([tile.rescale(self.camera.get_zoom()), 
                 ui.resolution//2 + camera.get_zoom() * (100*GameMap.cube_to_xy(tile.position) - camera.get_position() - 100)]) 
                            for tile in tiles.values()])
        

        #if DEBUG_MODE: screen.blit(tile[1].text, self.ui.resolution//2 + self.camera.get_zoom() * (100*GameMap.cube_to_xy(tile[1].position) - self.camera.get_position()))
            
    def clicked(self, pos: tuple[int, int]):
        pixel = np.array(pos) - ui.resolution//2
        coord_xy = ( pixel/self.camera.get_zoom() + self.camera.get_position() ) / 100
        tile_coord = GameMap.xy_to_cube(coord_xy)
        print(gameMap.get_tile(tile_coord).biome_id)




class EventHandler:pass




class Utils:
    @staticmethod
    def tune_color(input_color: tuple, intensity: int = 0) -> tuple:
        if intensity == 0: return input_color
        tuned_color = np.array(input_color) + np.array([randint(-intensity,intensity), randint(-intensity,intensity), randint(-intensity,intensity)]) 
        for i in range(len(tuned_color)):
            if tuned_color[i] > 255 : tuned_color[i] = 255
            if tuned_color[i] < 0 : tuned_color[i] = 0
        return tuned_color



class MapGen:
    def __init__(self, seed:int) -> None:
        if seed != 0: opensimplex.seed(seed)
        else: opensimplex.random_seed()
        with open(os.path.join('biomes.json'), 'r') as f:
            self.biomes = json.load(f)

    def _get_tile_properties(self, pos: tuple) -> dict[str,any]:
        value = MapGen._pos_to_value(pos)
        if -1 <= value <= -0.5: return self.biomes['water']
        elif -0.5 < value <= 0.5: return self.biomes['grass']
        elif 0.5 < value <= 1: return self.biomes['mountain']

        else: raise Exception(f'Invalid biome value: {value}')

    @staticmethod
    def _pos_to_value(pos: tuple) -> float:
        return opensimplex.noise2(pos[0]/GENERATION_COOF, pos[1]/GENERATION_COOF)

    @staticmethod
    def generate(pos: tuple) -> Tile:
        properties = MapGen._get_tile_properties()
        return Tile(pos, Utils.tune_color(properties['color'], properties['color_tune_intensity']))

    def generate_map(self, radius:int) -> GameMap:
        gameMap = GameMap()
        gameMap.add_tile(Tile((0,0,0), -1))
        for r in range(1, radius):
            for tile_pos in GameMap.ring((0,0,0), r):
                properties = self._get_tile_properties(tile_pos)
                tile = Tile(tile_pos, properties["biome_id"], Utils.tune_color(tuple(properties["color"]), properties["color_tuning"]))
                gameMap.add_tile(tile)
        return gameMap





pg.init()
pg.display.set_caption('Hexed v0.1')
pg.display.set_icon( pg.image.load(os.path.join('textures\grass.png')) )
screen = pg.display.set_mode(SCREEN_RESOLUTION, pg.RESIZABLE)
clock = pg.time.Clock()
ui = UI(SCREEN_RESOLUTION)
camera = Camera(ui)
view = View(ui, camera, screen)
mapGen = MapGen(SEED)
gameMap = mapGen.generate_map(MAP_SIZE)



print(len(gameMap.tiles))




while not exited: #main loop  

    #*

    for event in pg.event.get(): # sry) redo everything
        match event.type:
            case pg.QUIT: 
                exited = True
            case pg.WINDOWRESIZED:
                ui.rescale((event.y, event.x))
            case pg.KEYDOWN:
                match event.key: 
                    case pg.K_F11:
                        fullscreen = not fullscreen 
                        if fullscreen: screen = pg.display.set_mode(flags = pg.FULLSCREEN)
                        else: screen = pg.display.set_mode(SCREEN_RESOLUTION, flags=pg.RESIZABLE)
                        ui.rescale((pg.display.Info().current_h, pg.display.Info().current_w))
                    case pg.K_ESCAPE: exited = True
            case pg.MOUSEWHEEL:
                camera.change_zoom(event.y)
            case pg.MOUSEBUTTONDOWN:
                match event.button:
                    case 1: camera.start_movement(event.pos)
                    case 3: view.clicked(event.pos)
            case pg.MOUSEBUTTONUP:
                if event.button == 1 : camera.stop_movement()

    #*

    camera.process_movement()

    #*

    screen.fill(BACKGROUND_COLOR)
    view.draw_hexagones(gameMap.tiles)

    #*

    pg.display.flip()

    #*

    print(f'latency: {clock.get_time()}')


    clock.tick(FPS)
    
pg.quit()
