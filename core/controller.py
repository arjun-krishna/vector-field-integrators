from typing import List, Tuple
import pygame
import sys
from pygame import mouse

from pygame.constants import K_ESCAPE, K_d, K_i, K_q, K_x
from core.elements.textbox import TextBox

from core.geom import WindowGeometry
from core.world import World

class Controller:
    insert_mode: bool = False
    delete_mode: bool = False
    grabbed_idx: int = None
    anim_mode: bool = False
    integrator: str = None
    grabbed_idx: int = None
    animation_loop: bool = False

    type_mode: bool = False
    text_boxes: List[TextBox] = []
    active_text_box: TextBox = None

    mouse_pos: Tuple[int, int] = None

    def __init__(self, world: World) -> None:
        self.world = world

        self.text_boxes = [TextBox() for i in range(6)]
        # default filled in values
        self.text_boxes[0].reset_content('x*x - y*y - 4')
        self.text_boxes[1].reset_content('2*x*y')
        self.text_boxes[2].reset_content('-3')
        self.text_boxes[3].reset_content('3')
        self.text_boxes[4].reset_content('-3')
        self.text_boxes[5].reset_content('3')


    def activate_type_mode(self, text_box: TextBox) -> None:
        self.active_text_box = text_box
        self.active_text_box.activate()
        self.type_mode = True
        self.insert_mode = False
        self.delete_mode = False
        self.grabbed_idx = None

    def deactivate_type_mode(self) -> None:
        if self.type_mode:
            self.type_mode = False
            self.active_text_box.deactivate()
            self.active_text_box = None

    def toggle_insert_mode(self) -> None:
        self.insert_mode = not self.insert_mode
        self.delete_mode = False
        self.type_mode = False
        self.grabbed_idx = None

    def toggle_delete_mode(self) -> None:
        self.delete_mode = not self.delete_mode
        self.insert_mode = False
        self.grabbed_idx = None

    def clear_world(self) -> None:
        self.world.clear()
        self.insert_mode = False
        self.delete_mode = False
        self.grabbed_idx = None

    def checkRange(self, mos_pos, mx, Mx, my, My):
        return ((mos_pos[0] >= mx and mos_pos[0] <= Mx) and (mos_pos[1] >= my and mos_pos[1] <= My))

    def event_handler(self, geom: WindowGeometry, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            sys.exit()

        mouse_pos = self.get_mouse_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.insert_mode:
                self.world.add_point(mouse_pos)
            elif self.delete_mode:
                di = self.world.get_closest_point_idx(mouse_pos)
                if di is not None:
                    self.world.delete_point(di)
            else: # drag
                self.grabbed_idx = self.world.get_closest_point_idx(mouse_pos)

            # insert box (9, 254, 60, 30)
            if self.checkRange(mouse_pos, 9, 69, 254, 284):
                self.toggle_insert_mode()
            # delete box (89, 254, 60, 30)
            if self.checkRange(mouse_pos, 89, 149, 254, 284):
                self.toggle_delete_mode()
            # clear box (169, 254, 60, 30)
            if self.checkRange(mouse_pos, 169, 229, 254, 284):
                self.clear_world()
            
            for text_box in self.text_boxes:
                if text_box.mouse_in_textbox(mouse_pos[0], mouse_pos[1]):
                    self.deactivate_type_mode()
                    self.activate_type_mode(text_box)
                    break
            
        

        if event.type == pygame.MOUSEBUTTONUP:
            self.grabbed_idx = None

        if event.type == pygame.MOUSEMOTION:
            if self.grabbed_idx is not None:
                if pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_HAND:                
                    pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.world.update_point(self.grabbed_idx, mouse_pos)
            else:
                if pygame.mouse.get_cursor() == pygame.SYSTEM_CURSOR_HAND:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
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
            if event.key == K_i:
                self.toggle_insert_mode()
            if event.key == K_x:
                self.toggle_delete_mode()
            if event.key == K_d:
                self.clear_world()
            if event.key == K_ESCAPE:
                self.insert_mode = False
                self.delete_mode = False
                if self.type_mode:
                    self.deactivate_type_mode()
                self.grabbed_idx = None

    def get_mouse_pos(self) -> Tuple[int, int]:
        return pygame.mouse.get_pos()

    def get_Vx(self) -> str:
        return self.text_boxes[0].content
    
    def get_Vy(self) -> str:
        return self.text_boxes[1].content

    def get_Xrange(self) -> Tuple[float, float]:
        try:
            return (float(self.text_boxes[2].content), float(self.text_boxes[3].content))
        except Exception:
            return (-3, 3)

    def get_Yrange(self) -> Tuple[float, float]:
        try:
            return (float(self.text_boxes[4].content), float(self.text_boxes[5].content))
        except Exception:
            return (-3, 3)

    def draw(self, window: pygame.Surface, geom: WindowGeometry):
        mx, my = self.get_mouse_pos()
        if geom.on_grid(mx, my):
            if self.grabbed_idx is None and pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_CROSSHAIR:
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        else:
            if pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_ARROW:
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
        BLACK = (0, 0, 0)
        GREEN = (0, 255, 0)
        RED = (255, 0, 0)

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
        SPACING_Y += 3 * LR_MARGIN + 10

        # seperator
        pygame.draw.lines(window, BLACK, False, [(LR_MARGIN, SPACING_Y), (geom.controller_width - LR_MARGIN, SPACING_Y)], 2)
        SPACING_Y += 3

        # Grid
        ts = font_h1.render("Grid Settings", False, BLACK)
        window.blit(ts, (LR_MARGIN, SPACING_Y))
        SPACING_Y += 3.5 * LR_MARGIN

        ts = font_h2.render("x (min)", False, BLACK)
        window.blit(ts, (LR_MARGIN, SPACING_Y + 5))
        self.text_boxes[2].set_screen_coords(LR_MARGIN + 45, SPACING_Y, 85, 30)
        self.text_boxes[2].draw(window)

        ts = font_h2.render("x (max)", False, BLACK)
        window.blit(ts, (LR_MARGIN + 140, SPACING_Y + 5))
        self.text_boxes[3].set_screen_coords(LR_MARGIN + 195, SPACING_Y, 85, 30)
        self.text_boxes[3].draw(window)

        SPACING_Y += 40

        ts = font_h2.render("y (min)", False, BLACK)
        window.blit(ts, (LR_MARGIN, SPACING_Y + 5))
        self.text_boxes[4].set_screen_coords(LR_MARGIN + 45, SPACING_Y, 85, 30)
        self.text_boxes[4].draw(window)

        ts = font_h2.render("y (max)", False, BLACK)
        window.blit(ts, (LR_MARGIN + 140, SPACING_Y + 5))
        self.text_boxes[5].set_screen_coords(LR_MARGIN + 195, SPACING_Y, 85, 30)
        self.text_boxes[5].draw(window)

        SPACING_Y += 40

        # seperator
        pygame.draw.lines(window, BLACK, False, [(LR_MARGIN, SPACING_Y), (geom.controller_width - LR_MARGIN, SPACING_Y)], 2)
        SPACING_Y += 3

        # mode indicator
        window.blit(font_h1.render("Modes", False, BLACK), (LR_MARGIN, SPACING_Y))
        SPACING_Y += 3.5 * LR_MARGIN

        # insert rect
        m_rect = pygame.Rect(LR_MARGIN, SPACING_Y, 60, 30) # (9, 254, 60, 30)
        col = GREEN if self.insert_mode else BLACK
        pygame.draw.rect(window, col, m_rect, 1)
        window.blit(font_h2.render("INSERT", False, col), (LR_MARGIN + 5, SPACING_Y + 5))

        # delete rect
        m_rect = pygame.Rect(LR_MARGIN + 80, SPACING_Y, 60, 30) # (89, 254, 60, 30)
        col = RED if self.delete_mode else BLACK
        pygame.draw.rect(window, col, m_rect, 1)
        window.blit(font_h2.render("DELETE", False, col), (LR_MARGIN + 85, SPACING_Y + 5))

        # clear rect
        m_rect = pygame.Rect(LR_MARGIN + 160, SPACING_Y, 60, 30) # (169, 254, 60, 30)
        pygame.draw.rect(window, BLACK, m_rect, 1)
        window.blit(font_h2.render("CLEAR", False, BLACK), (LR_MARGIN + 165, SPACING_Y + 5))

        SPACING_Y += 40

        # seperator
        pygame.draw.lines(window, BLACK, False, [(LR_MARGIN, SPACING_Y), (geom.controller_width - LR_MARGIN, SPACING_Y)], 2)
        SPACING_Y += 3


        # m_rect = pygame.Rect(100, 255, 80, 40)
        # col = ACTIVE_COLOR if params['delete_mode'] else INACTIVE_COLOR
        # pygame.draw.rect(window, col, m_rect, 0)
        # window.blit(cmd_font.render("Delete", False, WINDOW_BACKGROUND), (113, 260))

