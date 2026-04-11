"""Unit tests for TextInput widget."""
import pygame
import pytest
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pygame_widget_kit.TextInput import (
    ALLOW_ALL_CHARS,
    BINARY_ONLY,
    HEX_ONLY,
    NUMBER_ONLY,
    OCTAL_ONLY,
    TEXT_ONLY,
    TextInput,
    TextInput2D,
)
from pygame_widget_kit.UIComponent import UIComponent


class _FakeManager:
    def __init__(self):
        self.root = UIComponent(pygame.Rect(0, 0, 800, 600))
        self.focused = None
        self.modal = None


def _x_for_index(widget: TextInput, index: int) -> int:
    width = widget.text.font.size(widget.text_value[:index])[0]
    return int(widget.absolute_rect[0] + widget.padding + width - widget._scroll_x + 1)


def _key_event(key, unicode="", mod=0):
    return pygame.event.Event(pygame.KEYDOWN, {"key": key, "unicode": unicode, "mod": mod})


@pytest.mark.unit
class TestTextInput:
    """Test TextInput widget functionality."""

    def test_textinput_initialization(self, basic_rect):
        """Test that TextInput initializes correctly."""
        text_input = TextInput(
            rect=basic_rect,
            initial_text="",
            text_color=(0, 0, 0),
            bg_color=(255, 255, 255)
        )
        
        assert text_input.rect == basic_rect
        assert text_input.text_value == ""
        assert text_input.text_color == (0, 0, 0)

    def test_textinput_text_input(self, basic_rect):
        """Test inputting text into TextInput."""
        text_input = TextInput(rect=basic_rect)
        text_input.text_value = "Hello"
        
        assert text_input.text_value == "Hello"

    def test_textinput_clear(self, basic_rect):
        """Test clearing TextInput."""
        text_input = TextInput(rect=basic_rect)
        text_input.text_value = "Some text"
        text_input.text_value = ""
        
        assert text_input.text_value == ""

    def test_textinput_focused_state(self, basic_rect):
        """Test TextInput focused state."""
        text_input = TextInput(rect=basic_rect)
        
        assert text_input.focused is False
        text_input.focused = True
        assert text_input.focused is True

    def test_textinput_enabled_disabled(self, basic_rect):
        """Test TextInput enabled/disabled state."""
        text_input = TextInput(rect=basic_rect)
        
        assert text_input.enabled is True
        text_input.enabled = False
        assert text_input.enabled is False

    def test_textinput_cursor_position(self, basic_rect):
        """Test cursor index in TextInput."""
        text_input = TextInput(rect=basic_rect, initial_text="test")
        
        # Cursor should start at the end of text
        assert text_input.cursor_index == len(text_input.text_value)

    def test_textinput_auto_horizontal_scroll_when_text_overflows(self):
        """TextInput should scroll horizontally when caret goes out of visible area."""
        text_input = TextInput(rect=pygame.Rect(0, 0, 120, 32), initial_text="x" * 120)

        text_input.cursor_index = len(text_input.text_value)
        text_input._ensure_cursor_visible()

        assert text_input._scroll_x > 0

    def test_character_insert_and_backspace(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 220, 40), initial_text="ab")
        widget.focused = True

        widget.handle_event(_key_event(pygame.K_c, unicode="c"))
        assert widget.text_value == "abc"

        widget.handle_event(_key_event(pygame.K_BACKSPACE))
        assert widget.text_value == "ab"

    def test_replace_selection_on_typing(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 260, 40), initial_text="hello world")
        widget.focused = True
        widget.selection_start = 0
        widget.selection_end = 5
        widget.cursor_index = 5

        widget.handle_event(_key_event(pygame.K_x, unicode="x"))

        assert widget.text_value == "x world"
        assert widget.cursor_index == 1
        assert widget.has_selection() is False

    def test_caret_blink_toggles_after_interval(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 220, 40), initial_text="abc")
        widget.focused = True
        widget.last_blinked_at = 0.0
        widget.caret_visible = True
        widget.update()

        assert widget.caret_visible is False

    def test_mouse_drag_selection(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), initial_text="hello world")
        widget.focused = True

        start_x = _x_for_index(widget, 2)
        end_x = _x_for_index(widget, 6)

        widget.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (start_x, 10), "button": 1}))
        widget.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {"pos": (end_x, 10)}))
        widget.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (end_x, 10), "button": 1}))

        assert widget.has_selection() is True
        start, end = widget.get_selection_range()
        assert end > start
        assert widget.dragging is False

    def test_shift_arrow_expands_and_shrinks_selection(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), initial_text="abcdef")
        widget.focused = True
        widget.cursor_index = 2

        widget.handle_event(_key_event(pygame.K_RIGHT, mod=pygame.KMOD_SHIFT))
        assert widget.get_selection_range() == [2, 3]

        widget.handle_event(_key_event(pygame.K_LEFT, mod=pygame.KMOD_SHIFT))
        assert widget.has_selection() is False
        assert widget.cursor_index == 2

    def test_shift_click_selects_from_anchor(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), initial_text="abcdef")
        widget.focused = True
        widget.cursor_index = 1

        click_x = _x_for_index(widget, 4)
        widget.handle_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"pos": (click_x, 10), "button": 1, "mod": pygame.KMOD_SHIFT},
            )
        )

        assert widget.get_selection_range() == [1, 5]

    def test_double_click_selects_word(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 420, 40), initial_text="hello world")
        widget.focused = True
        pos_x = _x_for_index(widget, 7)
        now = time.time()
        widget._last_click_time = now
        widget._last_click_pos = (pos_x, 10)
        widget._click_count = 1

        widget.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (pos_x, 10), "button": 1}))

        assert widget.get_selected_text() == "world"

    def test_triple_click_selects_all(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 420, 40), initial_text="hello world")
        widget.focused = True
        pos_x = _x_for_index(widget, 3)
        now = time.time()
        widget._last_click_time = now
        widget._last_click_pos = (pos_x, 10)
        widget._click_count = 2

        widget.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (pos_x, 10), "button": 1}))

        assert widget.get_selection_range() == [0, len(widget.text_value)]

    def test_selection_collapses_on_right_left_without_shift(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), initial_text="abcdef")
        widget.focused = True
        widget.selection_start = 1
        widget.selection_end = 4
        widget.cursor_index = 4

        widget.handle_event(_key_event(pygame.K_RIGHT))
        assert widget.has_selection() is False
        assert widget.cursor_index == 4

        widget.selection_start = 1
        widget.selection_end = 4
        widget.cursor_index = 4
        widget.handle_event(_key_event(pygame.K_LEFT))
        assert widget.has_selection() is False
        assert widget.cursor_index == 1

    def test_escape_clears_selection(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), initial_text="abcdef")
        widget.focused = True
        widget.selection_start = 1
        widget.selection_end = 4

        widget.handle_event(_key_event(pygame.K_ESCAPE))
        assert widget.has_selection() is False

    def test_clipboard_shortcuts_invoke_expected_methods(self, monkeypatch):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), initial_text="abcdef")
        widget.focused = True
        called = {"copy": 0, "paste": 0, "cut": 0, "undo": 0, "redo": 0}

        monkeypatch.setattr(widget, "copy_selected_text", lambda: called.__setitem__("copy", called["copy"] + 1))
        monkeypatch.setattr(widget, "paste_from_clipboard", lambda: called.__setitem__("paste", called["paste"] + 1))
        monkeypatch.setattr(widget, "cut_selected_text", lambda: called.__setitem__("cut", called["cut"] + 1))
        monkeypatch.setattr(widget, "undo", lambda: called.__setitem__("undo", called["undo"] + 1))
        monkeypatch.setattr(widget, "redo", lambda: called.__setitem__("redo", called["redo"] + 1))

        widget.handle_event(_key_event(pygame.K_c, mod=pygame.KMOD_CTRL))
        widget.handle_event(_key_event(pygame.K_v, mod=pygame.KMOD_CTRL))
        widget.handle_event(_key_event(pygame.K_x, mod=pygame.KMOD_CTRL))
        widget.handle_event(_key_event(pygame.K_z, mod=pygame.KMOD_CTRL))
        widget.handle_event(_key_event(pygame.K_z, mod=pygame.KMOD_CTRL | pygame.KMOD_SHIFT))
        widget.handle_event(_key_event(pygame.K_y, mod=pygame.KMOD_CTRL))

        assert called == {"copy": 1, "paste": 1, "cut": 1, "undo": 1, "redo": 2}

    def test_select_all_shortcut_ctrl_a(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), initial_text="abcdef")
        widget.focused = True

        widget.handle_event(_key_event(pygame.K_a, mod=pygame.KMOD_CTRL))
        assert widget.get_selection_range() == [0, 6]

    def test_undo_redo_snapshot_and_history_limit(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), initial_text="")
        widget._max_history = 3

        for ch in "abcd":
            widget._record_undo_state()
            widget.insert_text(ch, record_history=False)

        assert len(widget._undo_stack) <= 3

        last_text = widget.text_value
        widget.undo()
        assert widget.text_value != last_text

        undo_text = widget.text_value
        widget.redo()
        assert widget.text_value != undo_text

    def test_typing_burst_groups_word_chars_in_undo(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), initial_text="")
        widget.focused = True

        widget.handle_event(_key_event(pygame.K_a, unicode="a"))
        widget.handle_event(_key_event(pygame.K_b, unicode="b"))
        widget.handle_event(_key_event(pygame.K_c, unicode="c"))

        assert widget.text_value == "abc"
        assert len(widget._undo_stack) == 1

    def test_cursor_navigation_word_and_line_modifiers(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 420, 40), initial_text="hello world test")
        widget.focused = True
        widget.cursor_index = 0

        widget.handle_event(_key_event(pygame.K_RIGHT, mod=pygame.KMOD_CTRL))
        assert widget.cursor_index == 6

        widget.handle_event(_key_event(pygame.K_RIGHT, mod=pygame.KMOD_META))
        assert widget.cursor_index == len(widget.text_value)

        widget.handle_event(_key_event(pygame.K_LEFT, mod=pygame.KMOD_META))
        assert widget.cursor_index == 0

        widget.handle_event(_key_event(pygame.K_DOWN))
        assert widget.cursor_index == len(widget.text_value)

        widget.handle_event(_key_event(pygame.K_UP))
        assert widget.cursor_index == 0

    def test_advanced_delete_behaviors(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 460, 40), initial_text="hello world test")
        widget.focused = True
        widget.cursor_index = len(widget.text_value)

        widget.handle_event(_key_event(pygame.K_BACKSPACE, mod=pygame.KMOD_CTRL))
        assert widget.text_value == "hello world "

        widget.handle_event(_key_event(pygame.K_BACKSPACE, mod=pygame.KMOD_META))
        assert widget.text_value == ""

        widget.insert_text("abc def")
        widget.cursor_index = 0
        widget.handle_event(_key_event(pygame.K_DELETE, mod=pygame.KMOD_CTRL))
        assert widget.text_value == "def"

        widget.handle_event(_key_event(pygame.K_DELETE, mod=pygame.KMOD_META))
        assert widget.text_value == ""

    def test_delete_with_selection_has_priority(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), initial_text="abcdef")
        widget.focused = True
        widget.selection_start = 1
        widget.selection_end = 4
        widget.cursor_index = 4

        widget.handle_event(_key_event(pygame.K_DELETE))

        assert widget.text_value == "aef"
        assert widget.has_selection() is False

    @pytest.mark.parametrize(
        "mode,typed,expected",
        [
            (ALLOW_ALL_CHARS, "a1F", "a1F"),
            (NUMBER_ONLY, "a1F", "1"),
            (TEXT_ONLY, "a1F", "aF"),
            (HEX_ONLY, "g1Fz", "1F"),
            (BINARY_ONLY, "10210", "1010"),
            (OCTAL_ONLY, "012389", "0123"),
        ],
    )
    def test_character_filter_modes_for_typing(self, mode, typed, expected):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), allowed_char_mode=mode)
        widget.focused = True

        for ch in typed:
            widget.handle_event(_key_event(ord(ch.lower()) if ch.isalpha() else pygame.K_0, unicode=ch))

        assert widget.text_value == expected

    @pytest.mark.parametrize(
        "mode,paste_text,expected",
        [
            (ALLOW_ALL_CHARS, "a1F", "a1F"),
            (NUMBER_ONLY, "a1F", "1"),
            (TEXT_ONLY, "a1F", "aF"),
            (HEX_ONLY, "g1Fz", "1F"),
            (BINARY_ONLY, "10210", "1010"),
            (OCTAL_ONLY, "012389", "0123"),
        ],
    )
    def test_character_filter_modes_for_paste(self, monkeypatch, mode, paste_text, expected):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), allowed_char_mode=mode)
        widget.focused = True
        monkeypatch.setattr(widget, "_get_os_clipboard_text", lambda: paste_text)
        monkeypatch.setattr(widget, "_ensure_scrap", lambda: False)

        widget.paste_from_clipboard()
        assert widget.text_value == expected

    def test_clipboard_cache_fallback_is_used(self, monkeypatch):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), initial_text="")
        widget.focused = True
        widget._clipboard_cache = "cached"
        monkeypatch.setattr(widget, "_get_os_clipboard_text", lambda: None)
        monkeypatch.setattr(widget, "_ensure_scrap", lambda: False)

        widget.paste_from_clipboard()
        assert widget.text_value == "cached"

    def test_context_menu_copy_paste_and_focus_restore(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 360, 40), initial_text="hello")
        manager = _FakeManager()
        widget.ui_manager = manager
        manager.focused = UIComponent(pygame.Rect(0, 0, 10, 10))

        right_click_x = _x_for_index(widget, 2)
        widget.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (right_click_x, 10), "button": 3}))

        assert widget.context_menu is not None
        assert manager.modal is widget.context_menu

        widget._context_click_index = 1
        widget.selection_start = widget.selection_end = None
        widget.prepare_context_action_for_paste()

        assert manager.focused is widget
        assert widget.cursor_index == 1

    def test_padding_inner_rect_and_clip_restore_in_draw(self, display_surface):
        widget = TextInput(rect=pygame.Rect(20, 20, 180, 40), initial_text="hello")
        widget.focused = True
        widget.selection_start = 0
        widget.selection_end = 3

        inner = widget._get_inner_rect()
        assert inner.x == widget.absolute_rect[0] + widget.padding
        assert inner.y == widget.absolute_rect[1] + widget.padding

        old_clip = display_surface.get_clip()
        widget.draw(display_surface)
        assert display_surface.get_clip() == old_clip

    def test_no_edit_when_not_focused(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 320, 40), initial_text="abc")
        widget.focused = False

        widget.handle_event(_key_event(pygame.K_d, unicode="d"))
        assert widget.text_value == "abc"

    def test_drag_state_starts_and_ends(self):
        widget = TextInput(rect=pygame.Rect(0, 0, 320, 40), initial_text="abcdef")
        widget.focused = True

        start_x = _x_for_index(widget, 1)
        end_x = _x_for_index(widget, 3)
        widget.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (start_x, 10), "button": 1}))
        assert widget.dragging is True

        widget.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {"pos": (end_x, 10)}))
        widget.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (end_x, 10), "button": 1}))
        assert widget.dragging is False


