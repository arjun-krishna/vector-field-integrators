import pygame
import numpy as np

from core.geom import WindowGeometry


class Grid:

    def __init__(self, grid_color=(220, 255, 255), axes_color=(0, 0, 0)) -> None:
        self.grid_color = grid_color
        self.axes_color = axes_color
        self.font = pygame.font.SysFont('arial', 14)

    def draw(self, window: pygame.Surface, geom: WindowGeometry) -> None:
        """
        for x in range(geom.gridX[0], geom.gridX[1] + geom.grid_size, geom.grid_size):
            for y in range(geom.gridY[0], geom.gridY[1] + geom.grid_size, geom.grid_size):
                rect = pygame.Rect(x, y, geom.grid_size, geom.grid_size)
                pygame.draw.rect(window, self.grid_color, rect, 1)
        """
        origin = geom.transform_coords(0, 0, clip=False)
        xs_min, xs_max = geom.gridX
        ys_min, ys_max = geom.gridY

        xc, yc = None, None

        if origin is not None:
            xo, yo = origin
            xc, yc = xo, yo
            pygame.draw.lines(window, self.axes_color, False, [(xs_min, yo), (xs_max, yo)], 2)
            pygame.draw.lines(window, self.axes_color, False, [(xo, ys_min), (xo, ys_max)], 2)
        else:
            xc, yc = xs_min, ys_min
            # draw on the edges with annotation of x, y
            pygame.draw.lines(window, self.axes_color, False, [(xs_min, ys_min), (xs_max, ys_min)], 2)
            pygame.draw.lines(window, self.axes_color, False, [(xs_min, ys_min), (xs_min, ys_max)], 2)

        X = np.linspace(geom.xrange[0], geom.xrange[1], 15)
        XS = [geom.transform_coords(x, yc)[0] for x in X]
        X = np.around(X, decimals=1)
        for x, xs in zip(X, XS):
            pygame.draw.lines(window, self.axes_color, False, [(xs, yc+5), (xs, yc-5)], 1) 
            ts = self.font.render(f"{x}", False, self.axes_color)
            window.blit(ts, (xs-8, yc+5))
        
        Y = np.linspace(geom.yrange[0], geom.yrange[1], 15)
        YS = [geom.transform_coords(xc, y)[1] for y in Y]
        Y = np.around(Y, decimals=1)
        for y, ys in zip(Y, YS):
            pygame.draw.lines(window, self.axes_color, False, [(xc+5, ys), (xc-5, ys)], 1) 
            ts = self.font.render(f"{y}", False, self.axes_color)
            window.blit(ts, (xc+5, ys-8))
        