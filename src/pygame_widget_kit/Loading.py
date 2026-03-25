import math
import pygame

from .Animation import AngleAnimation, Easing
from .Text import Text
from .Widget import Widget


CIRCULAR_SPOKES = "CIRCULAR_SPOKES"
CIRCULAR_DOTS = "CIRCULAR_DOTS"
TRIANGLE_DOTS = "TRIANGLE_DOTS"
WAVE_DOTS = "WAVE_DOTS"
PULSING_RING = "PULSING_RING"
BAR_WAVE = "BAR_WAVE"
ROTATING_QUAD = "ROTATING_QUAD"
ORBITING_DOTS = "ORBITING_DOTS"
SPIRAL_DOTS = "SPIRAL_DOTS"
BOUNCE_DOTS = "BOUNCE_DOTS"
DOTS_SCALE = "DOTS_SCALE"
ROTATING_LINES = "ROTATING_LINES"
DOUBLE_BOUNCE = "DOUBLE_BOUNCE"
PENDULUM = "PENDULUM"
EXPANDING_RING = "EXPANDING_RING"
FLIP_DOTS = "FLIP_DOTS"
ROTATING_PLANE = "ROTATING_PLANE"
RADAR = "RADAR"
SHIFTING_DOTS = "SHIFTING_DOTS"
GRID_DOTS = "GRID_DOTS"


