from typing import List, Tuple
import pygame
import sys

from pygame.constants import K_ESCAPE, K_q
from core.elements.textbox import TextBox

from core.geom import WindowGeometry

class Controller:
    insert_mode: bool = False
    delete_mode: bool = False
    anim_mode: bool = False
    integrator: str = None
    grabbed_idx: int = None
    animation_loop: bool = False

    type_mode: bool = False
    text_boxes: List[TextBox] = []
    active_text_box: TextBox = None

    mouse_pos: Tuple[int, int] = None

    def __init__(self) -> None:
        self.text_boxes = [TextBox() for i in range(2)]
        # default filled in values
        self.text_boxes[0].reset_content('x*x - y*y - 4')
        self.text_boxes[1].reset_content('2*x*y')

    def activate_type_mode(self, text_box: TextBox) -> None:
        self.active_text_box = text_box
        self.active_text_box.activate()
        self.type_mode = True

    def deactivate_type_mode(self) -> None:
        if self.type_mode:
            self.type_mode = False
            self.active_text_box.deactivate()
            self.active_text_box = None

    def event_handler(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            for text_box in self.text_boxes:
                if text_box.mouse_in_textbox(self.mouse_pos[0], self.mouse_pos[1]):
                    self.deactivate_type_mode()
                    self.activate_type_mode(text_box)
                    break

        # if type mode is active
        if event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
            self.deactivate_type_mode()

        if event.type == pygame.KEYDOWN and self.type_mode:
            if event.key == pygame.K_RETURN:
                self.deactivate_type_mode()
            else:
                self.active_text_box.update_content(event)
        
        if event.type == pygame.KEYDOWN and not self.type_mode:
            if event.key == K_q:
                sys.exit()

    def get_mouse_pos(self) -> Tuple[int, int]:
        return self.mouse_pos

    def get_Vx(self) -> str:
        return self.text_boxes[0].content
    
    def get_Vy(self) -> str:
        return self.text_boxes[1].content

    def draw(self, window: pygame.Surface, geom: WindowGeometry):
        BLACK = (0, 0, 0)

        LR_MARGIN = int(0.0333 * geom.controller_width)
        SPACING_Y = LR_MARGIN

        font_h1 = pygame.font.SysFont('arialblack', 18)
        font_h2 = pygame.font.SysFont('arial', 16)
        font_p = pygame.font.SysFont('arial', 14)

        # Vector Field
        ts = font_h1.render("Vector Field", False, BLACK)
        window.blit(ts, (LR_MARGIN, SPACING_Y))
        SPACING_Y += 3 * LR_MARGIN

        # Vx(x, y)
        ts = font_h2.render("Vx(x, y)", False, BLACK)
        window.blit(ts, (LR_MARGIN, SPACING_Y + 7))
        self.text_boxes[0].set_screen_coords(LR_MARGIN + 55, SPACING_Y, geom.controller_width - 2 * LR_MARGIN - 55, 30)
        self.text_boxes[0].draw(window)
        SPACING_Y += 3 * LR_MARGIN + 5

        # Vy(x, y)
        ts = font_h2.render("Vy(x, y)", False, BLACK)
        window.blit(ts, (LR_MARGIN, SPACING_Y + 7))
        self.text_boxes[1].set_screen_coords(LR_MARGIN + 55, SPACING_Y, geom.controller_width - 2*LR_MARGIN - 55, 30)
        self.text_boxes[1].draw(window)
        SPACING_Y += 3 * LR_MARGIN + 5

        # seperator
        pygame.draw.lines(window, BLACK, False, [(LR_MARGIN, SPACING_Y), (geom.controller_width - LR_MARGIN, SPACING_Y)], 2)
        SPACING_Y += 3

        # Grid
        ts = font_h1.render("Grid Settings", False, BLACK)
        window.blit(ts, (LR_MARGIN, SPACING_Y))
        SPACING_Y += 3 * LR_MARGIN