"""Unit tests for CodeEditor widget."""
import pygame
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pygame_widget_kit.CodeEditor import CodeEditor


@pytest.mark.unit
class TestCodeEditor:
    def test_default_python_keyword_highlight_style(self):
        editor = CodeEditor(rect=pygame.Rect(0, 0, 400, 180), initial_text="for i in items:")

        style = editor._resolve_token_style("for")

        assert style.bold is True
        assert style.color != editor.default_style.color

    def test_custom_keyword_style_supports_color_bold_italic(self):
        editor = CodeEditor(
            rect=pygame.Rect(0, 0, 400, 180),
            keyword_styles={
                "for": {
                    "color": (255, 0, 0),
                    "bold": True,
                    "italic": True,
                }
            },
            default_style={"color": (0, 0, 0)},
        )

        style = editor._resolve_token_style("for")
        assert style.color == (255, 0, 0)
        assert style.bold is True
        assert style.italic is True

    def test_draw_renders_with_highlighting_without_error(self, display_surface):
        editor = CodeEditor(
            rect=pygame.Rect(10, 10, 500, 200),
            initial_text="for idx in range(10):\n    print(idx)",
            show_scrollbars=True,
        )
        editor.focused = True

        editor.draw(display_surface)

        assert True

    def test_autocomplete_provider_contract(self):
        calls = {}

        def provider(full_text, cursor_pos, prefix):
            calls["full_text"] = full_text
            calls["cursor_pos"] = cursor_pos
            calls["prefix"] = prefix
            return ["for", "format", "from"]

        editor = CodeEditor(rect=pygame.Rect(0, 0, 500, 160), initial_text="fo")
        editor.set_autocomplete_provider(provider)
        editor.cursor_line = 0
        editor.cursor_col = 2

        items = editor.request_completions()

        assert calls["full_text"] == "fo"
        assert calls["cursor_pos"] == (0, 2)
        assert calls["prefix"] == "fo"
        assert items == ["for", "format", "from"]

    def test_repeated_delete_is_grouped_in_single_undo(self):
        editor = CodeEditor(rect=pygame.Rect(0, 0, 500, 160), initial_text="hello")
        editor.focused = True

        backspace_event = pygame.event.Event(
            pygame.KEYDOWN,
            {"key": pygame.K_BACKSPACE, "unicode": "", "mod": 0},
        )
        undo_event = pygame.event.Event(
            pygame.KEYDOWN,
            {"key": pygame.K_z, "unicode": "", "mod": pygame.KMOD_CTRL},
        )

        editor.handle_event(backspace_event)
        editor.handle_event(backspace_event)
        editor.handle_event(backspace_event)

        assert editor.get_text() == "he"

        editor.handle_event(undo_event)

        assert editor.get_text() == "hello"
