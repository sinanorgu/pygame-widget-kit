import pygame
from .UIComponent import UIComponent
from .Widget import Widget
from .Animation import Easing


class LayoutContainer(Widget):
    """Base layout container that automatically positions children."""

    def __init__(
        self,
        rect,
        spacing: int = 0,
        padding: int = 0,
        z_index: int = 0,
        color=None,
        border_color=None,
        color_active=None,
        scrollable: bool = False,
        show_scrollbar: bool = True,
        scrollbar_width: int = 10,
        wheel_step: int = 32,
        smooth_scroll: bool = False,
        smooth_scroll_factor: float = 0.14,
        smooth_snap_threshold: float = 2.0,
    ):
        if color_active is None and color is not None:
            color_active = color

        super().__init__(
            rect=rect,
            style=None,
            z_index=z_index,
            color=color,
            border_color=border_color,
            color_active=color_active,
        )
        self.spacing = spacing
        self.padding = padding
        self._layout_dirty = True
        self.clip_children = True

        self.scrollable = scrollable
        self.show_scrollbar = show_scrollbar
        self.scrollbar_width = max(6, scrollbar_width)
        self.wheel_step = max(8, wheel_step)
        self.smooth_scroll = smooth_scroll
        self.smooth_scroll_factor = max(0.05, min(1.0, smooth_scroll_factor))
        self.smooth_snap_threshold = max(0.5, float(smooth_snap_threshold))

        self._scroll_y = 0.0
        self._scroll_target_y = 0.0
        self._max_scroll = 0.0
        self._content_height = 0

        self._scrollbar_track_rect = pygame.Rect(0, 0, 0, 0)
        self._scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)
        self._scrollbar_dragging = False
        self._scrollbar_drag_offset = 0
        self._last_smooth_tick_ms = None

    def set_scrollable(self, enabled: bool):
        self.scrollable = bool(enabled)
        if not self.scrollable:
            self._scroll_y = 0.0
            self._scroll_target_y = 0.0
            self._max_scroll = 0.0
            self._scrollbar_dragging = False
        self.mark_layout_dirty()

    def set_smooth_scroll(self, enabled: bool):
        self.smooth_scroll = bool(enabled)
        if not self.smooth_scroll:
            self._scroll_target_y = self._scroll_y
        self.mark_layout_dirty()

    def set_scrollbar_visible(self, visible: bool):
        self.show_scrollbar = bool(visible)
        self.mark_layout_dirty()

    def _scrollbar_reservation(self):
        if self.scrollable and self.show_scrollbar:
            return self.scrollbar_width + 6
        return 0

    def _viewport_rect_local(self):
        viewport_w = max(1, self.rect[2] - self.padding * 2 - self._scrollbar_reservation())
        viewport_h = max(1, self.rect[3] - self.padding * 2)
        return pygame.Rect(self.padding, self.padding, viewport_w, viewport_h)

    def _viewport_rect_absolute(self):
        local = self._viewport_rect_local()
        return pygame.Rect(
            self.absolute_rect[0] + local.x,
            self.absolute_rect[1] + local.y,
            local.width,
            local.height,
        )

    def _set_content_height(self, content_height: int):
        self._content_height = max(0, int(content_height))
        viewport_h = self._viewport_rect_local().height
        self._max_scroll = float(max(0, self._content_height - viewport_h))
        self._scroll_y = max(0.0, min(self._scroll_y, self._max_scroll))
        self._scroll_target_y = max(0.0, min(self._scroll_target_y, self._max_scroll))

    def _set_scroll_y(self, value: float, sync_target: bool = True):
        clamped = max(0.0, min(float(value), self._max_scroll))
        if abs(clamped - self._scroll_y) > 1e-6:
            self._scroll_y = clamped
            self.mark_layout_dirty()
        if sync_target:
            self._scroll_target_y = clamped

    def _set_scroll_target(self, value: float):
        clamped = max(0.0, min(float(value), self._max_scroll))
        self._scroll_target_y = clamped
        self.mark_layout_dirty()

        if not self.smooth_scroll:
            self._set_scroll_y(clamped)

    def _tick_smooth_scroll(self):
        if not self.scrollable or not self.smooth_scroll:
            self._last_smooth_tick_ms = None
            return

        if self._scrollbar_dragging:
            self._scroll_target_y = self._scroll_y
            self._last_smooth_tick_ms = None
            return

        now_ms = pygame.time.get_ticks()
        if self._last_smooth_tick_ms is None:
            self._last_smooth_tick_ms = now_ms
            return

        dt = (now_ms - self._last_smooth_tick_ms) / 1000.0
        self._last_smooth_tick_ms = now_ms
        if dt <= 0:
            return

        delta = self._scroll_target_y - self._scroll_y
        if abs(delta) <= 1e-6:
            return

        # Child placement is pixel-based, so tiny sub-pixel tails look like
        # jitter near the end. Snap early for a cleaner finish.
        if abs(delta) <= self.smooth_snap_threshold:
            self._set_scroll_y(self._scroll_target_y, sync_target=False)
            return

        # Normalize smoothing to time so behavior remains stable across FPS.
        normalized_alpha = 1.0 - pow(1.0 - self.smooth_scroll_factor, max(1.0, dt * 60.0))
        # Avoid a long "creep" phase near target by increasing pull strength
        # once we are in the final stretch.
        if abs(delta) < 24.0:
            normalized_alpha = max(normalized_alpha, 0.42)
        step = delta * normalized_alpha

        next_value = self._scroll_y + step
        if delta > 0:
            next_value = min(next_value, self._scroll_target_y)
        else:
            next_value = max(next_value, self._scroll_target_y)

        self._set_scroll_y(next_value, sync_target=False)

    def _scroll_by(self, delta_y: int):
        if not self.scrollable or self._max_scroll <= 0:
            return
        if self.smooth_scroll:
            self._set_scroll_target(self._scroll_target_y + delta_y)
        else:
            self._set_scroll_y(self._scroll_y + delta_y)

    def _update_scrollbar_geometry(self):
        self._scrollbar_track_rect = pygame.Rect(0, 0, 0, 0)
        self._scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)

        if not (self.scrollable and self.show_scrollbar and self._max_scroll > 0):
            return

        viewport = self._viewport_rect_absolute()
        track_x = self.absolute_rect[0] + self.rect[2] - self.padding - self.scrollbar_width
        track_y = viewport.y
        track_h = viewport.height
        if track_h <= 0:
            return

        self._scrollbar_track_rect = pygame.Rect(track_x, track_y, self.scrollbar_width, track_h)

        total = max(1, self._content_height)
        visible = max(1, viewport.height)
        thumb_h = max(20, int(track_h * (visible / total)))
        thumb_h = min(track_h, thumb_h)

        travel = max(0, track_h - thumb_h)
        ratio = 0.0 if self._max_scroll <= 0 else (self._scroll_y / self._max_scroll)
        thumb_y = track_y + int(travel * ratio)
        self._scrollbar_thumb_rect = pygame.Rect(track_x, thumb_y, self.scrollbar_width, thumb_h)

    def _draw_scrollbar(self, surface: pygame.Surface):
        if not (self.scrollable and self.show_scrollbar and self._max_scroll > 0):
            return

        if self._scrollbar_track_rect.width <= 0 or self._scrollbar_thumb_rect.width <= 0:
            return

        pygame.draw.rect(surface, (220, 220, 220), self._scrollbar_track_rect, border_radius=4)
        thumb_color = (140, 140, 140) if not self._scrollbar_dragging else (110, 110, 110)
        pygame.draw.rect(surface, thumb_color, self._scrollbar_thumb_rect, border_radius=4)

    def get_children_clip_rect(self):
        if self.scrollable:
            return self._viewport_rect_absolute()

        return pygame.Rect(
            self.absolute_rect[0],
            self.absolute_rect[1],
            self.absolute_rect[2],
            self.absolute_rect[3],
        )

    def add_child(self, component: UIComponent):
        super().add_child(component)
        self.mark_layout_dirty()

    def mark_layout_dirty(self):
        self._layout_dirty = True
        if self.parent and isinstance(self.parent, LayoutContainer):
            self.parent.mark_layout_dirty()

    def layout_children(self):
        self._tick_smooth_scroll()

        if self._layout_dirty:
            self._layout_dirty = False
            self._do_layout()
            return

        # Even when layout is clean, parent absolute positions may change.
        # Keep child absolute rects synced without recomputing full layout.
        for child in self.children:
            child.update_absolute_rect()

    def _do_layout(self):
        """Override in subclasses."""
        raise NotImplementedError

    def draw(self, surface: pygame.Surface):
        self.layout_children()
        super().draw(surface)
        self._update_scrollbar_geometry()
        self._draw_scrollbar(surface)

    def handle_event(self, event: pygame.event.Event):
        if not self.visible or not self.enabled or not self.scrollable:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            button = getattr(event, "button", None)
            pos = getattr(event, "pos", None)

            if button in (4, 5):
                if pos and self._viewport_rect_absolute().collidepoint(pos):
                    direction = -1 if button == 4 else 1
                    self._scroll_by(direction * self.wheel_step)
                return

            if button == 1:
                self._update_scrollbar_geometry()

                if self._scrollbar_thumb_rect.collidepoint(pos):
                    self._scrollbar_dragging = True
                    self._scrollbar_drag_offset = pos[1] - self._scrollbar_thumb_rect.y
                    return

                if self._scrollbar_track_rect.collidepoint(pos):
                    if pos[1] < self._scrollbar_thumb_rect.y:
                        self._scroll_by(-self.wheel_step * 3)
                    else:
                        self._scroll_by(self.wheel_step * 3)
                    return

        elif event.type == pygame.MOUSEMOTION:
            if not self._scrollbar_dragging:
                return

            self._update_scrollbar_geometry()
            if self._max_scroll <= 0:
                self._scrollbar_dragging = False
                return

            track = self._scrollbar_track_rect
            thumb = self._scrollbar_thumb_rect
            travel = max(1, track.height - thumb.height)
            target_y = event.pos[1] - self._scrollbar_drag_offset
            clamped_y = max(track.y, min(target_y, track.bottom - thumb.height))
            ratio = (clamped_y - track.y) / travel
            self._set_scroll_y(ratio * self._max_scroll)
            return

        elif event.type == pygame.MOUSEBUTTONUP:
            if getattr(event, "button", None) == 1:
                self._scrollbar_dragging = False
                return

        elif event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if self._viewport_rect_absolute().collidepoint(mouse_pos):
                self._scroll_by(-event.y * self.wheel_step)
            return


