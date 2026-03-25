import pygame
import pygame.gfxdraw

from functools import partial

from .Animation import Easing
from .Widget import Widget


THIN_LINE_BAR = "THIN_LINE_BAR"
SEGMENTED_BAR = "SEGMENTED_BAR"
STRIPED_BAR = "STRIPED_BAR"
GLOW_LINE_BAR = "GLOW_LINE_BAR"
TEXT_MODE_VALUE_MAX = "VALUE_MAX"
TEXT_MODE_PERCENT = "PERCENT"
TEXT_POSITION_RIGHT = "RIGHT"
TEXT_POSITION_LEFT = "LEFT"
TEXT_POSITION_NONE = "NONE"


class ProgressBar(Widget):
    THIN_LINE_BAR = THIN_LINE_BAR
    SEGMENTED_BAR = SEGMENTED_BAR
    STRIPED_BAR = STRIPED_BAR
    GLOW_LINE_BAR = GLOW_LINE_BAR
    TEXT_MODE_VALUE_MAX = TEXT_MODE_VALUE_MAX
    TEXT_MODE_PERCENT = TEXT_MODE_PERCENT
    TEXT_POSITION_RIGHT = TEXT_POSITION_RIGHT
    TEXT_POSITION_LEFT = TEXT_POSITION_LEFT
    TEXT_POSITION_NONE = TEXT_POSITION_NONE

    SUPPORTED_BAR_TYPES = {THIN_LINE_BAR, SEGMENTED_BAR, STRIPED_BAR, GLOW_LINE_BAR}
    SUPPORTED_TEXT_MODES = {TEXT_MODE_VALUE_MAX, TEXT_MODE_PERCENT}
    SUPPORTED_TEXT_POSITIONS = {TEXT_POSITION_RIGHT, TEXT_POSITION_LEFT, TEXT_POSITION_NONE}

    def __init__(
        self,
        rect,
        min_value: float = 0.0,
        max_value: float = 100.0,
        value: float = 0.0,
        bar_type: str = THIN_LINE_BAR,
        show_text: bool = True,
        animate_value_change: bool = True,
        value_animation_duration: float = 0.35,
        z_index: int = 0,
        color=(236, 236, 236),
        border_color=(140, 140, 140),
        hover_color=None,
        color_active=None,
        track_color=(214, 214, 214),
        fill_color=None,
        fill_color_start=(58, 146, 255),
        fill_color_end=(34, 84, 196),
        text_color=(15, 15, 15),
        bar_thickness: int = 6,
        text_display_mode: str = TEXT_MODE_VALUE_MAX,
        text_position: str = TEXT_POSITION_RIGHT,
        text_padding: int = 10,
        activity_animation_enabled: bool = False,
        shimmer_color=(255, 255, 255),
        shimmer_alpha: int = 90,
        shimmer_width_ratio: float = 0.18,
        shimmer_cycles_per_sec: float = 1.2,
        font_size: int = 17,
    ):
        super().__init__(
            rect=rect,
            style=None,
            z_index=z_index,
            color=color,
            border_color=border_color,
            hover_color=hover_color,
            color_active=color_active,
        )

        self.min_value = float(min_value)
        self.max_value = float(max_value)
        if self.max_value < self.min_value:
            self.min_value, self.max_value = self.max_value, self.min_value

        self.bar_type = bar_type if bar_type in self.SUPPORTED_BAR_TYPES else self.THIN_LINE_BAR

        initial_value = self._clamp_value(float(value))
        self.value = initial_value
        self.display_value = initial_value

        self.show_text = bool(show_text)
        self.animate_value_change = bool(animate_value_change)
        self.value_animation_duration = max(0.05, float(value_animation_duration))
        self.text_display_mode = (
            text_display_mode if text_display_mode in self.SUPPORTED_TEXT_MODES else self.TEXT_MODE_VALUE_MAX
        )
        self.text_position = text_position if text_position in self.SUPPORTED_TEXT_POSITIONS else self.TEXT_POSITION_RIGHT
        self.text_padding = max(2, int(text_padding))

        self.track_color = track_color
        if fill_color is None:
            self.fill_color_start = fill_color_start
            self.fill_color_end = fill_color_end
        else:
            self.fill_color_start = fill_color
            self.fill_color_end = fill_color
        self.text_color = text_color
        self.bar_thickness = max(4, int(bar_thickness))

        self.activity_animation_enabled = bool(activity_animation_enabled)
        self.activity_active = False
        self.shimmer_color = shimmer_color
        self.shimmer_alpha = max(0, min(255, int(shimmer_alpha)))
        self.shimmer_width_ratio = max(0.05, min(0.9, float(shimmer_width_ratio)))
        self.shimmer_cycles_per_sec = max(0.2, float(shimmer_cycles_per_sec))
        self.shimmer_phase = 0.0

        self.font_size = max(12, int(font_size))
        self.font = pygame.font.SysFont("Verdana", self.font_size)

        self.value_change_callback = None
        self._value_anim_key = (id(self), "progress_value")
        self._shimmer_anim_key = (id(self), "progress_shimmer")

        self.segment_count = 18
        self.segment_gap = 2
        self.stripe_width = 12
        self.glow_alpha = 80
        self.stripe_alpha = 42
        self.stripe_dark_alpha = 0
        self.stripe_bright_color = (255, 255, 255)
        self.stripe_dark_color = (8, 32, 82)
        self.stripe_top_highlight = (255, 255, 255, 110)
        self._gradient_cache = {}

        if self.bar_type == self.STRIPED_BAR:
            self.stripe_width = 14
            self.stripe_alpha = 175
            self.stripe_dark_alpha = 145
            # Dedicated striped palette: visibly different from thin-line and glow-line.
            self.track_color = (182, 197, 226)
            self.fill_color_start = (39, 122, 255)
            self.fill_color_end = (16, 56, 186)
            self.stripe_bright_color = (240, 250, 255)
            self.stripe_dark_color = (6, 34, 116)
            self.stripe_top_highlight = (255, 255, 255, 170)
        elif self.bar_type == self.GLOW_LINE_BAR:
            self.glow_alpha = 150

    def _set_ui_manager_recursive(self, ui_manager):
        super()._set_ui_manager_recursive(ui_manager)
        if self.activity_active and self.activity_animation_enabled:
            self._start_shimmer_animation()

    def bind_on_value_change(self, func, *args):
        self.value_change_callback = partial(func, *args)

    def _emit_value_change(self):
        if self.value_change_callback is not None:
            self.value_change_callback()

    def _clamp_value(self, value: float):
        if value < self.min_value:
            return self.min_value
        if value > self.max_value:
            return self.max_value
        return value

    def set_range(self, min_value: float, max_value: float):
        self.min_value = float(min_value)
        self.max_value = float(max_value)
        if self.max_value < self.min_value:
            self.min_value, self.max_value = self.max_value, self.min_value
        self.set_value(self.value)

    def get_value(self):
        return self.value

    def get_progress_ratio(self):
        if self.max_value == self.min_value:
            return 0.0
        return (self.display_value - self.min_value) / (self.max_value - self.min_value)

    def set_value(self, value: float):
        new_value = self._clamp_value(float(value))
        value_changed = abs(new_value - self.value) > 1e-9
        self.value = new_value

        if self.ui_manager is None or not self.animate_value_change:
            self.display_value = self.value
        else:
            delta = abs(self.value - self.display_value)
            duration = self.value_animation_duration
            if self.max_value != self.min_value:
                normalized_delta = delta / (self.max_value - self.min_value)
                duration = max(0.08, self.value_animation_duration * (0.35 + normalized_delta * 0.9))

            self.ui_manager.animation_manager.animate_attr(
                target=self,
                attr_name="display_value",
                to_value=self.value,
                duration=duration,
                easing=Easing.ease_out_cubic,
                key=self._value_anim_key,
            )

        if value_changed:
            self._emit_value_change()

    def increment(self, delta: float):
        self.set_value(self.value + float(delta))

    def set_show_text(self, show_text: bool):
        self.show_text = bool(show_text)

    def set_text_display_mode(self, mode: str):
        self.text_display_mode = mode if mode in self.SUPPORTED_TEXT_MODES else self.TEXT_MODE_VALUE_MAX

    def set_text_position(self, position: str):
        self.text_position = position if position in self.SUPPORTED_TEXT_POSITIONS else self.TEXT_POSITION_RIGHT

    def set_activity_animation_enabled(self, enabled: bool):
        self.activity_animation_enabled = bool(enabled)
        if not self.activity_animation_enabled:
            self._stop_shimmer_animation()
            return

        if self.activity_active:
            self._start_shimmer_animation()

    def activate(self):
        self.activity_active = True
        if self.activity_animation_enabled:
            self._start_shimmer_animation()

    def deactivate(self):
        self.activity_active = False
        self._stop_shimmer_animation()

    def _set_shimmer_phase(self, value: float):
        self.shimmer_phase = max(0.0, min(1.0, float(value)))

    def _stop_shimmer_animation(self):
        self.shimmer_phase = 0.0
        if self.ui_manager is not None:
            self.ui_manager.animation_manager.clear_key(self._shimmer_anim_key)

    def _on_shimmer_complete(self):
        if self.activity_active and self.activity_animation_enabled:
            self._start_shimmer_animation()

    def _start_shimmer_animation(self):
        if self.ui_manager is None:
            return

        duration = 1.0 / self.shimmer_cycles_per_sec
        self.ui_manager.animation_manager.animate_attr(
            target=self,
            attr_name="shimmer_phase",
            to_value=1.0,
            from_value=0.0,
            duration=duration,
            easing=Easing.linear,
            key=self._shimmer_anim_key,
            on_complete=self._on_shimmer_complete,
        )

    def _bar_rect(self):
        bar_left = self.absolute_rect[0] + 8
        bar_right = self.absolute_rect[0] + self.rect[2] - 8

        if self.show_text and self.text_position != self.TEXT_POSITION_NONE:
            text_w, _ = self._measure_text_size(self._format_value_text())
            reservation = text_w + self.text_padding + 6
            if self.text_position == self.TEXT_POSITION_RIGHT:
                bar_right -= reservation
            elif self.text_position == self.TEXT_POSITION_LEFT:
                bar_left += reservation

        width = max(24, bar_right - bar_left)

        y = self.absolute_rect[1] + max(2, self.rect[3] // 2 - self.bar_thickness // 2)
        return pygame.Rect(int(bar_left), int(y), int(width), int(self.bar_thickness))

    def _format_value_text(self):
        if self.max_value == self.min_value:
            ratio = 0.0
        else:
            ratio = (self.display_value - self.min_value) / (self.max_value - self.min_value)

        ratio = max(0.0, min(1.0, ratio))

        if self.text_display_mode == self.TEXT_MODE_PERCENT:
            return f"{ratio * 100:.0f}%"

        return f"{self.display_value:.0f}/{self.max_value:.0f}"

    def _measure_text_size(self, text: str):
        render = self.font.render(text, True, self.text_color)
        return render.get_width(), render.get_height()

    def _draw_aa_circle(self, surface: pygame.Surface, center_x: int, center_y: int, radius: int, color):
        if radius <= 0:
            return
        pygame.gfxdraw.filled_circle(surface, center_x, center_y, radius, color)
        pygame.gfxdraw.aacircle(surface, center_x, center_y, radius, color)

    def _draw_aa_rounded_rect(self, surface: pygame.Surface, rect: pygame.Rect, color, radius: int):
        if rect.width <= 0 or rect.height <= 0:
            return

        radius = max(0, min(int(radius), rect.width // 2, rect.height // 2))
        if radius == 0:
            pygame.gfxdraw.box(surface, rect, color)
            return

        middle_rect = pygame.Rect(rect.x + radius, rect.y, rect.width - 2 * radius, rect.height)
        vertical_rect = pygame.Rect(rect.x, rect.y + radius, rect.width, rect.height - 2 * radius)
        pygame.gfxdraw.box(surface, middle_rect, color)
        pygame.gfxdraw.box(surface, vertical_rect, color)

        self._draw_aa_circle(surface, rect.x + radius, rect.y + radius, radius, color)
        self._draw_aa_circle(surface, rect.right - radius - 1, rect.y + radius, radius, color)
        self._draw_aa_circle(surface, rect.x + radius, rect.bottom - radius - 1, radius, color)
        self._draw_aa_circle(surface, rect.right - radius - 1, rect.bottom - radius - 1, radius, color)

    def _draw_horizontal_gradient_rounded(self, surface: pygame.Surface, rect: pygame.Rect, start_color, end_color, radius: int):
        if rect.width <= 0 or rect.height <= 0:
            return

        cache_key = (rect.width, rect.height, start_color, end_color, radius)
        cached = self._gradient_cache.get(cache_key)
        if cached is None:
            gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            width = max(1, rect.width - 1)

            for x in range(rect.width):
                t = x / width
                color = (
                    int(start_color[0] + (end_color[0] - start_color[0]) * t),
                    int(start_color[1] + (end_color[1] - start_color[1]) * t),
                    int(start_color[2] + (end_color[2] - start_color[2]) * t),
                    255,
                )
                pygame.gfxdraw.vline(gradient_surface, x, 0, rect.height - 1, color)

            mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            self._draw_aa_rounded_rect(mask, pygame.Rect(0, 0, rect.width, rect.height), (255, 255, 255, 255), radius)
            gradient_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self._gradient_cache[cache_key] = gradient_surface
            cached = gradient_surface

        surface.blit(cached, rect.topleft)

    def _draw_thin_line_bar(self, surface: pygame.Surface):
        bar_rect = self._bar_rect()
        ratio = max(0.0, min(1.0, self.get_progress_ratio()))
        radius = min(5, bar_rect.height // 2)

        self._draw_aa_rounded_rect(surface, bar_rect, self.track_color, radius)

        filled_width = int(round(bar_rect.width * ratio))
        if filled_width > 0:
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, filled_width, bar_rect.height)
            self._draw_horizontal_gradient_rounded(
                surface,
                fill_rect,
                self.fill_color_start,
                self.fill_color_end,
                0,
            )

            if self.activity_active and self.activity_animation_enabled:
                self._draw_shimmer(surface, fill_rect)

    def _draw_segmented_bar(self, surface: pygame.Surface):
        bar_rect = self._bar_rect()
        ratio = max(0.0, min(1.0, self.get_progress_ratio()))
        radius = min(5, bar_rect.height // 2)

        self._draw_aa_rounded_rect(surface, bar_rect, self.track_color, radius)

        segment_count = max(4, self.segment_count)
        total_gap = self.segment_gap * (segment_count - 1)
        usable_width = max(1, bar_rect.width - total_gap)
        base_segment_w = max(1, usable_width // segment_count)
        remainder = max(0, usable_width - (base_segment_w * segment_count))
        active_segments = int(round(segment_count * ratio))

        if ratio >= 0.999:
            self._draw_horizontal_gradient_rounded(
                surface,
                bar_rect,
                self.fill_color_start,
                self.fill_color_end,
                radius,
            )
            return

        cursor_x = bar_rect.x
        for i in range(segment_count):
            seg_w = base_segment_w + (1 if i < remainder else 0)
            seg_x = cursor_x
            seg_rect = pygame.Rect(seg_x, bar_rect.y, seg_w, bar_rect.height)
            cursor_x += seg_w + self.segment_gap

            if i < active_segments:
                if self.activity_active and self.activity_animation_enabled:
                    phase = (self.shimmer_phase + (i / max(1, segment_count - 1))) % 1.0
                    mix = 0.35 + (0.65 * phase)
                    color = (
                        int(self.fill_color_start[0] + (self.fill_color_end[0] - self.fill_color_start[0]) * mix),
                        int(self.fill_color_start[1] + (self.fill_color_end[1] - self.fill_color_start[1]) * mix),
                        int(self.fill_color_start[2] + (self.fill_color_end[2] - self.fill_color_start[2]) * mix),
                    )
                    self._draw_aa_rounded_rect(surface, seg_rect, color, 0)
                else:
                    solid_color = (
                        int((self.fill_color_start[0] + self.fill_color_end[0]) / 2),
                        int((self.fill_color_start[1] + self.fill_color_end[1]) / 2),
                        int((self.fill_color_start[2] + self.fill_color_end[2]) / 2),
                    )
                    self._draw_aa_rounded_rect(surface, seg_rect, solid_color, 0)

    def _draw_striped_bar(self, surface: pygame.Surface):
        bar_rect = self._bar_rect()
        ratio = max(0.0, min(1.0, self.get_progress_ratio()))
        radius = min(5, bar_rect.height // 2)

        self._draw_aa_rounded_rect(surface, bar_rect, self.track_color, radius)

        filled_width = int(round(bar_rect.width * ratio))
        if filled_width <= 0:
            return

        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, filled_width, bar_rect.height)
        self._draw_horizontal_gradient_rounded(
            surface,
            fill_rect,
            self.fill_color_start,
            self.fill_color_end,
            0,
        )

        stripe_surface = pygame.Surface((fill_rect.width, fill_rect.height), pygame.SRCALPHA)
        stripe_width = max(6, self.stripe_width)
        phase_px = stripe_width
        if self.activity_active and self.activity_animation_enabled:
            phase_px = int(self.shimmer_phase * stripe_width * 2)

        stripe_color = (
            self.stripe_bright_color[0],
            self.stripe_bright_color[1],
            self.stripe_bright_color[2],
            self.stripe_alpha,
        )
        dark_stripe_color = (
            self.stripe_dark_color[0],
            self.stripe_dark_color[1],
            self.stripe_dark_color[2],
            self.stripe_dark_alpha,
        )

        # Primary bright diagonal stripes.
        for x in range(-stripe_width + phase_px, fill_rect.width + stripe_width, stripe_width * 2):
            p1 = (x, fill_rect.height)
            p2 = (x + stripe_width, fill_rect.height)
            p3 = (x + stripe_width * 2, 0)
            p4 = (x + stripe_width, 0)
            pygame.gfxdraw.filled_polygon(stripe_surface, [p1, p2, p3, p4], stripe_color)

        # Secondary darker stripes between bright bands for stronger contrast.
        for x in range(-stripe_width * 2 + phase_px, fill_rect.width + stripe_width, stripe_width * 2):
            q1 = (x, fill_rect.height)
            q2 = (x + stripe_width // 2, fill_rect.height)
            q3 = (x + stripe_width + stripe_width // 2, 0)
            q4 = (x + stripe_width, 0)
            pygame.gfxdraw.filled_polygon(stripe_surface, [q1, q2, q3, q4], dark_stripe_color)

        surface.blit(stripe_surface, fill_rect.topleft)

        # Crisp top highlight line to separate striped bar from thin-line style.
        top_line = pygame.Surface((fill_rect.width, 1), pygame.SRCALPHA)
        top_line.fill(self.stripe_top_highlight)
        surface.blit(top_line, (fill_rect.x, fill_rect.y))

    def _draw_glow_line_bar(self, surface: pygame.Surface):
        bar_rect = self._bar_rect()
        ratio = max(0.0, min(1.0, self.get_progress_ratio()))
        radius = min(5, bar_rect.height // 2)

        self._draw_aa_rounded_rect(surface, bar_rect, self.track_color, radius)

        filled_width = int(round(bar_rect.width * ratio))
        if filled_width <= 0:
            return

        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, filled_width, bar_rect.height)

        glow = pygame.Surface((fill_rect.width + 20, fill_rect.height + 20), pygame.SRCALPHA)
        glow_color = (*self.fill_color_end, self.glow_alpha)
        self._draw_aa_rounded_rect(
            glow,
            pygame.Rect(10, 10, fill_rect.width, fill_rect.height),
            glow_color,
            radius,
        )
        self._draw_aa_rounded_rect(
            glow,
            pygame.Rect(8, 8, fill_rect.width + 4, fill_rect.height + 4),
            (*self.fill_color_start, max(40, self.glow_alpha // 2)),
            radius + 2,
        )
        surface.blit(glow, (fill_rect.x - 10, fill_rect.y - 10))

        self._draw_horizontal_gradient_rounded(
            surface,
            fill_rect,
            self.fill_color_start,
            self.fill_color_end,
            0,
        )

        # Add a subtle top highlight so glow-line looks visibly different from thin-line.
        highlight_h = max(1, fill_rect.height // 3)
        highlight_rect = pygame.Rect(fill_rect.x, fill_rect.y, fill_rect.width, highlight_h)
        highlight = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 70))
        surface.blit(highlight, highlight_rect.topleft)

        if self.activity_active and self.activity_animation_enabled:
            self._draw_shimmer(surface, fill_rect)

    def _draw_shimmer(self, surface: pygame.Surface, fill_rect: pygame.Rect):
        shimmer_width = max(10, int(fill_rect.width * self.shimmer_width_ratio))
        if shimmer_width <= 0:
            return

        travel = fill_rect.width + shimmer_width * 2
        highlight_center = fill_rect.x - shimmer_width + int(travel * self.shimmer_phase)
        highlight_rect = pygame.Rect(
            highlight_center - shimmer_width // 2,
            fill_rect.y,
            shimmer_width,
            fill_rect.height,
        )
        clipped = highlight_rect.clip(fill_rect)
        if clipped.width <= 0 or clipped.height <= 0:
            return

        overlay = pygame.Surface((clipped.width, clipped.height), pygame.SRCALPHA)
        overlay.fill((*self.shimmer_color, self.shimmer_alpha))
        surface.blit(overlay, (clipped.x, clipped.y))

    def _draw_value_text(self, surface: pygame.Surface):
        if not self.show_text or self.text_position == self.TEXT_POSITION_NONE:
            return

        text = self._format_value_text()
        render = self.font.render(text, True, self.text_color)

        bar_rect = self._bar_rect()
        if self.text_position == self.TEXT_POSITION_RIGHT:
            text_x = bar_rect.right + self.text_padding
        else:
            text_x = self.absolute_rect[0] + 8

        text_y = bar_rect.centery - render.get_height() // 2
        surface.blit(render, (text_x, text_y))

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        super().draw(surface)

        if self.bar_type == self.THIN_LINE_BAR:
            self._draw_thin_line_bar(surface)
        elif self.bar_type == self.SEGMENTED_BAR:
            self._draw_segmented_bar(surface)
        elif self.bar_type == self.STRIPED_BAR:
            self._draw_striped_bar(surface)
        elif self.bar_type == self.GLOW_LINE_BAR:
            self._draw_glow_line_bar(surface)
        else:
            self._draw_thin_line_bar(surface)

        self._draw_value_text(surface)
