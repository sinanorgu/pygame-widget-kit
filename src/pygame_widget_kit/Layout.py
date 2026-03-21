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

    def add_child(self, component: UIComponent):
        super().add_child(component)
        self._layout_dirty = True

    def mark_layout_dirty(self):
        self._layout_dirty = True
        if self.parent and isinstance(self.parent, LayoutContainer):
            self.parent.mark_layout_dirty()

    def layout_children(self):
        if not self._layout_dirty:
            self._do_layout()
            return
        self._layout_dirty = False
        self._do_layout()

    def _do_layout(self):
        """Override in subclasses."""
        raise NotImplementedError

    def draw(self, surface: pygame.Surface):
        self.layout_children()
        super().draw(surface)


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
    ):
        super().__init__(rect, spacing, padding, z_index, color, border_color)
        self.align = align  # "left", "center", "right"

    def _do_layout(self):
        if not self.children:
            return

        container_width = self.rect[2] - 2 * self.padding
        container_height = self.rect[3] - 2 * self.padding

        current_y = self.padding

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
    ):
        super().__init__(rect, spacing, padding, z_index, color, border_color)
        self.align = align  # "top", "center", "bottom"

    def _do_layout(self):
        if not self.children:
            return

        container_width = self.rect[2] - 2 * self.padding
        container_height = self.rect[3] - 2 * self.padding

        current_x = self.padding

        for child in self.children:
            if not child.visible:
                continue

            if hasattr(child, "rect") and len(child.rect) >= 2:
                child_width = child.rect[2] if len(child.rect) > 2 else 40
                child_height = child.rect[3] if len(child.rect) > 3 else container_height

                if self.align == "center":
                    child_y = self.padding + (container_height - child_height) // 2
                elif self.align == "bottom":
                    child_y = self.padding + container_height - child_height
                else:
                    child_y = self.padding

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
            if hasattr(child, "rect") and len(child.rect) > 3:
                total += child.rect[3] + self.spacing

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
                child_height = child.rect[3]

                child_y = self.header_height + self.padding + current_y

                child.rect = (self.padding, child_y, child_width, child_height)
                child.update_absolute_rect()

                current_y += child_height + self.spacing

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
        surface.set_clip(clip_rect)

        modal_component = self.ui_manager.modal if self.ui_manager is not None else None
        deferred_draw = []

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
