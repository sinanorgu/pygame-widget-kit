"""Tests for ToggleButton widget."""
import pygame
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pygame_widget_kit.ToggleButton import ToggleButton


@pytest.mark.unit
class TestToggleButton:
    """Test ToggleButton widget functionality."""

    def test_toggle_button_initialization(self):
        """Test that ToggleButton initializes correctly."""
        toggle = ToggleButton(
            pos=(10, 10),
            size=(50, 50)
        )
        
        assert toggle is not None
        assert toggle.enabled is True

    def test_toggle_button_toggled_state(self):
        """Test toggling the button."""
        toggle = ToggleButton(pos=(10, 10), size=(50, 50))
        
        # Initial state
        initial_state = toggle.active
        
        # Toggle state
        toggle.active = not initial_state
        assert toggle.active == (not initial_state)

    def test_toggle_button_visibility(self):
        """Test toggle button visibility."""
        toggle = ToggleButton(pos=(10, 10), size=(50, 50))
        
        assert toggle.visible is True
        toggle.visible = False
        assert toggle.visible is False

    def test_toggle_button_enabled_disabled(self):
        """Test enabling/disabling toggle button."""
        toggle = ToggleButton(pos=(10, 10), size=(50, 50))
        
        assert toggle.enabled is True
        toggle.enabled = False
        assert toggle.enabled is False

    def test_toggle_button_hover_state(self):
        """Test toggle button hover state."""
        toggle = ToggleButton(pos=(10, 10), size=(50, 50))
        
        assert toggle.hovered is False
        toggle.hovered = True
        assert toggle.hovered is True
