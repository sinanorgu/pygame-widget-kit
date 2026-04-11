"""Tests for TextArea widget."""
import pygame
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pygame_widget_kit.TextArea import TextArea


@pytest.mark.unit
class TestTextArea:
    """Test TextArea widget functionality."""

    def test_textarea_initialization(self, basic_rect):
        """Test that TextArea initializes correctly."""
        textarea = TextArea(rect=basic_rect)
        
        assert textarea.rect == basic_rect
        assert textarea.enabled is True

    def test_textarea_visibility(self, basic_rect):
        """Test textarea visibility."""
        textarea = TextArea(rect=basic_rect)
        
        assert textarea.visible is True
        textarea.visible = False
        assert textarea.visible is False

    def test_textarea_enabled_disabled(self, basic_rect):
        """Test enabling/disabling textarea."""
        textarea = TextArea(rect=basic_rect)
        
        assert textarea.enabled is True
        textarea.enabled = False
        assert textarea.enabled is False

    def test_textarea_is_component(self, basic_rect):
        """Test that TextArea is a valid component."""
        textarea = TextArea(rect=basic_rect)
        
        assert hasattr(textarea, 'rect')
        assert hasattr(textarea, 'visible')
        assert hasattr(textarea, 'enabled')
        assert hasattr(textarea, 'focused')
