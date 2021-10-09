from typing import List, Tuple

import pygame

from core.geom import WindowGeometry
import numpy as np
from core.solvers import ExplicitEulerSolver, MidpointSolver, RK4Solver

from core.system import System


class World:
    points = np.array([]).reshape(0, 2)
    meta_data = np.array([]).reshape(0,4) # nsteps, dt_euler, dt_midpoint, dt_rk4
    active_ipls = np.array([], dtype=np.bool8).reshape(0, 3) # euler, midpoint, rk4
    COLOR = (201, 45, 34)  # (255, 0, 0)
    SELECTED_COLOR = (235, 143, 52)
    BLACK = (0, 0, 0)
    selected_idx = None
    
    multi_select_mode = False
    select_corner1: Tuple[int, int] = None
    select_corner2: Tuple[int, int] = None
    mouse_pos: Tuple[int, int] = None
    
    # UI
    display_idx = True
    draw_trails = True

    # trail colors
    COL1 = (255, 0, 0)
    COL2 = (0, 255, 0)
    COL3 = (0, 0, 255)

    steps = 0
    in_anim = False
    euler_points = np.array([]).reshape(0, 2)
    midpoint_points = np.array([]).reshape(0, 2)
    rk4_points = np.array([]).reshape(0, 2)
    euler_meta = np.array([]).reshape(0, 2)
    midpoint_meta = np.array([]).reshape(0, 2)
    rk4_meta = np.array([]).reshape(0, 2)
    euler_system = None
    midpoint_system = None
    rk4_system = None

    euler_solver = ExplicitEulerSolver()
    midpoint_solver = MidpointSolver()
    rk4_solver = RK4Solver()


    def __init__(self, geom: WindowGeometry) -> None:
        self.geom = geom
        self.font = pygame.font.SysFont('arial', 14)

    def clear(self) -> None:
        self.points = np.array([]).reshape(0, 2)
        self.meta_data = np.array([]).reshape(0, 4)
        self.active_ipls = np.array([], dtype=np.bool8).reshape(0, 3)
        self.selected_idx = None
        self.multi_select_mode = False
        self.select_corner1 = None
        self.select_corner2 = None

    def update_geom(self, geom: WindowGeometry) -> None:
        self.geom = geom

    def add_point(self, p: Tuple[int, int]) -> None:
        '''Add point to the world'''
        if self.geom.on_grid(p[0], p[1]):
            self.points = np.vstack([self.points, self.geom.transform_screen_coords(p[0], p[1])])
            self.meta_data = np.vstack([self.meta_data, [100, 0.01, 0.01, 0.01]])
            self.active_ipls = np.vstack([self.active_ipls, [True, False, False]])
    
    def toggle_integrator(self, idx: int) -> None:
        if self.selected_idx is not None:
            self.active_ipls[self.selected_idx, idx] = not self.active_ipls[self.selected_idx, idx]
        if self.multi_select_mode:
            ids = self.get_point_ids_in_bounding_box()
            self.active_ipls[ids, idx] = np.logical_not(self.active_ipls[ids, idx])

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
                 self.geom.range(self.geom.gridX)) * 5
        y_tol = (self.geom.range(self.geom.yrange) /
                 self.geom.range(self.geom.gridY)) * 5
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

    def get_point_ids_in_bounding_box(self):
        ids = []
        if self.select_corner1 is not None and self.select_corner2 is not None:
            c1, c2 = self.select_corner1, self.select_corner2
            W = abs(c2[0] - c1[0])
            H = abs(c2[1] - c1[1])
            if c1[0] < c2[0] and c1[1] < c2[1]:
                top, left = c1[0], c1[1]
            elif c1[0] < c2[0] and c1[1] > c2[1]:
                top, left = c1[0], c2[1]
            elif c1[0] > c2[0] and c1[1] > c2[1]:
                top, left = c2[0], c2[1]
            else:
                top, left = c2[0], c1[1]

            xmin, ymax = self.geom.transform_screen_coords(top, left)
            xmax, ymin = self.geom.transform_screen_coords(top+W, left+H)
            
            for i, p in enumerate(self.points):
                if p[0] >= xmin and p[0] <= xmax and \
                    p[1] >= ymin and p[1] <= ymax:
                    ids.append(i)
        return ids

    def update_meta_data_on_bounding_box(self, meta_idx: int, value: float) -> None:
        ids = self.get_point_ids_in_bounding_box()
        self.meta_data[ids,meta_idx] = value

    def clear_config_on_bounding_box(self) -> None:
        ids = self.get_point_ids_in_bounding_box()
        self.active_ipls[ids, :] = [False, False, False]
        self.meta_data[ids, :] = [0, 0, 0, 0]

    def delete_point(self, idx: int) -> None:
        self.points = np.delete(self.points, idx, 0)
        self.meta_data = np.delete(self.meta_data, idx, 0)
        self.active_ipls = np.delete(self.active_ipls, idx, 0)

    def draw(self, window: pygame.Surface):
        if self.in_anim:
            self.draw_animated(window)
            self.step_world()
        else:
            self.draw_points(window)
            if self.multi_select_mode:
                c1 = self.select_corner1
                mp = self.mouse_pos if self.geom.on_grid(self.mouse_pos[0], self.mouse_pos[1]) else None
                c2 = self.select_corner2 if self.select_corner2 else mp

                if c1 is not None and c2 is not None:
                    # draw selection rectangle
                    W = abs(c2[0] - c1[0])
                    H = abs(c2[1] - c1[1])
                    if c1[0] < c2[0] and c1[1] < c2[1]:
                        top, left = c1[0], c1[1]
                    elif c1[0] < c2[0] and c1[1] > c2[1]:
                        top, left = c1[0], c2[1]
                    elif c1[0] > c2[0] and c1[1] > c2[1]:
                        top, left = c2[0], c2[1]
                    else:
                        top, left = c2[0], c1[1]
                    rect = pygame.Rect(top, left, W, H)
                    pygame.draw.rect(window, self.BLACK, rect, 2)

    def draw_points(self, window: pygame.Surface):
        for idx, p in enumerate(self.points):
            ps = self.geom.transform_coords(p[0], p[1], clip=False)
            if ps is not None:
                col = self.SELECTED_COLOR if self.selected_idx == idx else self.COLOR
                pygame.draw.circle(window, col, ps, 10)
                if self.display_idx:
                    ts = self.font.render(f"P{idx}", False, self.BLACK)
                    window.blit(ts, (ps[0], ps[1]+10))

    def draw_animated(self, window: pygame.Surface):
        self.draw_animated_points(window, self.euler_points, self.COL1)
        self.draw_animated_points(window, self.midpoint_points, self.COL2)
        self.draw_animated_points(window, self.rk4_points, self.COL3)

    def draw_animated_points(self, window: pygame.Surface, points: np.ndarray, col):
        for p in points[:,-1,:]:
            ps = self.geom.transform_coords(p[0], p[1], clip=False)
            if ps is not None:
                pygame.draw.circle(window, col, ps, 10)
        if self.draw_trails:
            for i in range(points.shape[1] - 1):
                for p0, p1 in zip(points[:,i,:], points[:,i+1,:]):
                    ps0 = self.geom.transform_coords(p0[0], p0[1], clip=False)
                    ps1 = self.geom.transform_coords(p1[0], p1[1], clip=False)
                    if ps0 is None or ps1 is None:
                        continue
                    pygame.draw.line(window, col, ps0, ps1, 2)

    def start_animation(self, V_x: str, V_y: str):
        self.steps = 0
        self.in_anim = True
        for i, (e, m, rk4) in enumerate(self.active_ipls):
            if e:
                self.euler_points = np.vstack([self.euler_points, [self.points[i]]])
                self.euler_meta = np.vstack([self.euler_meta, self.meta_data[i,(0,1)]])
            if m:
                self.midpoint_points = np.vstack([self.midpoint_points, [self.points[i]]])
                self.midpoint_meta = np.vstack([self.midpoint_meta, self.meta_data[i,(0,2)]])
            if rk4:
                self.rk4_points = np.vstack([self.rk4_points, [self.points[i]]])
                self.rk4_meta = np.vstack([self.rk4_meta, self.meta_data[i, (0,3)]])
        self.euler_points = self.euler_points[:,np.newaxis,:]
        self.midpoint_points = self.midpoint_points[:,np.newaxis,:]
        self.rk4_points = self.rk4_points[:,np.newaxis,:]

        self.euler_system = System(V_x, V_y)
        self.midpoint_system = System(V_x, V_y)
        self.rk4_system = System(V_x, V_y)

        self.euler_system.set_state(self.euler_points[:,-1,:])
        self.midpoint_system.set_state(self.midpoint_points[:,-1,:])
        self.rk4_system.set_state(self.rk4_points[:,-1,:])

    def stop_animation(self):
        self.steps = 0
        self.in_anim = False
        self.euler_points = np.array([]).reshape(0, 2)
        self.midpoint_points = np.array([]).reshape(0, 2)
        self.rk4_points = np.array([]).reshape(0, 2)
        self.euler_meta = np.array([]).reshape(0, 2)
        self.midpoint_meta = np.array([]).reshape(0, 2)
        self.rk4_meta = np.array([]).reshape(0, 2)
        self.euler_system = None
        self.midpoint_system = None
        self.rk4_system = None

    def step_world(self):
        self.steps += 1
        n_updates = 0

        # euler update with varying N steps
        N, dt = self.euler_meta[:,0], self.euler_meta[:,1]
        to_update = self.steps <= N
        self.euler_solver.step(self.euler_system, dt)
        n_updates += to_update.sum()
        X_curr = self.euler_points[:,-1,:].copy()
        X_new = self.euler_system.get_state()
        X_curr[to_update,:] = X_new[to_update,:]
        self.euler_system.set_state(X_curr)
        self.euler_points = np.hstack([self.euler_points, X_curr[:,np.newaxis,:]])

        # midpoint update with varying N steps
        N, dt = self.midpoint_meta[:,0], self.midpoint_meta[:,1]
        to_update = self.steps <= N
        self.midpoint_solver.step(self.midpoint_system, dt)
        n_updates += to_update.sum()
        X_curr = self.midpoint_points[:,-1,:].copy()
        X_new = self.midpoint_system.get_state()
        X_curr[to_update,:] = X_new[to_update,:]
        self.midpoint_system.set_state(X_curr)
        self.midpoint_points = np.hstack([self.midpoint_points, X_curr[:,np.newaxis,:]])

        # rk4 update with varying N steps
        N, dt = self.rk4_meta[:,0], self.rk4_meta[:,1]
        to_update = self.steps <= N
        self.rk4_solver.step(self.rk4_system, dt)
        n_updates += to_update.sum()
        X_curr = self.rk4_points[:,-1,:].copy()
        X_new = self.rk4_system.get_state()
        X_curr[to_update,:] = X_new[to_update,:]
        self.rk4_system.set_state(X_curr)
        self.rk4_points = np.hstack([self.rk4_points, X_curr[:,np.newaxis,:]])

        if n_updates == 0:
            self.stop_animation()



