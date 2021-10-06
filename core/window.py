from typing import Tuple
import pygame

from core.app_constants import TITLE
from core.controller import Controller
from core.geom import WindowGeometry
from core.grid import Grid
from core.quiver import Quiver
from core.ui_constants import GRID_COLOR, WINDOW_BACKGROUND

class AppWindow:

    def __init__(self) -> None:
        geom = WindowGeometry()
        self.window = pygame.display.set_mode(geom.get_window_size())
        pygame.display.set_caption(TITLE)
        pygame.font.init()

        self.ctrl = Controller()

        self.geom = WindowGeometry()
        self.grid = Grid(grid_color=GRID_COLOR)
        self.quiver = Quiver()

    def draw(self) -> None:
        self.window.fill(WINDOW_BACKGROUND)
        # update geom ranges from ctrl
        self.geom.xrange = self.ctrl.get_Xrange()
        self.geom.yrange = self.ctrl.get_Yrange()
        # end update
        self.ctrl.draw(self.window, self.geom)
        self.grid.draw(self.window, self.geom)
        self.quiver.draw(self.window, self.geom, self.ctrl.get_Vx(), self.ctrl.get_Vy())

    def run(self) -> None:
        self.window.fill(WINDOW_BACKGROUND)
        pygame.display.flip()
        while True:
            self.draw()
            for event in pygame.event.get():
                self.ctrl.event_handler(event)
            pygame.display.update()