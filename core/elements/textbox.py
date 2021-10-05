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
            if event.key == pygame.K_BACKSPACE:
                self.buffer = self.buffer[:-1]
            elif event.key == pygame.K_DELETE:
                self.buffer = ''
            else:
                # TODO validate unicode ranges (pyfunc eval())
                self.buffer += event.unicode
    
    def reset_content(self, val:str = ''):
        self.content = val
        self.buffer = val
    
    def set_content(self):
        self.content = self.buffer

    def get_content(self):
        if self.active:
            return self.buffer
        else:
            return self.content