"""Tests for Slider widget."""
import pygame
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pygame_widget_kit.Slider import Slider


@pytest.mark.unit
class TestSlider:
    """Test Slider widget functionality."""

    def test_slider_initialization(self):
        """Test that Slider initializes correctly."""
        slider = Slider(pos=(10, 10), size=(200, 20))
        
        assert slider is not None
        assert slider.enabled is True

    def test_slider_value_range(self):
        """Test slider min/max values."""
        slider = Slider(pos=(10, 10), size=(200, 20), min_value=0, max_value=100)
        
        assert slider.min_value == 0
        assert slider.max_value == 100
        assert slider.enabled is True

    def test_slider_disabled(self):
        """Test disabling slider."""
        slider = Slider(pos=(10, 10), size=(200, 20))
        slider.enabled = False
        
        assert slider.enabled is False

    def test_slider_visibility(self):
        """Test slider visibility."""
        slider = Slider(pos=(10, 10), size=(200, 20))
        
        assert slider.visible is True
        slider.visible = False
        assert slider.visible is False
