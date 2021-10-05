import pygame

from core.geom import WindowGeometry

class Grid:

    def __init__(self, grid_color=(220, 255, 255), axes_color=(0, 0, 0)) -> None:
        self.grid_color = grid_color
        self.axes_color = axes_color

    def draw(self, window: pygame.Surface, geom: WindowGeometry) -> None:
        """
        for x in range(geom.gridX[0], geom.gridX[1] + geom.grid_size, geom.grid_size):
            for y in range(geom.gridY[0], geom.gridY[1] + geom.grid_size, geom.grid_size):
                rect = pygame.Rect(x, y, geom.grid_size, geom.grid_size)
                pygame.draw.rect(window, self.grid_color, rect, 1)
        """
        pass