class VBoxLayout(LayoutContainer):
    """Vertical box layout: stacks children from top to bottom."""

    def __init__(
        self,
        rect,
        spacing: int = 0,
        padding: int = 0,
        z_index: int = 0,
        color=None,
        border_color=None,
        align: str = "left",
        scrollable: bool = False,
        show_scrollbar: bool = True,
        smooth_scroll: bool = False,
        smooth_scroll_factor: float = 0.14,
        smooth_snap_threshold: float = 2.0,
    ):
        super().__init__(
            rect,
            spacing,
            padding,
            z_index,
            color,
            border_color,
            scrollable=scrollable,
            show_scrollbar=show_scrollbar,
            smooth_scroll=smooth_scroll,
            smooth_scroll_factor=smooth_scroll_factor,
            smooth_snap_threshold=smooth_snap_threshold,
        )
        self.align = align  # "left", "center", "right"

    def _do_layout(self):
        if not self.children:
            self._set_content_height(0)
            return

        visible_children = []
        for child in self.children:
            if child.visible:
                visible_children.append(child)

        measured_height = 0
        for child in visible_children:
            if hasattr(child, "get_layout_height"):
                measured_height += child.get_layout_height()
            elif len(child.rect) > 3:
                measured_height += child.rect[3]
            else:
                measured_height += 40

        if len(visible_children) > 1:
            measured_height += self.spacing * (len(visible_children) - 1)

        if self.scrollable:
            self._set_content_height(measured_height)
        else:
            self._set_content_height(0)

        container_width = self.rect[2] - 2 * self.padding - self._scrollbar_reservation()
        container_width = max(1, container_width)
        y_offset = int(round(self._scroll_y)) if self.scrollable else 0

        current_y = self.padding - y_offset

        for child in self.children:
            if not child.visible:
                continue

            if hasattr(child, "rect") and len(child.rect) >= 2:
                child_width = child.rect[2] if len(child.rect) > 2 else container_width
                if hasattr(child, "get_layout_height"):
                    child_height = child.get_layout_height()
                else:
                    child_height = child.rect[3] if len(child.rect) > 3 else 40

                if self.align == "center":
                    child_x = self.padding + (container_width - child_width) // 2
                elif self.align == "right":
                    child_x = self.padding + container_width - child_width
                else:
                    child_x = self.padding

                child_rect_height = child.rect[3] if len(child.rect) > 3 else child_height
                child.rect = (child_x, current_y, child_width, child_rect_height)
                child.update_absolute_rect()

                current_y += child_height + self.spacing


