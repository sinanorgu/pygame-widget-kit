"""Tests for ProgressBar widget."""
import pygame
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pygame_widget_kit.ProgressBar import ProgressBar


@pytest.mark.unit
class TestProgressBar:
    """Test ProgressBar widget functionality."""

    def test_progressbar_initialization(self, basic_rect):
        """Test that ProgressBar initializes correctly."""
        progress = ProgressBar(rect=basic_rect)
        
        assert progress.rect == basic_rect
        assert progress.enabled is True

    def test_progressbar_visibility(self, basic_rect):
        """Test progress bar visibility."""
        progress = ProgressBar(rect=basic_rect)
        
        assert progress.visible is True
        progress.visible = False
        assert progress.visible is False

    def test_progressbar_enabled_disabled(self, basic_rect):
        """Test enabling/disabling progress bar."""
        progress = ProgressBar(rect=basic_rect)
        
        assert progress.enabled is True
        progress.enabled = False
        assert progress.enabled is False

    def test_progressbar_is_component(self, basic_rect):
        """Test that ProgressBar is a valid component."""
        progress = ProgressBar(rect=basic_rect)
        
        assert hasattr(progress, 'rect')
        assert hasattr(progress, 'visible')
        assert hasattr(progress, 'enabled')