@pytest.mark.unit
class TestTextInput2D:
    """Test advanced 2D text input and scrollbar behaviors."""

    def test_vertical_scrollbar_appears_on_line_overflow(self):
        """Vertical scrollbar should appear when content exceeds available height."""
        long_text = "\n".join(["line"] * 40)
        widget = TextInput2D(
            rect=pygame.Rect(0, 0, 180, 90),
            initial_text=long_text,
            show_scrollbars=True,
        )

        geometry = widget._get_scrollbar_geometry()
        assert geometry["show_v"] is True
        assert geometry["v_thumb"] is not None

    def test_horizontal_scrollbar_appears_on_text_overflow(self):
        """Horizontal scrollbar should appear when a line is wider than available width."""
        widget = TextInput2D(
            rect=pygame.Rect(0, 0, 120, 90),
            initial_text="W" * 200,
            show_scrollbars=True,
        )

        geometry = widget._get_scrollbar_geometry()
        assert geometry["show_h"] is True
        assert geometry["h_thumb"] is not None

    def test_auto_scroll_moves_horizontally_while_typing(self):
        """Caret visibility logic should move horizontal scroll when typing long lines."""
        widget = TextInput2D(
            rect=pygame.Rect(0, 0, 120, 80),
            initial_text="",
            show_scrollbars=True,
        )
        widget.focused = True

        widget.insert_text("A" * 220)
        widget._ensure_cursor_visible()

        assert widget._scroll_x > 0

    def test_auto_scroll_moves_vertically_for_bottom_caret(self):
        """Caret visibility should move vertical scroll for long multi-line content."""
        long_text = "\n".join([f"line {i}" for i in range(60)])
        widget = TextInput2D(
            rect=pygame.Rect(0, 0, 180, 100),
            initial_text=long_text,
            show_scrollbars=True,
        )

        widget._ensure_cursor_visible()
        assert widget._scroll_y > 0

    def test_vertical_scrollbar_drag_changes_scroll_position(self):
        """Dragging vertical scrollbar thumb should change scroll position."""
        long_text = "\n".join([f"line {i}" for i in range(80)])
        widget = TextInput2D(
            rect=pygame.Rect(0, 0, 180, 100),
            initial_text=long_text,
            show_scrollbars=True,
        )

        geometry = widget._get_scrollbar_geometry()
        thumb = geometry["v_thumb"]
        assert thumb is not None

        start_y = widget._scroll_y
        down_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": thumb.center, "button": 1},
        )
        move_event = pygame.event.Event(
            pygame.MOUSEMOTION,
            {"pos": (thumb.centerx, thumb.centery + 25)},
        )
        up_event = pygame.event.Event(
            pygame.MOUSEBUTTONUP,
            {"pos": (thumb.centerx, thumb.centery + 25), "button": 1},
        )

        widget.handle_event(down_event)
        widget.handle_event(move_event)
        widget.handle_event(up_event)

        assert widget._scroll_y >= start_y
        assert widget._scroll_drag_mode is None

    def test_mousewheel_scroll_changes_vertical_offset(self):
        """Mouse wheel should move vertical scroll when focused."""
        long_text = "\n".join([f"line {i}" for i in range(80)])
        widget = TextInput2D(
            rect=pygame.Rect(0, 0, 180, 100),
            initial_text=long_text,
            show_scrollbars=True,
        )
        widget.focused = True

        start_y = widget._scroll_y
        wheel_event = pygame.event.Event(pygame.MOUSEWHEEL, {"y": -1})
        widget.handle_event(wheel_event)

        assert widget._scroll_y > start_y
