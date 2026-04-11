"""Tests for Radio widget."""
import pygame
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pygame_widget_kit.Radio import Radio


@pytest.mark.unit
class TestRadio:
    """Test Radio widget functionality."""

    def test_radio_initialization(self, basic_rect):
        """Test that Radio initializes correctly."""
        options = ["Option 1", "Option 2", "Option 3"]
        radio = Radio(rect=basic_rect, options=options)
        
        assert radio is not None
        assert radio.enabled is True

    def test_radio_visibility(self, basic_rect):
        """Test radio visibility."""
        options = ["A", "B", "C"]
        radio = Radio(rect=basic_rect, options=options)
        
        assert radio.visible is True
        radio.visible = False
        assert radio.visible is False

    def test_radio_enabled_disabled(self, basic_rect):
        """Test enabling/disabling radio."""
        options = ["Item 1", "Item 2"]
        radio = Radio(rect=basic_rect, options=options)
        
        assert radio.enabled is True
        radio.enabled = False
        assert radio.enabled is False

    def test_radio_default_index(self, basic_rect):
        """Test radio default index."""
        options = ["First", "Second", "Third"]
        radio = Radio(rect=basic_rect, options=options, default_index=1)
        
        assert radio is not None
