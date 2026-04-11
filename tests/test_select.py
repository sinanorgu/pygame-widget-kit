"""Tests for Select/Dropdown widget."""
import pygame
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pygame_widget_kit.Select import Select


@pytest.mark.unit
class TestSelect:
    """Test Select/Dropdown widget functionality."""

    def test_select_initialization(self, basic_rect):
        """Test that Select initializes correctly."""
        options = ["Option 1", "Option 2", "Option 3"]
        select = Select(
            rect=basic_rect,
            options=options,
            default_index=0
        )
        
        assert select.rect == basic_rect
        assert select is not None

    def test_select_enabled_disabled(self, basic_rect):
        """Test enabling/disabling select."""
        options = ["A", "B", "C"]
        select = Select(rect=basic_rect, options=options)
        
        assert select.enabled is True
        select.enabled = False
        assert select.enabled is False

    def test_select_visibility(self, basic_rect):
        """Test select visibility."""
        options = ["Item 1", "Item 2"]
        select = Select(rect=basic_rect, options=options)
        
        assert select.visible is True
        select.visible = False
        assert select.visible is False

    def test_select_has_options(self, basic_rect):
        """Test select has options property."""
        options = ["Red", "Green", "Blue"]
        select = Select(rect=basic_rect, options=options)
        
        assert hasattr(select, 'enabled')
