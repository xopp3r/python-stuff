from __future__ import annotations
import numpy as np
import pygame as pg
import os
from abc import abstractmethod, ABC


FPS: int = 120
exited: bool = False
fullscreen: bool = False
RESOLUTION: int = 1080
SCREEN_RESOLUTION = ((16*RESOLUTION//9, RESOLUTION))
WHITE = (255,255,255)





class UI:
    def __init__(self, size: tuple[int, int]) -> None:
        self.resolution = np.array(size)
        self.observers :any = []

    def add_observers(self, obj) -> None: #edo : add types and create interface
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
    def __init__(self, coordinates:tuple[int,int,int]) -> None:
        self.position = np.array(coordinates, dtype=np.int16)

    @staticmethod
    def directions() -> np.ndarray:
        return np.array([[+1, 0, -1], [+1, -1, 0], [0, -1, +1], [-1, 0, +1], [-1, +1, 0], [0, +1, -1]])
    
    @staticmethod
    def vertices() -> np.ndarray:
        return np.array([[0, 1], [np.sqrt(3)/2, 0.5], [np.sqrt(3)/2, -0.5], [0, -1], [-np.sqrt(3)/2, -0.5], [-np.sqrt(3)/2, 0.5]])



class Camera:
    def __init__(self, ui: UI) -> None:
        self._ui = ui
        self._position = self._ui.resolution//2
        self._zoom: int = 100
        self._moving: bool = False
        
    def change_zoom(self, coof: int) -> None:
        if 30 <= (self._zoom * 2**(coof/6)) <= 150: self._zoom *= 2**(coof/6)

    def get_zoom(self) -> int:
        return self._zoom

    def get_position(self) -> np.ndarray:
        return self._position

    def process_movement(self) -> None:
        if self._moving:
            end_pos = pg.mouse.get_pos()
            self._position += np.array(end_pos) - np.array(self._start_pos)
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
    def cube_to_xy(vec: np.ndarray):
        return np.matmul( vec[:2] , np.array([[np.sqrt(3), 0],[np.sqrt(3)/2, 1.5]]) )



class Renderer:pass
class EventHandler:pass







def draw_hexagones(tiles: dict[Tile]) -> None: #redo : instanse to camera
    for tile_pos in tiles.keys():
        points = camera.get_position() + camera.get_zoom() * (GameMap.cube_to_xy(tile_pos) + Tile.vertices())
        pg.draw.polygon(screen, WHITE, points, 2)





pg.init()
screen = pg.display.set_mode(SCREEN_RESOLUTION, pg.RESIZABLE)
clock = pg.time.Clock()
ui = UI(SCREEN_RESOLUTION)
camera = Camera(ui)

#grass_texture = pg.image.load(os.path.join('textures\grass.png'))




gameMap = GameMap()
t = []
for a in range(-10,10):
    for b in range(-10,10):
        t.append(Tile((a,b,-a-b)))
gameMap.add_tiles(t)





while not exited: #main loop 
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
                        else: screen = pg.display.set_mode(SCREEN_RESOLUTION)
                        ui.rescale((pg.display.Info().current_h, pg.display.Info().current_w))
                    case pg.K_ESCAPE: exited = True
            case pg.MOUSEWHEEL:
                camera.change_zoom(event.y)
            case pg.MOUSEBUTTONDOWN:
                if event.button == 1 : 
                    camera.start_movement(event.pos)
            case pg.MOUSEBUTTONUP:
                if event.button == 1 : camera.stop_movement()

    camera.process_movement()


    screen.fill((0,0,0))
    draw_hexagones(gameMap.tiles)


    pg.display.flip()
    clock.tick(FPS)
    
pg.quit()