from typing import List, Tuple

import pygame

from core.geom import WindowGeometry
import numpy as np

class World:
    points = np.array([]).reshape(0, 2)
    COLOR = (255, 165, 0)
    i = 0
    dt = 2

    def __init__(self, geom: WindowGeometry) -> None:
        self.geom = geom

    def update_geom(self, geom: WindowGeometry):
        self.geom = geom

    def add_point(self, p: Tuple[int, int]) -> None:
        '''Add point to the world'''
        if self.geom.on_grid(p[0], p[1]):
            self.points = np.vstack([self.points, self.geom.transform_screen_coords(p[0], p[1])])
    
    def get_points(self) -> List[Tuple[int, int]]:
        '''Get points in the world'''
        return self.points 
    
    def draw(self, window: pygame.Surface):
        for p in self.points:
            ps = self.geom.transform_coords(p[0], p[1], clip=False)
            if ps is not None:
                pygame.draw.circle(window, self.COLOR, ps, 10)