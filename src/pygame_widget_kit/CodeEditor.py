import keyword
import re
from dataclasses import dataclass

import pygame

from .UIComponent import UIComponent
from .TextInput import ALLOW_ALL_CHARS, TextInput


@dataclass(frozen=True)
class HighlightStyle:
    color: tuple[int, int, int]
    bold: bool = False
    italic: bool = False


class CodeEditor(TextInput):
    def __init__(
        self,
        rect,
        initial_text="",
        keyword_styles=None,
        token_styles=None,
        default_style=None,
        allow_multiline=True,
        allowed_char_mode: int = ALLOW_ALL_CHARS,
        text_color=(20, 20, 20),
        bg_color=(245, 245, 245),
        hover_color=(245, 245, 245),
        active_color=(245, 245, 245),
        border_color=(165, 165, 165),
        selection_color=(100, 150, 255),
        caret_color=(10, 10, 10),
        padding=6,
        font_size=25,
        font_type="Veranda",
        show_scrollbars=True,
        z_index=0,
    ):
        super().__init__(
            rect=rect,
            initial_text=initial_text,
            allow_multiline=allow_multiline,
            allowed_char_mode=allowed_char_mode,
            text_color=text_color,
            bg_color=bg_color,
            hover_color=hover_color,
            active_color=active_color,
            border_color=border_color,
            selection_color=selection_color,
            caret_color=caret_color,
            padding=padding,
            font_size=font_size,
            font_type=font_type,
            show_scrollbars=show_scrollbars,
            z_index=z_index,
        )

        self.default_style = self._coerce_style(
            default_style,
            fallback_color=text_color,
        )
        self._font_cache = {}
        self._render_cache = {}
        self._style_version = 0
        self.keyword_styles = {}
        self.token_styles = {}
        self.set_keyword_styles(
            keyword_styles if keyword_styles is not None else self.python_default_keyword_styles()
        )
        self.set_token_styles(token_styles or {})

        self.autocomplete_provider = None
        self.autocomplete_items = []
        self._tokenizer = re.compile(r"\w+|\s+|[^\w\s]+", re.UNICODE)

    @staticmethod
    def python_default_keyword_styles():
        base_keyword_style = HighlightStyle((44, 96, 180), bold=True)
        styles = {kw: base_keyword_style for kw in keyword.kwlist}
        styles["True"] = HighlightStyle((160, 70, 35), bold=True)
        styles["False"] = HighlightStyle((160, 70, 35), bold=True)
        styles["None"] = HighlightStyle((120, 80, 120), italic=True)
        return styles

    def _coerce_style(self, value, fallback_color=(0, 0, 0)):
        if isinstance(value, HighlightStyle):
            return value

        if isinstance(value, dict):
            color = value.get("color", value.get("text_color", fallback_color))
            return HighlightStyle(
                tuple(color),
                bool(value.get("bold", False)),
                bool(value.get("italic", False)),
            )

        if isinstance(value, (list, tuple)) and len(value) >= 3:
            return HighlightStyle((int(value[0]), int(value[1]), int(value[2])))

        return HighlightStyle(tuple(fallback_color))

    def _invalidate_style_cache(self):
        self._style_version += 1
        self._render_cache.clear()

    def set_keyword_styles(self, styles: dict):
        self.keyword_styles = {
            str(token): self._coerce_style(style, fallback_color=self.default_style.color)
            for token, style in styles.items()
        }
        self._invalidate_style_cache()

    def set_token_styles(self, styles: dict):
        self.token_styles = {
            str(token): self._coerce_style(style, fallback_color=self.default_style.color)
            for token, style in styles.items()
        }
        self._invalidate_style_cache()

    def set_keyword_style(self, token: str, style):
        self.keyword_styles[str(token)] = self._coerce_style(style, fallback_color=self.default_style.color)
        self._invalidate_style_cache()

    def remove_keyword_style(self, token: str):
        if token in self.keyword_styles:
            self.keyword_styles.pop(token)
            self._invalidate_style_cache()

    def _get_font(self, bold=False, italic=False):
        key = (bool(bold), bool(italic))
        font = self._font_cache.get(key)
        if font is None:
            font = pygame.font.SysFont(self.font_type, self.font_size, bold=key[0], italic=key[1])
            self._font_cache[key] = font
        return font

    def _resolve_token_style(self, token: str):
        if token in self.token_styles:
            return self.token_styles[token]
        if token.isidentifier() and token in self.keyword_styles:
            return self.keyword_styles[token]
        return self.default_style

    def _highlight_segments(self, line: str):
        cache_key = (line, self._style_version)
        cached = self._render_cache.get(cache_key)
        if cached is not None:
            return cached

        parts = self._tokenizer.findall(line)
        if not parts and line:
            parts = [line]

        segments = [(token, self._resolve_token_style(token)) for token in parts]
        self._render_cache[cache_key] = segments
        return segments

    def _get_styled_prefix_width(self, line_text: str, upto_col: int):
        clamped = max(0, min(upto_col, len(line_text)))
        prefix = line_text[:clamped]
        width = 0

        for token, style in self._highlight_segments(prefix):
            if not token:
                continue
            font = self._get_font(style.bold, style.italic)
            width += font.size(token)[0]

        return width

    def get_current_prefix(self):
        line = self.lines[self.cursor_line]
        i = self.cursor_col
        while i > 0 and (line[i - 1].isalnum() or line[i - 1] == "_"):
            i -= 1
        return line[i:self.cursor_col]

    def set_autocomplete_provider(self, provider):
        self.autocomplete_provider = provider

    def request_completions(self):
        if self.autocomplete_provider is None:
            self.autocomplete_items = []
            return []

        prefix = self.get_current_prefix()
        items = self.autocomplete_provider(
            self.get_text(),
            (self.cursor_line, self.cursor_col),
            prefix,
        )
        self.autocomplete_items = list(items) if items else []
        return self.autocomplete_items

    def handle_event(self, event: pygame.event.Event):
        before_text = self.get_text()
        before_cursor = (self.cursor_line, self.cursor_col)
        super().handle_event(event)

        if event.type != pygame.KEYDOWN:
            return

        mods = getattr(event, "mod", pygame.key.get_mods())
        has_ctrl_or_cmd = bool(mods & (pygame.KMOD_CTRL | pygame.KMOD_META))
        if has_ctrl_or_cmd and event.key == pygame.K_SPACE:
            self.request_completions()
            return

        if self.autocomplete_provider is None:
            return

        after_text = self.get_text()
        after_cursor = (self.cursor_line, self.cursor_col)
        if before_text != after_text or before_cursor != after_cursor:
            self.request_completions()

    def draw(self, surface):
        UIComponent.draw(self, surface)
        self.update()

        inner_rect, content_rect, show_h, show_v = self._get_content_layout()

        prev_clip = surface.get_clip()
        effective_clip = content_rect.clip(prev_clip)
        surface.set_clip(effective_clip)

        if effective_clip.width > 0 and effective_clip.height > 0:
            self._draw_selection(surface)

            start_line = max(0, int(self._scroll_y // self._get_line_height()) - 1)
            visible_count = int(content_rect.height // self._get_line_height()) + 3
            end_line = min(len(self.lines), start_line + visible_count)

            for i in range(start_line, end_line):
                line = self.lines[i]
                draw_x = content_rect.x - self._scroll_x
                draw_y = self._line_y(i)

                for token, style in self._highlight_segments(line):
                    if not token:
                        continue
                    font = self._get_font(style.bold, style.italic)
                    render = font.render(token, True, style.color)
                    surface.blit(render, (draw_x, draw_y))
                    draw_x += render.get_width()

            if self.focused and self.caret_visible:
                line_text = self.lines[self.cursor_line]
                caret_x = content_rect.x + self._get_styled_prefix_width(line_text, self.cursor_col) - self._scroll_x
                caret_y = self._line_y(self.cursor_line)
                pygame.draw.rect(surface, self.caret_color, (caret_x, caret_y, 2, self._get_line_height()))

        surface.set_clip(prev_clip)
        self._draw_scrollbars(surface, inner_rect, content_rect, show_h, show_v)
