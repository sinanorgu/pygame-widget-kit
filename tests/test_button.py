"""Unit tests for Button widget."""
import pygame
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pygame_widget_kit.Button import Button


@pytest.mark.unit
class TestButton:
    """Test Button widget functionality."""

    def test_button_initialization(self):
        """Test that Button initializes correctly."""
        button = Button(
            text_str="Click me",
            pos=(10, 10),
            size=(100, 50),
            text_color=(0, 0, 0),
            color=(200, 200, 200)
        )
        
        assert button.text_str == "Click me"
        assert button.text_color == (0, 0, 0)
        assert button.color == (200, 200, 200)
        assert button.size == (100, 50)

    def test_button_text_update(self):
        """Test updating button text."""
        button = Button(text_str="Original")
        button.text_str = "Updated"
        
        assert button.text_str == "Updated"

    def test_button_enabled_disabled(self):
        """Test button enabled/disabled state."""
        button = Button(text_str="Click")
        
        assert button.enabled is True
        button.enabled = False
        assert button.enabled is False

    def test_button_hovering(self):
        """Test button hover state."""
        button = Button(text_str="Hover")
        
        assert button.hovered is False
        button.hovered = True
        assert button.hovered is True

    def test_button_active_state(self):
        """Test button active/pressed state."""
        button = Button(text_str="Press")
        
        assert button.active is False
        button.active = True
        assert button.active is True