class HBoxLayout(LayoutContainer):
    """Horizontal box layout: stacks children from left to right."""

    def __init__(
        self,
        rect,
        spacing: int = 0,
        padding: int = 0,
        z_index: int = 0,
        color=None,
        border_color=None,
        align: str = "top",
        scrollable: bool = False,
        show_scrollbar: bool = True,
        smooth_scroll: bool = False,
        smooth_scroll_factor: float = 0.14,
        smooth_snap_threshold: float = 2.0,
    ):
        super().__init__(
            rect,
            spacing,
            padding,
            z_index,
            color,
            border_color,
            scrollable=scrollable,
            show_scrollbar=show_scrollbar,
            smooth_scroll=smooth_scroll,
            smooth_scroll_factor=smooth_scroll_factor,
            smooth_snap_threshold=smooth_snap_threshold,
        )
        self.align = align  # "top", "center", "bottom"

    def _do_layout(self):
        if not self.children:
            self._set_content_height(0)
            return

        container_width = self.rect[2] - 2 * self.padding - self._scrollbar_reservation()
        container_height = self.rect[3] - 2 * self.padding
        container_width = max(1, container_width)

        max_h = 0
        for child in self.children:
            if not child.visible:
                continue
            if hasattr(child, "get_layout_height"):
                child_h = child.get_layout_height()
            elif len(child.rect) > 3:
                child_h = child.rect[3]
            else:
                child_h = 40
            max_h = max(max_h, child_h)

        if self.scrollable:
            self._set_content_height(max_h)
        else:
            self._set_content_height(0)

        y_offset = int(round(self._scroll_y)) if self.scrollable else 0

        current_x = self.padding

        for child in self.children:
            if not child.visible:
                continue

            if hasattr(child, "rect") and len(child.rect) >= 2:
                child_width = child.rect[2] if len(child.rect) > 2 else 40
                child_height = child.rect[3] if len(child.rect) > 3 else container_height

                if self.align == "center":
                    child_y = self.padding + (container_height - child_height) // 2 - y_offset
                elif self.align == "bottom":
                    child_y = self.padding + container_height - child_height - y_offset
                else:
                    child_y = self.padding - y_offset

                child.rect = (current_x, child_y, child_width, child_height)
                child.update_absolute_rect()

                current_x += child_width + self.spacing


