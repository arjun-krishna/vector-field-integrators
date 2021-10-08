from typing import List, Tuple

import pygame

from core.geom import WindowGeometry
import numpy as np


class World:
    points = np.array([]).reshape(0, 2)
    meta_data = np.array([]).reshape(0,4) # nsteps, dt_euler, dt_midpoint, dt_rk4
    active_ipls = np.array([], dtype=np.bool8).reshape(0, 3) # euler, midpoint, rk4
    COLOR = (201, 45, 34)  # (255, 0, 0)
    SELECTED_COLOR = (235, 143, 52)
    BLACK = (0, 0, 0)
    i = 0
    dt = 2
    selected_idx = None
    display_idx = True

    def __init__(self, geom: WindowGeometry) -> None:
        self.geom = geom
        self.font = pygame.font.SysFont('arial', 14)

    def clear(self) -> None:
        self.points = np.array([]).reshape(0, 2)
        self.meta_data = np.array([]).reshape(0, 4)
        self.active_ipls = np.array([], dtype=np.bool8).reshape(0, 3)
        self.selected_idx = None

    def update_geom(self, geom: WindowGeometry) -> None:
        self.geom = geom

    def add_point(self, p: Tuple[int, int]) -> None:
        '''Add point to the world'''
        if self.geom.on_grid(p[0], p[1]):
            self.points = np.vstack([self.points, self.geom.transform_screen_coords(p[0], p[1])])
            self.meta_data = np.vstack([self.meta_data, [100, 0.5, 0.5, 0.5]])
            self.active_ipls = np.vstack([self.active_ipls, [False, True, False]])
    
    def toggle_integrator(self, idx: int) -> None:
        if self.selected_idx is not None:
            self.active_ipls[self.selected_idx, idx] = not self.active_ipls[self.selected_idx, idx]

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
        x_tol = (self.geom.range(self.geom.xrange) /
                 self.geom.range(self.geom.gridX)) * 3
        y_tol = (self.geom.range(self.geom.yrange) /
                 self.geom.range(self.geom.gridY)) * 3
        atol = min(x_tol, y_tol)
        md = np.isclose(self.points, C, atol=atol).sum(axis=1) == C.shape[1]
        if md.any():
            return np.argmax(md)
        else:
            return None

    def update_point(self, idx: int, p: Tuple[int, int]) -> None:
        if self.geom.on_grid(p[0], p[1]):
            self.points[idx] = self.geom.transform_screen_coords(p[0], p[1])

    def update_meta_data(self, idx: int, meta_idx: int, value: float) -> None:
        self.meta_data[idx,meta_idx] = value

    def delete_point(self, idx: int) -> None:
        self.points = np.delete(self.points, idx, 0)
        self.meta_data = np.delete(self.meta_data, idx, 0)
        self.active_ipls = np.delete(self.active_ipls, idx, 0)

    def draw(self, window: pygame.Surface):
        for idx, p in enumerate(self.points):
            ps = self.geom.transform_coords(p[0], p[1], clip=False)
            if ps is not None:
                col = self.SELECTED_COLOR if self.selected_idx == idx else self.COLOR
                pygame.draw.circle(window, col, ps, 10)
                if self.display_idx:
                    ts = self.font.render(f"P{idx}", False, self.BLACK)
                    window.blit(ts, (ps[0], ps[1]+10))
