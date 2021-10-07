from typing import List, Tuple

import pygame

from core.geom import WindowGeometry
import numpy as np

class World:
    points = np.array([]).reshape(0, 2)
    COLOR = (201, 45, 34)#(255, 0, 0)
    i = 0
    dt = 2

    def __init__(self, geom: WindowGeometry) -> None:
        self.geom = geom
    
    def clear(self) -> None:
        self.points = np.array([]).reshape(0, 2)

    def update_geom(self, geom: WindowGeometry) -> None:
        self.geom = geom

    def add_point(self, p: Tuple[int, int]) -> None:
        '''Add point to the world'''
        if self.geom.on_grid(p[0], p[1]):
            self.points = np.vstack([self.points, self.geom.transform_screen_coords(p[0], p[1])])
    
    def get_points(self) -> List[Tuple[int, int]]:
        '''Get points in the world'''
        return self.points
    
    def get_closest_point_idx(self, p: Tuple[int, int]) -> int:
        if self.points.size == 0:
            return None
        px = self.geom.transform_screen_coords(p[0], p[1])
        if px is None:
            return None
        C = np.broadcast_to(px, self.points.shape)
        # manhattan distance
        x_tol = (self.geom.range(self.geom.xrange) / self.geom.range(self.geom.gridX)) * 3
        y_tol = (self.geom.range(self.geom.yrange) / self.geom.range(self.geom.gridY)) * 3
        atol = min(x_tol, y_tol)
        md = np.isclose(self.points, C, atol=atol).sum(axis=1) == C.shape[1]
        if md.any():
            return np.argmax(md)
        else:
            return None

    def update_point(self, idx: int, p: Tuple[int, int]) -> None:
        if self.geom.on_grid(p[0], p[1]):
            self.points[idx] = self.geom.transform_screen_coords(p[0], p[1])

    def delete_point(self, idx: int) -> None:
        self.points = np.delete(self.points, idx, 0)
    
    def draw(self, window: pygame.Surface):
        for p in self.points:
            ps = self.geom.transform_coords(p[0], p[1], clip=False)
            if ps is not None:
                pygame.draw.circle(window, self.COLOR, ps, 10)