class CollapsibleContainer(VBoxLayout):
    """Accordion-style container with header and collapsible content."""

    def __init__(
        self,
        rect,
        title: str = "Section",
        spacing: int = 0,
        padding: int = 10,
        z_index: int = 0,
        color=(200, 200, 200),
        border_color=(100, 100, 100),
        header_height: int = 32,
        collapsed: bool = False,
        animation_duration: float = 0.16,
        show_body_when_collapsed: bool = True,
    ):
        super().__init__(rect, spacing, padding, z_index, color, border_color)

        self.title = title
        self.header_height = header_height
        self.collapsed = collapsed
        self.animation_duration = animation_duration
        self.show_body_when_collapsed = show_body_when_collapsed

        self.content_height = 0
        self.animated_height_ratio = 0.0 if collapsed else 1.0

        self._header_rect = pygame.Rect(self.rect[0], self.rect[1], self.rect[2], header_height)

    def _on_animation_update(self, _):
        self.mark_layout_dirty()

    def toggle(self, animated: bool = True):
        self.collapsed = not self.collapsed
        target_ratio = 0.0 if self.collapsed else 1.0

        if animated and self.ui_manager is not None:
            self.ui_manager.animation_manager.animate_attr(
                target=self,
                attr_name="animated_height_ratio",
                to_value=target_ratio,
                duration=self.animation_duration,
                easing=Easing.linear,
                on_update=self._on_animation_update,
                key=(id(self), "collapse_height"),
            )
        else:
            self.animated_height_ratio = target_ratio

        self.mark_layout_dirty()

        if self.parent and isinstance(self.parent, LayoutContainer):
            self.parent.mark_layout_dirty()

    def on_click(self, event):
        if self._header_rect.collidepoint(event.pos):
            self.toggle(animated=True)

    def set_position(self, x: int, y: int):
        self.rect = (x, y, self.rect[2], self.rect[3])
        self._header_rect.x = x
        self._header_rect.y = y
        self.update_absolute_rect()

    def _measure_content_height(self):
        total = 0
        for child in self.children:
            if not child.visible:
                continue

            if hasattr(child, "get_layout_height"):
                child_height = child.get_layout_height()
            elif hasattr(child, "rect") and len(child.rect) > 3:
                child_height = child.rect[3]
            else:
                child_height = 40

            total += child_height + self.spacing

        if total > 0:
            total -= self.spacing

        return total

    def _contains_component(self, root_component, target_component):
        if root_component is target_component:
            return True

        for child in root_component.children:
            if self._contains_component(child, target_component):
                return True

        return False

    def get_layout_height(self):
        self.content_height = self._measure_content_height()
        visible_content = round(self.content_height * self.animated_height_ratio)

        if self.animated_height_ratio <= 0.001 and not self.show_body_when_collapsed:
            return self.header_height

        return self.header_height + (2 * self.padding) + visible_content

    def _do_layout(self):
        if not self.children:
            return

        self.content_height = self._measure_content_height()
        visible_height = round(self.content_height * self.animated_height_ratio)

        current_y = 0
        for child in self.children:
            if not child.visible:
                continue

            if hasattr(child, "rect") and len(child.rect) > 3:
                child_width = child.rect[2]
                child_rect_height = child.rect[3]
                if hasattr(child, "get_layout_height"):
                    child_layout_height = child.get_layout_height()
                else:
                    child_layout_height = child_rect_height

                child_y = self.header_height + self.padding + current_y

                child.rect = (self.padding, child_y, child_width, child_rect_height)
                child.update_absolute_rect()

                current_y += child_layout_height + self.spacing

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        self.layout_children()

        area_height = self.get_layout_height()
        area_rect = pygame.Rect(
            self.absolute_rect[0],
            self.absolute_rect[1],
            self.absolute_rect[2],
            area_height,
        )

        content_rect = pygame.Rect(
            self.absolute_rect[0],
            self.absolute_rect[1] + self.header_height,
            self.absolute_rect[2],
            max(0, area_height - self.header_height),
        )
        if content_rect.height > 0:
            pygame.draw.rect(surface, (245, 245, 245), content_rect, border_radius=5)

        self._header_rect.width = self.absolute_rect[2]
        self._header_rect.x = self.absolute_rect[0]
        self._header_rect.y = self.absolute_rect[1]

        pygame.draw.rect(surface, self.color, self._header_rect, border_radius=5)
        pygame.draw.rect(surface, self.border_color, self._header_rect, 2, border_radius=5)

        text_color = (0, 0, 0)
        text = self.title

        indicator_size = max(6, int(self.header_height * 0.22))
        indicator_cx = self._header_rect.x + 16
        indicator_cy = self._header_rect.centery

        try:
            font_size = max(16, int(self.header_height * 0.62))
            font = pygame.font.Font(None, font_size)
            text_surface = font.render(text, True, text_color)
            text_x = indicator_cx + indicator_size + 8
            text_y = self._header_rect.y + (self._header_rect.height - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
        except Exception:
            pass

        if self.animated_height_ratio <= 0.5:
            indicator_points = [
                (indicator_cx - indicator_size // 2, indicator_cy - indicator_size),
                (indicator_cx - indicator_size // 2, indicator_cy + indicator_size),
                (indicator_cx + indicator_size, indicator_cy),
            ]
        else:
            indicator_points = [
                (indicator_cx - indicator_size, indicator_cy - indicator_size // 2),
                (indicator_cx + indicator_size, indicator_cy - indicator_size // 2),
                (indicator_cx, indicator_cy + indicator_size),
            ]

        pygame.draw.polygon(surface, text_color, indicator_points)

        pygame.draw.rect(surface, self.border_color, area_rect, 2, border_radius=5)

        clip_rect = pygame.Rect(
            self.absolute_rect[0],
            self.absolute_rect[1] + self.header_height + self.padding,
            self.absolute_rect[2],
            max(0, round(self.content_height * self.animated_height_ratio)),
        )
        old_clip = surface.get_clip()
        effective_clip = clip_rect.clip(old_clip)
        surface.set_clip(effective_clip)

        modal_component = self.ui_manager.modal if self.ui_manager is not None else None
        deferred_draw = []

        if effective_clip.width > 0 and effective_clip.height > 0:
            for child in sorted(self.children, key=lambda c: c.z_index):
                if not child.visible:
                    continue

                if modal_component is not None and self._contains_component(child, modal_component):
                    deferred_draw.append(child)
                    continue

                child.draw(surface)

        surface.set_clip(old_clip)

        for child in deferred_draw:
            child.draw(surface)
