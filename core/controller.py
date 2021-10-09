from typing import List, Tuple
from numpy.lib.twodim_base import triu_indices
import pygame
import sys

from pygame.constants import K_ESCAPE, K_SPACE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, QUIT, K_d, K_i, K_q, K_x
from core.elements.textbox import TextBox

from core.geom import WindowGeometry
from core.world import World


class Controller:
    insert_mode: bool = False
    delete_mode: bool = False
    animate_mode: bool = False

    grabbed_idx: int = None

    type_mode: bool = False
    text_boxes: List[TextBox] = []
    active_text_box: TextBox = None
    active_text_box_id: int = None

    mouse_pos: Tuple[int, int] = None

    def __init__(self, world: World) -> None:
        self.world = world

        self.text_boxes = [TextBox() for i in range(10)]
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
            if self.world.selected_idx is not None and self.active_text_box_id > 5:
                x = float(self.active_text_box.content) if self.active_text_box.content else 0
                self.world.update_meta_data(self.world.selected_idx, self.active_text_box_id - 6, x)
            self.active_text_box = None
            self.active_text_box_id = None
    
    def start_anim(self) -> None:
        self.animate_mode = True
        self.insert_mode = False
        self.delete_mode = False
        self.type_mode = False
        self.grabbed_idx = None
        self.world.selected_idx = None
        self.clearInterpolatorConfig()
        self.world.start_animation(self.get_Vx(), self.get_Vy())

    def stop_anim(self) -> None:
        self.animate_mode = False
        self.world.stop_animation()

    def toggle_insert_mode(self) -> None:
        self.insert_mode = not self.insert_mode
        self.delete_mode = False
        if self.animate_mode:
            self.stop_anim()
        self.type_mode = False
        self.grabbed_idx = None
        self.world.selected_idx = None
        self.clearInterpolatorConfig()

    def toggle_delete_mode(self) -> None:
        self.delete_mode = not self.delete_mode
        self.insert_mode = False
        if self.animate_mode:
            self.stop_anim()
        self.grabbed_idx = None
        self.world.selected_idx = None
        self.clearInterpolatorConfig()

    def clear_world(self) -> None:
        self.world.clear()
        self.insert_mode = False
        self.delete_mode = False
        if self.animate_mode:
            self.stop_anim()
        self.grabbed_idx = None
        self.world.selected_idx = None
        self.clearInterpolatorConfig()

    def clearInterpolatorConfig(self):
        for i in range(6, 10):
            self.text_boxes[i].reset_content('')

    def checkRange(self, mos_pos, mx, Mx, my, My):
        return ((mos_pos[0] >= mx and mos_pos[0] <= Mx) and (mos_pos[1] >= my and mos_pos[1] <= My))

    def event_handler(self, geom: WindowGeometry, event: pygame.event.Event) -> None:
        if event.type == QUIT:
            sys.exit()

        mouse_pos = self.get_mouse_pos()

        if event.type == MOUSEBUTTONDOWN and event.button == 1:  # left button
            if self.insert_mode:
                self.world.add_point(mouse_pos)
            elif self.delete_mode:
                di = self.world.get_closest_point_idx(mouse_pos)
                if di is not None:
                    self.world.delete_point(di)
            elif self.type_mode:
                if sum([tb.mouse_in_textbox(mouse_pos[0], mouse_pos[1]) for tb in self.text_boxes]) == 0:
                    self.deactivate_type_mode()
            else:  # drag
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

            # selection id toggle integrator
            if self.world.selected_idx is not None:
                if self.checkRange(mouse_pos, 9, 179, 418.5, 458.5):
                    self.world.toggle_integrator(0)
                if self.checkRange(mouse_pos, 9, 179, 463.5, 503.5):
                    self.world.toggle_integrator(1)
                if self.checkRange(mouse_pos, 9, 179, 508.5, 548.5):
                    self.world.toggle_integrator(2)

            for idx, text_box in enumerate(self.text_boxes[:6]):
                if text_box.mouse_in_textbox(mouse_pos[0], mouse_pos[1]):
                    self.deactivate_type_mode()
                    self.active_text_box_id = idx
                    self.activate_type_mode(text_box)
                    break

            if self.world.selected_idx is not None:
                for idx, text_box in enumerate(self.text_boxes[6:]):
                    if text_box.mouse_in_textbox(mouse_pos[0], mouse_pos[1]):
                        self.deactivate_type_mode()
                        self.active_text_box_id = idx + 6
                        self.activate_type_mode(text_box)
                        break

        if event.type == MOUSEBUTTONDOWN and event.button == 3:  # right button
            if not self.type_mode and not self.insert_mode and not self.delete_mode and not self.animate_mode:
                self.world.selected_idx = self.world.get_closest_point_idx(mouse_pos)
                if self.world.selected_idx is not None:
                    meta_data = self.world.meta_data[self.world.selected_idx,:]
                    for i in range(4):
                        content = str(int(meta_data[i])) if i == 0 else str(meta_data[i])
                        self.text_boxes[i+6].reset_content(content)
                else:
                    self.clearInterpolatorConfig()

        if event.type == MOUSEBUTTONUP:  # release grabbed point
            self.grabbed_idx = None

        if event.type == MOUSEMOTION:
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
            if event.key == K_SPACE:
                if not self.animate_mode:
                    self.start_anim()
                else:
                    self.stop_anim()
            if event.key == K_ESCAPE:
                self.insert_mode = False
                self.delete_mode = False
                if self.type_mode:
                    self.deactivate_type_mode()
                if self.animate_mode:
                    self.stop_anim()
                self.grabbed_idx = None
                self.world.selected_idx = None
                self.clearInterpolatorConfig()

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
        GREEN = (50, 168, 107)
        RED = (255, 0, 0)

        LR_MARGIN = int(0.0333 * geom.controller_width)
        SPACING_Y = LR_MARGIN

        font_h1 = pygame.font.SysFont('arial', 18, bold=True)
        font_h2 = pygame.font.SysFont('arial', 16)
        font_p = pygame.font.SysFont('georgia', 15, italic=True)

        # Vector Field
        ts = font_h1.render("Vector Field", False, BLACK)
        window.blit(ts, (LR_MARGIN, SPACING_Y))
        SPACING_Y += 3.5 * LR_MARGIN

        # Vx(x, y)
        ts = font_h2.render("Vx(x, y)", False, BLACK)
        window.blit(ts, (LR_MARGIN, SPACING_Y + 7))
        self.text_boxes[0].set_screen_coords(
            LR_MARGIN + 55, SPACING_Y, geom.controller_width - 2 * LR_MARGIN - 55, 30)
        self.text_boxes[0].draw(window)
        SPACING_Y += 3 * LR_MARGIN + 5

        # Vy(x, y)
        ts = font_h2.render("Vy(x, y)", False, BLACK)
        window.blit(ts, (LR_MARGIN, SPACING_Y + 7))
        self.text_boxes[1].set_screen_coords(
            LR_MARGIN + 55, SPACING_Y, geom.controller_width - 2*LR_MARGIN - 55, 30)
        self.text_boxes[1].draw(window)
        SPACING_Y += 3 * LR_MARGIN + 10

        # seperator
        pygame.draw.lines(window, BLACK, False, [
                          (LR_MARGIN, SPACING_Y), (geom.controller_width - LR_MARGIN, SPACING_Y)], 2)
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
        self.text_boxes[3].set_screen_coords(
            LR_MARGIN + 195, SPACING_Y, 85, 30)
        self.text_boxes[3].draw(window)

        SPACING_Y += 40

        ts = font_h2.render("y (min)", False, BLACK)
        window.blit(ts, (LR_MARGIN, SPACING_Y + 5))
        self.text_boxes[4].set_screen_coords(LR_MARGIN + 45, SPACING_Y, 85, 30)
        self.text_boxes[4].draw(window)

        ts = font_h2.render("y (max)", False, BLACK)
        window.blit(ts, (LR_MARGIN + 140, SPACING_Y + 5))
        self.text_boxes[5].set_screen_coords(
            LR_MARGIN + 195, SPACING_Y, 85, 30)
        self.text_boxes[5].draw(window)

        SPACING_Y += 40

        # seperator
        pygame.draw.lines(window, BLACK, False, [
                          (LR_MARGIN, SPACING_Y), (geom.controller_width - LR_MARGIN, SPACING_Y)], 2)
        SPACING_Y += 3

        # mode indicator
        window.blit(font_h1.render("Modes", False, BLACK),
                    (LR_MARGIN, SPACING_Y))
        SPACING_Y += 3.5 * LR_MARGIN

        # insert rect
        m_rect = pygame.Rect(LR_MARGIN, SPACING_Y, 60, 30)  # (9, 254, 60, 30)
        col = GREEN if self.insert_mode else BLACK
        pygame.draw.rect(window, col, m_rect, 1)
        window.blit(font_h2.render("INSERT", False, col),
                    (LR_MARGIN + 5, SPACING_Y + 5))

        # delete rect
        m_rect = pygame.Rect(LR_MARGIN + 80, SPACING_Y,
                             60, 30)  # (89, 254, 60, 30)
        col = RED if self.delete_mode else BLACK
        pygame.draw.rect(window, col, m_rect, 1)
        window.blit(font_h2.render("DELETE", False, col),
                    (LR_MARGIN + 85, SPACING_Y + 5))

        # clear rect
        m_rect = pygame.Rect(LR_MARGIN + 160, SPACING_Y,
                             60, 30)  # (169, 254, 60, 30)
        pygame.draw.rect(window, BLACK, m_rect, 1)
        window.blit(font_h2.render("CLEAR", False, BLACK),
                    (LR_MARGIN + 165, SPACING_Y + 5))

        SPACING_Y += 40

        # seperator
        pygame.draw.lines(window, BLACK, False, [
                          (LR_MARGIN, SPACING_Y), (geom.controller_width - LR_MARGIN, SPACING_Y)], 2)
        SPACING_Y += 3

        # Integrators config
        window.blit(font_h1.render("Integrator Config", False, BLACK),
                    (LR_MARGIN, SPACING_Y))
        SPACING_Y += 3 * LR_MARGIN
        window.blit(font_p.render("Right-click a point to start configuring", False, BLACK), (LR_MARGIN, SPACING_Y))
        SPACING_Y += 30
        if self.world.selected_idx is not None:
            point_str = "P" + str(self.world.selected_idx)
            aipls = self.world.active_ipls[self.world.selected_idx,:]
            cols = [GREEN if c else BLACK for c in aipls]
        else:
            point_str = ""
            aipls = [False] * 3
            cols = [BLACK] * 3
        window.blit(font_h2.render("Selected Point =  " + point_str, False, BLACK),
                    (LR_MARGIN, SPACING_Y))
        m_rect = pygame.Rect(LR_MARGIN + 100, SPACING_Y, 50, 20)
        pygame.draw.rect(window, BLACK, m_rect, 1)
        SPACING_Y += 25
        window.blit(font_h2.render("n steps = ", False, BLACK),
                    (LR_MARGIN, SPACING_Y + 5))
        self.text_boxes[6].set_screen_coords(
            LR_MARGIN + 60, SPACING_Y, geom.controller_width - 2 * LR_MARGIN - 70, 30)
        self.text_boxes[6].draw(window)
        SPACING_Y += 35
        # 418.5
        m_rect = pygame.Rect(LR_MARGIN, SPACING_Y,
                             geom.controller_width - 2 * LR_MARGIN - 10, 40)
        pygame.draw.rect(window, cols[0], m_rect, 1)
        window.blit(font_h2.render("Explicit Euler", False, cols[0]),
                    (LR_MARGIN + 10, SPACING_Y + 10))
        window.blit(font_h2.render("h", False, BLACK),
                    (LR_MARGIN + 155, SPACING_Y + 10))
        self.text_boxes[7].set_screen_coords(
            LR_MARGIN + 170, SPACING_Y + 5, 100, 30)
        self.text_boxes[7].draw(window)
        SPACING_Y += 45

        # 463.5
        m_rect = pygame.Rect(LR_MARGIN, SPACING_Y,
                             geom.controller_width - 2 * LR_MARGIN - 10, 40)
        pygame.draw.rect(window, cols[1], m_rect, 1)
        window.blit(font_h2.render("Midpoint Method", False, cols[1]),
                    (LR_MARGIN + 10, SPACING_Y + 10))
        window.blit(font_h2.render("h", False, BLACK),
                    (LR_MARGIN + 155, SPACING_Y + 10))
        self.text_boxes[8].set_screen_coords(
            LR_MARGIN + 170, SPACING_Y + 5, 100, 30)
        self.text_boxes[8].draw(window)
        SPACING_Y += 45

        # 508.5
        m_rect = pygame.Rect(LR_MARGIN, SPACING_Y,
                             geom.controller_width - 2 * LR_MARGIN - 10, 40)
        pygame.draw.rect(window, cols[2], m_rect, 1)
        window.blit(font_h2.render("RK4", False, cols[2]),
                    (LR_MARGIN + 10, SPACING_Y + 10))
        window.blit(font_h2.render("h", False, BLACK),
                    (LR_MARGIN + 155, SPACING_Y + 10))
        self.text_boxes[9].set_screen_coords(
            LR_MARGIN + 170, SPACING_Y + 5, 100, 30)
        self.text_boxes[9].draw(window)
        SPACING_Y += 45

        # seperator
        pygame.draw.lines(window, BLACK, False, [
                          (LR_MARGIN, SPACING_Y), (geom.controller_width - LR_MARGIN, SPACING_Y)], 2)
        SPACING_Y += 3

        # RIGHT Pane World selector
        LR_MARGIN = geom.pane2 + 10
        SPACING_Y = 10
        pygame.draw.lines(window, BLACK, False, [
                          (LR_MARGIN, 0), (LR_MARGIN, geom.window_size[1])], 2)
        LR_MARGIN += 10
        window.blit(font_h1.render("Points", False, BLACK),
                    (LR_MARGIN, SPACING_Y))
        SPACING_Y += 30
        pygame.draw.lines(window, BLACK, False, [
                          (LR_MARGIN - 10, SPACING_Y), (geom.window_size[0], SPACING_Y)])

        
