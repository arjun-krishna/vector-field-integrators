from typing import Tuple
from core.app_constants import DEFAULT_GRID_SIZE, DEFAULT_WINDOW_SIZE, PANE_1, PANE_2
import numpy as np


class WindowGeometry:
    window_size: Tuple[int, int] = DEFAULT_WINDOW_SIZE
    pane1: int = PANE_1
    pane2: int = PANE_2
    grid_size: int = DEFAULT_GRID_SIZE

    def __init__(self) -> None:
        self.controller_width = self.pane1
        self.ctrlX = (0, self.controller_width)
        self.ctrlY = (0, self.window_size[1])
        self.gridX = (self.controller_width, self.pane2)
        self.gridY = (0, self.window_size[1])
        self.xrange = (-3.0, 3.0)
        self.yrange = (-3.0, 3.0)

    def get_window_size(self) -> Tuple[int, int]:
        '''Returns total window size'''
        return self.window_size

    def on_grid(self, xs: int, ys: int) -> bool:
        '''Tests if screen co-ordinates (xs, ys) is on the grid'''
        return (xs >= self.gridX[0] and xs <= self.gridX[1]) and \
            (ys >= self.gridY[0] and ys <= self.gridY[1])

    def in_range(self, x: int, y: int) -> bool:
        '''Tests if (x,y) co-ordinate is in range'''
        return (x >= self.xrange[0] and x <= self.xrange[1]) and \
            (y >= self.yrange[0] and y <= self.yrange[1])

    def range(self, t: Tuple[any, any]) -> any:
        return t[1] - t[0]

    def transform_screen_coords(self, xs: int, ys: int) -> Tuple[int, int]:
        '''Screen co-ordinates (xs, ys) to (x, y)'''
        if self.on_grid(xs, ys):
            x = self.xrange[0] + (self.range(self.xrange) /
                                  self.range(self.gridX) * (xs - self.gridX[0]))
            y = self.yrange[0] + (self.range(self.yrange) /
                                  self.range(self.gridY) * (self.gridY[1] - ys))
            return (x, y)
        else:
            return None

    def transform_coords(self, x: int, y: int, clip: bool = True) -> Tuple[int, int]:
        '''co-ordinates (x, y) to screen co-ordinates (xs, ys)'''
        if clip:
            x = min(x, self.xrange[1])
            x = max(x, self.xrange[0])
            y = min(y, self.yrange[1])
            y = max(y, self.yrange[0])
        if self.in_range(x, y):
            xs = self.gridX[0] + (self.range(self.gridX) /
                                  self.range(self.xrange) * (x - self.xrange[0]))
            ys = self.gridY[1] + (self.range(self.gridY) /
                                  self.range(self.yrange) * (self.yrange[0] - y))
            return (xs, ys)
        else:
            return None

    def meshgrid(self):
        return np.mgrid[self.xrange[0]:self.xrange[1]:20j, self.yrange[0]:self.yrange[1]:20j]
