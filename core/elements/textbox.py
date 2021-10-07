from pygame.constants import K_BACKSPACE, K_DELETE, K_LEFT, K_RIGHT, K_SLASH
import pygame


class TextBox:
    active = False
    COL_INACTIVE = (0, 0, 0)
    COL_ACTIVE = (0, 0, 255)
    COL_TEXT = (40, 40, 40)
    content = ''
    buffer = ''

    def __init__(self) -> None:
        '''needs set_screen_coords before draw'''
        self.txt_font = pygame.font.SysFont('arial', 18)
        pass

    def draw(self, window: pygame.Surface) -> None:
        txt_box = pygame.Rect(self.xs, self.ys, self.W, self.H)
        col = self.COL_ACTIVE if self.active else self.COL_INACTIVE
        pygame.draw.rect(window, col, txt_box, 1)

        ts = self.txt_font.render(self.get_content(), False, self.COL_TEXT)
        window.blit(ts, (self.xs + 4, self.ys + 4))

    def set_screen_coords(self, xs: int, ys: int, W: int, H: int) -> None:
        self.xs = xs
        self.ys = ys
        self.W = W
        self.H = H

    def mouse_in_textbox(self, mouse_xs: int, mouse_ys: int) -> bool:
        return (mouse_xs >= self.xs) and (mouse_xs <= self.xs + self.W) \
            and (mouse_ys >= self.ys) and (mouse_ys <= self.ys + self.H)

    def update_content(self, event: pygame.event.Event):
        if self.active:
            if event.key == K_BACKSPACE:
                l, r = self.buffer.split('|')
                self.buffer = l[:-1] + '|' + r
            elif event.key == K_DELETE:
                self.buffer = '|'
            elif event.key == K_SLASH:  # ingore SLASH (|)
                pass
            elif event.key == K_LEFT:
                l, r = self.buffer.split('|')
                self.buffer = l[:-1] + '|' + l[-1:] + r
            elif event.key == K_RIGHT:
                l, r = self.buffer.split('|')
                self.buffer = l + r[:1] + '|' + r[1:]
            else:
                # TODO validate unicode ranges (pyfunc eval())
                l, r = self.buffer.split('|')
                self.buffer = l + event.unicode + '|' + r

    def reset_content(self, val: str = ''):
        self.content = val
        self.buffer = val

    def activate(self):
        self.active = True
        self.buffer += '|'

    def deactivate(self):
        self.active = False
        self.buffer = self.buffer.replace('|', '')
        self.content = self.buffer

    def get_content(self):
        if self.active:
            return self.buffer
        else:
            return self.content