class LoadingSpinner(Widget):
    CIRCULAR_SPOKES = CIRCULAR_SPOKES
    CIRCULAR_DOTS = CIRCULAR_DOTS
    TRIANGLE_DOTS = TRIANGLE_DOTS
    WAVE_DOTS = WAVE_DOTS
    PULSING_RING = PULSING_RING
    BAR_WAVE = BAR_WAVE
    ROTATING_QUAD = ROTATING_QUAD
    ORBITING_DOTS = ORBITING_DOTS
    SPIRAL_DOTS = SPIRAL_DOTS
    BOUNCE_DOTS = BOUNCE_DOTS
    DOTS_SCALE = DOTS_SCALE
    ROTATING_LINES = ROTATING_LINES
    DOUBLE_BOUNCE = DOUBLE_BOUNCE
    PENDULUM = PENDULUM
    EXPANDING_RING = EXPANDING_RING
    FLIP_DOTS = FLIP_DOTS
    ROTATING_PLANE = ROTATING_PLANE
    RADAR = RADAR
    SHIFTING_DOTS = SHIFTING_DOTS
    GRID_DOTS = GRID_DOTS

    SUPPORTED_ICON_TYPES = {CIRCULAR_SPOKES, CIRCULAR_DOTS, TRIANGLE_DOTS, WAVE_DOTS, PULSING_RING, BAR_WAVE, ROTATING_QUAD, ORBITING_DOTS, SPIRAL_DOTS, BOUNCE_DOTS, DOTS_SCALE, ROTATING_LINES, DOUBLE_BOUNCE, PENDULUM, EXPANDING_RING, FLIP_DOTS, ROTATING_PLANE, RADAR, SHIFTING_DOTS, GRID_DOTS}

    def __init__(
        self,
        rect,
        text: str = "Loading...",
        icon_type: str = CIRCULAR_SPOKES,
        z_index: int = 0,
        color=None,
        border_color=None,
        hover_color=None,
        color_active=None,
        text_color=(30, 30, 30),
        font_size: int = 22,
        icon_color=(35, 35, 35),
        track_color=(210, 210, 210),
        icon_radius: int = 10,
        spoke_length: int = 10,
        spoke_width: int = 3,
        spoke_count: int = 12,
        speed_deg_per_sec: float = 240.0,
        text_gap: int = 10,
        auto_start: bool = True,
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

        self.icon_type = icon_type if icon_type in self.SUPPORTED_ICON_TYPES else self.CIRCULAR_SPOKES

        self.icon_color = icon_color
        self.track_color = track_color
        self.icon_radius = max(6, int(icon_radius))
        self.spoke_length = max(4, int(spoke_length))
        self.spoke_width = max(1, int(spoke_width))
        self.spoke_count = max(8, int(spoke_count))
        self.speed_deg_per_sec = max(30.0, float(speed_deg_per_sec))
        self.text_gap = max(4, int(text_gap))

        self.angle = 0.0
        self.running = bool(auto_start)
        self._animation_key = (id(self), "loading_spinner_angle")

        self.text = Text(
            text_str=text,
            font_size=font_size,
            pos=(0, 0),
            text_color=text_color,
            bg_color=None,
            color=None,
            border_color=None,
        )
        self.add_child(self.text)
        self._update_text_position()

    def _set_ui_manager_recursive(self, ui_manager):
        super()._set_ui_manager_recursive(ui_manager)
        if self.running:
            self._start_rotation_animation()

    def set_text(self, text: str):
        self.text.set_text(text)
        self._update_text_position()

    def set_icon_type(self, icon_type: str):
        if icon_type in self.SUPPORTED_ICON_TYPES:
            self.icon_type = icon_type
            return
        self.icon_type = self.CIRCULAR_SPOKES

    def start(self):
        self.running = True
        self._start_rotation_animation()

    def stop(self):
        self.running = False
        if self.ui_manager is not None:
            self.ui_manager.animation_manager.clear_key(self._animation_key)

    def _set_angle(self, value: float):
        self.angle = float(value) % 360.0

    def _on_rotation_complete(self):
        if self.running:
            self._start_rotation_animation()

    def _start_rotation_animation(self):
        if self.ui_manager is None:
            return

        duration = 360.0 / self.speed_deg_per_sec
        self.ui_manager.animation_manager.add(
            AngleAnimation(
                getter=lambda: self.angle,
                setter=self._set_angle,
                to_angle=self.angle + 360.0,
                from_angle=self.angle,
                duration=duration,
                easing=Easing.linear,
                key=self._animation_key,
                shortest_path=False,
                on_complete=self._on_rotation_complete,
            )
        )

    def _icon_outer_radius(self):
        return self.icon_radius + self.spoke_length

    def _icon_center(self):
        icon_outer = self._icon_outer_radius()
        left_margin = 8

        min_x = self.absolute_rect[0] + icon_outer + 2
        max_x = self.absolute_rect[0] + self.absolute_rect[2] - icon_outer - 2
        preferred_x = self.absolute_rect[0] + left_margin + icon_outer

        center_x = min(preferred_x, max_x)
        center_x = max(center_x, min_x)
        center_y = self.absolute_rect[1] + self.absolute_rect[3] // 2
        return center_x, center_y

    def _update_text_position(self):
        icon_outer = self._icon_outer_radius()
        text_w, text_h = self.text.size

        text_x = 8 + (icon_outer * 2) + self.text_gap
        max_text_x = max(4, self.rect[2] - text_w - 4)
        text_x = min(text_x, max_text_x)

        text_y = max(0, (self.rect[3] - text_h) // 2)
        self.text.rect = (text_x, text_y, text_w, text_h)
        self.text.update_absolute_rect()

    def get_layout_height(self):
        return max(self.rect[3], self.text.size[1] + 8)

    def _draw_circular_spokes_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        icon_outer = self._icon_outer_radius()

        step = 360.0 / float(self.spoke_count)

        for index in range(self.spoke_count):
            angle_deg = self.angle - (step * index)
            angle_rad = math.radians(angle_deg)

            inner_x = center_x + math.cos(angle_rad) * self.icon_radius
            inner_y = center_y + math.sin(angle_rad) * self.icon_radius
            outer_x = center_x + math.cos(angle_rad) * icon_outer
            outer_y = center_y + math.sin(angle_rad) * icon_outer

            if self.spoke_count <= 1:
                fade = 1.0
            else:
                fade = 1.0 - (index / (self.spoke_count - 1))
            intensity = 0.2 + (0.8 * fade)

            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )

            pygame.draw.line(
                surface,
                color,
                (int(inner_x), int(inner_y)),
                (int(outer_x), int(outer_y)),
                self.spoke_width,
            )

    def _draw_circular_dots_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        icon_outer = self._icon_outer_radius()

        if self.track_color is not None:
            pygame.draw.circle(
                surface,
                self.track_color,
                (int(center_x), int(center_y)),
                int(icon_outer),
                width=1,
            )

        dot_radius = max(2, self.spoke_width)
        step = 360.0 / float(self.spoke_count)

        for index in range(self.spoke_count):
            angle_deg = self.angle + (step * index)
            angle_rad = math.radians(angle_deg)

            dot_x = center_x + math.cos(angle_rad) * icon_outer
            dot_y = center_y + math.sin(angle_rad) * icon_outer

            if self.spoke_count <= 1:
                fade = 1.0
            else:
                fade = 1.0 - (index / (self.spoke_count - 1))
            intensity = 0.3 + (0.7 * fade)

            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )

            pygame.draw.circle(surface, color, (int(dot_x), int(dot_y)), dot_radius)

    def _draw_triangle_dots_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        triangle_size = self.icon_radius + self.spoke_length

        triangle_angles = [90, 210, 330]
        triangle_vertices = []

        for angle_deg in triangle_angles:
            angle_rad = math.radians(angle_deg)
            px = center_x + math.cos(angle_rad) * triangle_size
            py = center_y + math.sin(angle_rad) * triangle_size
            triangle_vertices.append(((px, py)))

        if self.track_color is not None and len(triangle_vertices) == 3:
            pygame.draw.polygon(
                surface,
                self.track_color,
                [(int(x), int(y)) for x, y in triangle_vertices],
                width=2,
            )

        dot_radius = max(2, self.spoke_width)

        v0 = triangle_vertices[0]
        v1 = triangle_vertices[1]
        v2 = triangle_vertices[2]
        edges = [(v0, v1), (v1, v2), (v2, v0)]

        edge_lengths = []
        total_perimeter = 0.0
        for edge in edges:
            dx = edge[1][0] - edge[0][0]
            dy = edge[1][1] - edge[0][1]
            length = math.sqrt(dx * dx + dy * dy)
            edge_lengths.append(length)
            total_perimeter += length

        if total_perimeter <= 0:
            return

        normalized_angle = (self.angle % 360.0) / 360.0
        progress = normalized_angle * total_perimeter

        for dot_index in range(3):
            dot_progress = (progress + (total_perimeter / 3.0) * dot_index) % total_perimeter

            edge_idx = 0
            remaining_dist = dot_progress
            while edge_idx < len(edge_lengths) and remaining_dist > edge_lengths[edge_idx]:
                remaining_dist -= edge_lengths[edge_idx]
                edge_idx += 1

            if edge_idx >= len(edges):
                edge_idx = 0
                remaining_dist = 0

            edge = edges[edge_idx]
            edge_len = edge_lengths[edge_idx]

            if edge_len > 0:
                t = remaining_dist / edge_len
            else:
                t = 0

            dot_x = edge[0][0] + (edge[1][0] - edge[0][0]) * t
            dot_y = edge[0][1] + (edge[1][1] - edge[0][1]) * t

            intensity = 0.4 + (0.6 * (1.0 - dot_index / 3.0))
            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )

            pygame.draw.circle(surface, color, (int(dot_x), int(dot_y)), dot_radius)

    def _draw_wave_dots_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        dot_radius = max(2, self.spoke_width)
        dot_count = 5
        spacing = 12

        for i in range(dot_count):
            x_offset = (i - dot_count // 2) * spacing
            phase = (self.angle / 360.0) * 2 * math.pi + (i / dot_count) * math.pi
            y_offset = math.sin(phase) * 8

            dot_x = center_x + x_offset
            dot_y = center_y + y_offset

            intensity = 0.4 + 0.6 * (1.0 - (i / max(1, dot_count - 1)))
            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )
            pygame.draw.circle(surface, color, (int(dot_x), int(dot_y)), dot_radius)

    def _draw_pulsing_ring_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        radius_base = self.icon_radius + 4
        pulse = math.sin((self.angle / 360.0) * 2 * math.pi) * 4
        radius = radius_base + pulse

        pygame.draw.circle(surface, self.icon_color, (int(center_x), int(center_y)), int(radius), width=self.spoke_width)

    def _draw_bar_wave_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        bar_count = 5
        bar_width = 4
        max_height = 20
        spacing = 10

        for i in range(bar_count):
            phase = (self.angle / 360.0) * 2 * math.pi + (i / bar_count) * (2 * math.pi / 2)
            height = max_height * (0.3 + 0.7 * (1.0 + math.sin(phase)) / 2.0)

            bar_x = center_x + (i - bar_count // 2) * spacing
            bar_y = center_y - height // 2

            intensity = 0.4 + 0.6 * ((1.0 + math.sin(phase)) / 2.0)
            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )
            pygame.draw.rect(surface, color, (int(bar_x) - bar_width // 2, int(bar_y), bar_width, int(height)))

    def _draw_rotating_quad_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        size = self.icon_radius + self.spoke_length
        angle_rad = math.radians(self.angle)

        corners = [
            (math.cos(angle_rad + 0 * math.pi / 2) * size, math.sin(angle_rad + 0 * math.pi / 2) * size),
            (math.cos(angle_rad + 1 * math.pi / 2) * size, math.sin(angle_rad + 1 * math.pi / 2) * size),
            (math.cos(angle_rad + 2 * math.pi / 2) * size, math.sin(angle_rad + 2 * math.pi / 2) * size),
            (math.cos(angle_rad + 3 * math.pi / 2) * size, math.sin(angle_rad + 3 * math.pi / 2) * size),
        ]
        points = [(int(center_x + x), int(center_y + y)) for x, y in corners]
        pygame.draw.polygon(surface, self.icon_color, points, width=self.spoke_width)

    def _draw_orbiting_dots_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        dot_radius = max(2, self.spoke_width)
        orbit_radius = self.icon_radius + self.spoke_length
        dot_count = 3

        for i in range(dot_count):
            angle_deg = self.angle + (360.0 / dot_count) * i
            angle_rad = math.radians(angle_deg)

            dot_x = center_x + math.cos(angle_rad) * orbit_radius
            dot_y = center_y + math.sin(angle_rad) * orbit_radius

            intensity = 0.4 + 0.6 * (1.0 - (i / max(1, dot_count - 1)))
            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )
            pygame.draw.circle(surface, color, (int(dot_x), int(dot_y)), dot_radius)

    def _draw_spiral_dots_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        dot_radius = max(2, self.spoke_width)
        dot_count = 4

        for i in range(dot_count):
            angle_deg = self.angle + (360.0 / dot_count) * i
            angle_rad = math.radians(angle_deg)
            spiral_radius = self.icon_radius + (self.spoke_length * (i / max(1, dot_count - 1)))

            dot_x = center_x + math.cos(angle_rad) * spiral_radius
            dot_y = center_y + math.sin(angle_rad) * spiral_radius

            intensity = 0.3 + 0.7 * (i / max(1, dot_count - 1))
            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )
            pygame.draw.circle(surface, color, (int(dot_x), int(dot_y)), dot_radius + int(i))

    def _draw_bounce_dots_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        dot_radius = max(2, self.spoke_width)
        dot_count = 3
        spacing = 14

        for i in range(dot_count):
            phase = (self.angle / 360.0) * 2 * math.pi - (i / dot_count) * (math.pi * 0.8)
            bounce = abs(math.sin(phase)) * 12

            dot_x = center_x + (i - dot_count // 2) * spacing
            dot_y = center_y - bounce

            intensity = 0.4 + 0.6 * abs(math.sin(phase))
            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )
            pygame.draw.circle(surface, color, (int(dot_x), int(dot_y)), int(dot_radius + intensity * 2))

    def _draw_dots_scale_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        dot_count = 4
        spacing = 12

        for i in range(dot_count):
            phase = (self.angle / 360.0) * 2 * math.pi + (i / dot_count) * (2 * math.pi)
            scale = 0.5 + 0.5 * (1.0 + math.sin(phase)) / 2.0
            dot_radius = max(1, int((self.spoke_width + 1) * scale))

            dot_x = center_x + (i - dot_count // 2) * spacing - spacing // 4
            dot_y = center_y

            intensity = 0.3 + 0.7 * scale
            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )
            pygame.draw.circle(surface, color, (int(dot_x), int(dot_y)), dot_radius)

    def _draw_rotating_lines_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        line_count = 6
        line_length = self.icon_radius + self.spoke_length

        for i in range(line_count):
            angle_deg = self.angle + (360.0 / line_count) * i
            angle_rad = math.radians(angle_deg)

            end_x = center_x + math.cos(angle_rad) * line_length
            end_y = center_y + math.sin(angle_rad) * line_length

            intensity = 0.2 + 0.8 * (1.0 - (i / max(1, line_count - 1)))
            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )
            pygame.draw.line(
                surface,
                color,
                (int(center_x), int(center_y)),
                (int(end_x), int(end_y)),
                self.spoke_width,
            )

    def _draw_double_bounce_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        dot_radius = max(2, self.spoke_width + 1)
        spacing = 16

        for dot_idx in range(2):
            phase = (self.angle / 360.0) * 2 * math.pi + (dot_idx * math.pi)
            bounce = abs(math.sin(phase)) * 14

            dot_x = center_x + (dot_idx - 0.5) * spacing
            dot_y = center_y - bounce

            intensity = 0.4 + 0.6 * abs(math.sin(phase))
            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )
            pygame.draw.circle(surface, color, (int(dot_x), int(dot_y)), int(dot_radius + 1))

    def _draw_pendulum_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        dot_radius = max(2, self.spoke_width)
        pivot_x, pivot_y = center_x, center_y - 8
        pendulum_length = 16

        angle_deg = math.sin((self.angle / 360.0) * 2 * math.pi) * 45
        angle_rad = math.radians(angle_deg)

        dot_x = pivot_x + math.sin(angle_rad) * pendulum_length
        dot_y = pivot_y + math.cos(angle_rad) * pendulum_length

        pygame.draw.line(surface, self.icon_color, (int(pivot_x), int(pivot_y)), (int(dot_x), int(dot_y)), self.spoke_width)
        pygame.draw.circle(surface, self.icon_color, (int(dot_x), int(dot_y)), dot_radius + 2)

    def _draw_expanding_ring_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        ring_count = 3
        base_radius = self.icon_radius

        for ring_idx in range(ring_count):
            phase = (self.angle / 360.0) * 2 * math.pi + (ring_idx / ring_count) * (2 * math.pi / 1.5)
            scale = (1.0 + math.sin(phase)) / 2.0
            radius = base_radius + (self.spoke_length * (ring_idx / ring_count + 1)) + (scale * 4)
            alpha_intensity = 0.6 * (1.0 - scale)

            if alpha_intensity > 0.1:
                color = (
                    min(255, max(0, int(self.icon_color[0] * alpha_intensity))),
                    min(255, max(0, int(self.icon_color[1] * alpha_intensity))),
                    min(255, max(0, int(self.icon_color[2] * alpha_intensity))),
                )
                pygame.draw.circle(surface, color, (int(center_x), int(center_y)), int(radius), width=self.spoke_width)

    def _draw_flip_dots_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        dot_count = 4
        orbit_radius = self.icon_radius + self.spoke_length

        for i in range(dot_count):
            angle_deg = self.angle + (360.0 / dot_count) * i
            angle_rad = math.radians(angle_deg)
            flip_scale = abs(math.cos(angle_rad))
            dot_radius = max(1, int((self.spoke_width + 1) * flip_scale))

            dot_x = center_x + math.cos(angle_rad) * orbit_radius
            dot_y = center_y + math.sin(angle_rad) * orbit_radius

            intensity = 0.4 + 0.6 * flip_scale
            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )
            pygame.draw.circle(surface, color, (int(dot_x), int(dot_y)), dot_radius)

    def _draw_rotating_plane_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        size = self.icon_radius + self.spoke_length
        angle_rad = math.radians(self.angle)

        rect_width = int(size * 1.5)
        rect_height = int(size * 0.6)

        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        corners = [
            (-rect_width // 2, -rect_height // 2),
            (rect_width // 2, -rect_height // 2),
            (rect_width // 2, rect_height // 2),
            (-rect_width // 2, rect_height // 2),
        ]

        rotated = []
        for x, y in corners:
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            rotated.append((int(center_x + rx), int(center_y + ry)))

        pygame.draw.polygon(surface, self.icon_color, rotated, width=self.spoke_width)

    def _draw_radar_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        radar_radius = self.icon_radius + self.spoke_length
        sweep_angle = self.angle % 360.0
        sweep_rad = math.radians(sweep_angle)

        pygame.draw.circle(surface, self.track_color if self.track_color else self.icon_color, (int(center_x), int(center_y)), int(radar_radius), width=1)
        pygame.draw.line(
            surface,
            self.icon_color,
            (int(center_x), int(center_y)),
            (int(center_x + math.cos(sweep_rad) * radar_radius), int(center_y + math.sin(sweep_rad) * radar_radius)),
            self.spoke_width,
        )

    def _draw_shifting_dots_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        dot_radius = max(2, self.spoke_width)
        dot_count = 5
        spacing = 10

        for i in range(dot_count):
            phase = (self.angle / 360.0) * 2 * math.pi
            offset = (phase + (i / dot_count) * 2 * math.pi) % (2 * math.pi)
            x_shift = math.sin(offset) * 8

            dot_x = center_x + (i - dot_count // 2) * spacing + x_shift
            dot_y = center_y

            intensity = 0.4 + 0.6 * (1.0 - (i / max(1, dot_count - 1)))
            color = (
                min(255, max(0, int(self.icon_color[0] * intensity))),
                min(255, max(0, int(self.icon_color[1] * intensity))),
                min(255, max(0, int(self.icon_color[2] * intensity))),
            )
            pygame.draw.circle(surface, color, (int(dot_x), int(dot_y)), dot_radius)

    def _draw_grid_dots_icon(self, surface: pygame.Surface):
        center_x, center_y = self._icon_center()
        grid_size = 3
        spacing = 8
        phase = (self.angle / 360.0) * 2 * math.pi

        for row in range(grid_size):
            for col in range(grid_size):
                dot_offset = ((row * grid_size + col) / (grid_size * grid_size)) * 2 * math.pi
                dot_phase = (phase + dot_offset) % (2 * math.pi)
                scale = 0.3 + 0.7 * (1.0 + math.sin(dot_phase)) / 2.0
                dot_radius = max(1, int((self.spoke_width) * scale))

                x_pos = center_x + (col - 1) * spacing
                y_pos = center_y + (row - 1) * spacing

                intensity = 0.3 + 0.7 * scale
                color = (
                    min(255, max(0, int(self.icon_color[0] * intensity))),
                    min(255, max(0, int(self.icon_color[1] * intensity))),
                    min(255, max(0, int(self.icon_color[2] * intensity))),
                )
                pygame.draw.circle(surface, color, (int(x_pos), int(y_pos)), dot_radius)

    def _draw_icon(self, surface: pygame.Surface):
        if self.icon_type == self.CIRCULAR_SPOKES:
            self._draw_circular_spokes_icon(surface)
        elif self.icon_type == self.CIRCULAR_DOTS:
            self._draw_circular_dots_icon(surface)
        elif self.icon_type == self.TRIANGLE_DOTS:
            self._draw_triangle_dots_icon(surface)
        elif self.icon_type == self.WAVE_DOTS:
            self._draw_wave_dots_icon(surface)
        elif self.icon_type == self.PULSING_RING:
            self._draw_pulsing_ring_icon(surface)
        elif self.icon_type == self.BAR_WAVE:
            self._draw_bar_wave_icon(surface)
        elif self.icon_type == self.ROTATING_QUAD:
            self._draw_rotating_quad_icon(surface)
        elif self.icon_type == self.ORBITING_DOTS:
            self._draw_orbiting_dots_icon(surface)
        elif self.icon_type == self.SPIRAL_DOTS:
            self._draw_spiral_dots_icon(surface)
        elif self.icon_type == self.BOUNCE_DOTS:
            self._draw_bounce_dots_icon(surface)
        elif self.icon_type == self.DOTS_SCALE:
            self._draw_dots_scale_icon(surface)
        elif self.icon_type == self.ROTATING_LINES:
            self._draw_rotating_lines_icon(surface)
        elif self.icon_type == self.DOUBLE_BOUNCE:
            self._draw_double_bounce_icon(surface)
        elif self.icon_type == self.PENDULUM:
            self._draw_pendulum_icon(surface)
        elif self.icon_type == self.EXPANDING_RING:
            self._draw_expanding_ring_icon(surface)
        elif self.icon_type == self.FLIP_DOTS:
            self._draw_flip_dots_icon(surface)
        elif self.icon_type == self.ROTATING_PLANE:
            self._draw_rotating_plane_icon(surface)
        elif self.icon_type == self.RADAR:
            self._draw_radar_icon(surface)
        elif self.icon_type == self.SHIFTING_DOTS:
            self._draw_shifting_dots_icon(surface)
        elif self.icon_type == self.GRID_DOTS:
            self._draw_grid_dots_icon(surface)
        else:
            self._draw_circular_spokes_icon(surface)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        self._update_text_position()
        super().draw(surface)
        self._draw_icon(surface)
