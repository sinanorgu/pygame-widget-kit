import pygame
from .UIComponent import *
from functools import partial


class Slider(UIComponent):
    def __init__(
        self,
        pos=(0, 0),
        size=(200, 20),
        min_value=0,
        max_value=100,
        value=None,
        style=None,
        z_index=0,
        color=(200, 200, 200),
        border_color=(120, 120, 120),
        hover_color=(220, 220, 220),
        handle_color=(80, 80, 80),
        handle_hover_color=None,
        handle_border_color=None,
    ):
        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value if value is None else value

        self.size = size

        self.handle_color = handle_color
        self.handle_hover_color = (
            handle_hover_color
            if handle_hover_color is not None
            else tuple(min(c + 30, 255) for c in handle_color)
        )
        self.handle_active_color = tuple(max(c - 40, 0) for c in handle_color)
        self.handle_border_color = handle_border_color

        self.dragging = False
        self.drag_offset = 0
        self.change_function = None

        rect = (pos[0], pos[1], self.size[0], self.size[1])
        super().__init__(rect, style, z_index, color, border_color, hover_color)

        self.handle_width = min(self.rect[2], self.rect[3])
        self.handle_height = self.rect[3]

        self.set_value(self.value)

    def change_bind(self, func, *args):
        self.change_function = partial(func, *args)

    def on_change(self):
        if self.change_function is not None:
            self.change_function()

    def set_value(self, value):
        if self.max_value == self.min_value:
            if self.value != self.min_value:
                self.value = self.min_value
                self.on_change()
            return

        old_value = self.value
        if value < self.min_value:
            value = self.min_value
        elif value > self.max_value:
            value = self.max_value

        self.value = value
        if self.value != old_value:
            self.on_change()

    def get_value(self):
        return self.value

    def _get_track_range(self):
        x = self.absolute_rect[0]
        w = self.rect[2]
        handle_w = self.handle_width
        min_center = x + handle_w / 2
        max_center = x + w - handle_w / 2
        return min_center, max_center

    def _value_to_center(self):
        min_center, max_center = self._get_track_range()
        if max_center <= min_center or self.max_value == self.min_value:
            return min_center

        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        ratio = max(0, min(1, ratio))
        return min_center + ratio * (max_center - min_center)

    def _get_handle_rect(self):
        center_x = self._value_to_center()
        handle_x = int(center_x - self.handle_width / 2)
        handle_y = int(self.absolute_rect[1] + (self.rect[3] - self.handle_height) / 2)
        return pygame.Rect(handle_x, handle_y, self.handle_width, self.handle_height)

    def _set_value_from_mouse(self, mouse_x, use_offset):
        min_center, max_center = self._get_track_range()
        if max_center <= min_center or self.max_value == self.min_value:
            self.set_value(self.min_value)
            return

        center_x = mouse_x - (self.drag_offset if use_offset else 0)
        if center_x < min_center:
            center_x = min_center
        elif center_x > max_center:
            center_x = max_center

        ratio = (center_x - min_center) / (max_center - min_center)
        self.set_value(self.min_value + ratio * (self.max_value - self.min_value))

    def _begin_drag(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        handle_rect = self._get_handle_rect()

        if handle_rect.collidepoint(mouse_x, mouse_y):
            self.drag_offset = mouse_x - handle_rect.centerx
        else:
            self.drag_offset = 0
            self._set_value_from_mouse(mouse_x, use_offset=False)

        self.dragging = True

    def on_click(self, event):
        if not self.visible or not self.enabled:
            return

        if not self.dragging:
            self._set_value_from_mouse(event.pos[0], use_offset=False)

        self.dragging = False
        self.drag_offset = 0
        

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        if self.active and self.enabled:
            if not self.dragging:
                self._begin_drag()
            mouse_x, _ = pygame.mouse.get_pos()
            self._set_value_from_mouse(mouse_x, use_offset=True)
        else:
            self.dragging = False
            self.drag_offset = 0

        super().draw(surface)

        handle_color = self.handle_color
        if not self.enabled:
            handle_color = tuple(c // 2 for c in handle_color)
        elif self.active:
            handle_color = self.handle_active_color
        elif self.hovered:
            handle_color = self.handle_hover_color

        handle_rect = self._get_handle_rect()
        pygame.draw.rect(surface, handle_color, handle_rect, 0)
        if self.handle_border_color:
            pygame.draw.rect(surface, self.handle_border_color, handle_rect, 2)
