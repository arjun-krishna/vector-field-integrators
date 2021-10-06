from typing import Tuple
import pygame

from core.app_constants import TITLE
from core.controller import Controller
from core.geom import WindowGeometry
from core.grid import Grid
from core.quiver import Quiver
from core.ui_constants import GRID_COLOR, WINDOW_BACKGROUND
from core.world import World

class AppWindow:

    def __init__(self) -> None:
        geom = WindowGeometry()
        self.window = pygame.display.set_mode(geom.get_window_size())
        pygame.display.set_caption(TITLE)
        pygame.font.init()

        self.geom = WindowGeometry()
        self.grid = Grid(grid_color=GRID_COLOR)
        self.quiver = Quiver()
        self.world = World(self.geom)
        self.ctrl = Controller(self.world)

    def draw(self) -> None:
        self.window.fill(WINDOW_BACKGROUND)
        # update geom ranges from ctrl
        self.geom.xrange = self.ctrl.get_Xrange()
        self.geom.yrange = self.ctrl.get_Yrange()
        self.world.update_geom(self.geom)
        # end update

        # draw control pane
        self.ctrl.draw(self.window, self.geom)

        # draw grid
        self.grid.draw(self.window, self.geom)

        # draw quiver
        self.quiver.draw(self.window, self.geom, self.ctrl.get_Vx(), self.ctrl.get_Vy())

        # draw world
        self.world.draw(self.window)

    def run(self) -> None:
        self.window.fill(WINDOW_BACKGROUND)
        pygame.display.flip()
        while True:
            self.draw()
            for event in pygame.event.get():
                self.ctrl.event_handler(self.geom, event)
            pygame.display.update()