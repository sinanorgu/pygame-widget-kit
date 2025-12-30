import pygame
from .UIComponent import *


class TextArea(UIComponent):
    def __init__(
        self,
        rect,
        text_str="",
        font_size=25,
        font_type="Veranda",
        text_color: tuple[int, int, int] = (127, 127, 127),
        bg_color=None,
        hover_color=None,
        padding=6,
        line_spacing=0,
        max_chars_per_line=None,
        style=None,
        z_index=0,
        border_color=None,
    ):
        self.font_size = font_size
        self.font_type = font_type
        self.font = pygame.font.SysFont(self.font_type, self.font_size)

        self.text_str = text_str
        self.text_color = text_color
        self.padding = padding
        self.line_spacing = line_spacing
        self.max_chars_per_line = max_chars_per_line

        super().__init__(rect, style, z_index, bg_color, border_color, hover_color)

        self._rebuild_lines()

    def _wrap_line(self, line):
        if self.max_chars_per_line is None or self.max_chars_per_line <= 0:
            return [line]

        words = line.split(" ")
        if not words:
            return [line]

        wrapped = []
        current = ""

        for word in words:
            if current == "":
                if len(word) > self.max_chars_per_line:
                    wrapped.append(word)
                else:
                    current = word
                continue

            candidate_len = len(current) + 1 + len(word)
            if candidate_len <= self.max_chars_per_line:
                current = f"{current} {word}"
            else:
                wrapped.append(current)
                if len(word) > self.max_chars_per_line:
                    wrapped.append(word)
                    current = ""
                else:
                    current = word

        if current != "":
            wrapped.append(current)

        return wrapped

    def _rebuild_lines(self):
        raw_lines = self.text_str.split("\n")
        self.lines = []
        for raw_line in raw_lines:
            if raw_line == "":
                self.lines.append("")
                continue
            self.lines.extend(self._wrap_line(raw_line))
        self.line_height = self.font.get_linesize()
        self.line_renders = [
            self.font.render(line, True, self.text_color, None) for line in self.lines
        ]

    def set_text(self, new_text_str):
        self.text_str = new_text_str
        self._rebuild_lines()

    def update_font_size(self, new_size):
        self.font_size = new_size
        self.font = pygame.font.SysFont(self.font_type, self.font_size)
        self._rebuild_lines()

    def update_font_type(self, new_type):
        self.font_type = new_type
        self.font = pygame.font.SysFont(self.font_type, self.font_size)
        self._rebuild_lines()

    def draw(self, surface):
        if not self.visible:
            return

        super().draw(surface)

        if not self.lines:
            return

        color = self.text_color
        if not self.enabled:
            color = tuple(c // 2 for c in color)

        x = self.absolute_rect[0] + self.padding
        y = self.absolute_rect[1] + self.padding
        step = self.line_height + self.line_spacing

        for i, line in enumerate(self.lines):
            if color == self.text_color:
                render = self.line_renders[i]
            else:
                render = self.font.render(line, True, color, None)
            surface.blit(render, (x, y + i * step))
