from core.geom import WindowGeometry
import numpy as np
import pygame


class Quiver:
    COLOR = (0, 0, 255)

    def __init__(self) -> None:
        pass

    def draw(self, window: pygame.Surface, geom: WindowGeometry, vx_str: str, vy_str: str) -> None:
        xx, yy = geom.meshgrid()

        @np.vectorize
        def Vx(x, y):
            try:
                return eval(vx_str)
            except Exception:
                return 0 * x

        @np.vectorize
        def Vy(x, y):
            try:
                return eval(vy_str)
            except Exception:
                return 0 * y

        V_x = Vx(xx, yy)
        V_y = Vy(xx, yy)
        mV = np.sqrt(V_x ** 2 + V_y ** 2)
        m = mV.min()
        M = mV.max()

        D = xx[1, 0] - xx[0, 0]

        if m != 0:
            V_x = V_x / mV
            V_y = V_y / mV
            if (m == M):
                S = 0.99*D
            else:
                S = 0.1*D + 0.89*D*(mV - m) / (M - m)

            V_x = V_x * S
            V_y = V_y * S

            for (i, x) in enumerate(xx[:, 0][1:-1]):
                for (j, y) in enumerate(yy[0, :]):
                    # TODO use scaling on the co-ordinate rather screen scaling
                    # and transform from co-ordinates to screen co-ordinates
                    vx, vy = (V_x[i+1, j], V_y[i+1, j])
                    px, py = -0.1*vy, 0.1*vx
                    arrow = [
                        (x, y),
                        (x + 0.9*vx, y + 0.9*vy),
                        (x + 0.9*vx + px, y + 0.9*vy + py),
                        (x + vx, y + vy),
                        (x + 0.9*vx - px, y + 0.9*vy - py),
                        (x + 0.9*vx, y + 0.9*vy)
                    ]
                    arrow_s = [geom.transform_coords(x, y) for (x, y) in arrow]
                    pygame.draw.polygon(window, self.COLOR, arrow_s, 1)
