import pygame
import pygame.gfxdraw
from functools import partial
from .UIComponent import UIComponent


class ToggleButton(UIComponent):
    def __init__(
        self,
        pos=(0, 0),
        size=(85, 40),
        state=False,
        z_index=0,
        off_color=(205, 205, 205),
        on_gradient_start=(102, 225, 182),
        on_gradient_end=(99, 149, 255),
        knob_color=(245, 245, 245),
        knob_shadow_color=(70, 70, 70),
        border_color=None,
    ):
        rect = (pos[0], pos[1], size[0], size[1])
        super().__init__(rect=rect, style=None, z_index=z_index, color=off_color, border_color=border_color, hover_color=None)

        self.state = bool(state)

        self.off_color = off_color
        self.on_gradient_start = on_gradient_start
        self.on_gradient_end = on_gradient_end
        self.knob_color = knob_color
        self.knob_shadow_color = knob_shadow_color

        self._toggle_callback = None

    def bind_on_toggle(self, func, *args):
        self._toggle_callback = partial(func, *args)

    def set_state(self, value: bool):
        next_state = bool(value)
        if self.state != next_state:
            self.state = next_state
            if self._toggle_callback is not None:
                self._toggle_callback()

    def toggle(self):
        self.set_state(not self.state)

    def get_state(self):
        return self.state

    def on_click(self, event):
        if not self.visible or not self.enabled:
            return
        self.toggle()

    def _draw_horizontal_gradient(self, surface, rect: pygame.Rect, start_color, end_color, border_radius):
        gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        width = max(1, rect.width - 1)
        for x in range(rect.width):
            ratio = x / width
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            pygame.draw.line(gradient_surface, (r, g, b), (x, 0), (x, rect.height))

        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, rect.width, rect.height), border_radius=border_radius)
        gradient_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(gradient_surface, rect.topleft)

    def _draw_aa_circle(self, surface: pygame.Surface, center_x: int, center_y: int, radius: int, color):
        if radius <= 0:
            return
        pygame.gfxdraw.filled_circle(surface, center_x, center_y, radius, color)
        pygame.gfxdraw.aacircle(surface, center_x, center_y, radius, color)

    def _draw_soft_shadow(self, surface: pygame.Surface, center_x: int, center_y: int, radius: int):
        shadow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        local_cx = shadow_surface.get_width() // 2
        local_cy = shadow_surface.get_height() // 2

        shadow_layers = [
            (radius + 5, 24),
            (radius + 3, 38),
            (radius + 1, 56),
            (radius, 72),
        ]

        for layer_radius, alpha in shadow_layers:
            shadow_color = (
                self.knob_shadow_color[0],
                self.knob_shadow_color[1],
                self.knob_shadow_color[2],
                alpha,
            )
            self._draw_aa_circle(shadow_surface, local_cx, local_cy, layer_radius, shadow_color)

        blit_x = center_x - local_cx
        blit_y = center_y - local_cy
        surface.blit(shadow_surface, (blit_x, blit_y))

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        track_rect = pygame.Rect(self.absolute_rect)
        border_radius = track_rect.height // 2

        if self.state:
            self._draw_horizontal_gradient(
                surface,
                track_rect,
                self.on_gradient_start,
                self.on_gradient_end,
                border_radius,
            )
        else:
            pygame.draw.rect(surface, self.off_color, track_rect, border_radius=border_radius)

        knob_margin = max(3, track_rect.height // 14)
        knob_radius = track_rect.height // 2 - knob_margin

        if self.state:
            knob_center_x = track_rect.right - knob_margin - knob_radius
        else:
            knob_center_x = track_rect.left + knob_margin + knob_radius

        knob_center_y = track_rect.centery

        shadow_offset_x = 2 if self.state else 1
        shadow_offset_y = 4
        self._draw_soft_shadow(
            surface,
            knob_center_x + shadow_offset_x,
            knob_center_y + shadow_offset_y,
            knob_radius,
        )

        self._draw_aa_circle(surface, knob_center_x, knob_center_y, knob_radius, self.knob_color)

        if self.border_color:
            pygame.draw.rect(surface, self.border_color, track_rect, 2, border_radius=border_radius)
