"""Unit tests for UIComponent base class."""
import pygame
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pygame_widget_kit.UIComponent import UIComponent


@pytest.mark.unit
class TestUIComponent:
    """Test UIComponent basic functionality."""

    def test_component_initialization(self, basic_rect):
        """Test that UIComponent initializes with correct properties."""
        component = UIComponent(
            rect=basic_rect,
            color=(255, 0, 0),
            border_color=(0, 255, 0)
        )
        
        assert component.rect == basic_rect
        assert component.color == (255, 0, 0)
        assert component.border_color == (0, 255, 0)
        assert component.visible is True
        assert component.enabled is True
        assert component.focused is False
        assert component.hovered is False

    def test_add_child_component(self, basic_rect):
        """Test adding child components."""
        parent = UIComponent(rect=basic_rect, color=(255, 0, 0))
        child_rect = pygame.Rect(20, 20, 50, 50)
        child = UIComponent(rect=child_rect, color=(0, 255, 0))
        
        parent.add_child(child)
        
        assert len(parent.children) == 1
        assert parent.children[0] == child
        assert child.parent == parent

    def test_multiple_children(self, basic_rect):
        """Test adding multiple children."""
        parent = UIComponent(rect=basic_rect, color=(255, 0, 0))
        
        for i in range(3):
            child_rect = pygame.Rect(20 + i*10, 20 + i*10, 50, 50)
            child = UIComponent(rect=child_rect, color=(0, 255, 0))
            parent.add_child(child)
        
        assert len(parent.children) == 3

    def test_visibility_toggle(self, basic_rect):
        """Test visibility property."""
        component = UIComponent(rect=basic_rect, color=(255, 0, 0))
        
        assert component.visible is True
        component.visible = False
        assert component.visible is False

    def test_enabled_toggle(self, basic_rect):
        """Test enabled property."""
        component = UIComponent(rect=basic_rect, color=(255, 0, 0))
        
        assert component.enabled is True
        component.enabled = False
        assert component.enabled is False

    def test_hover_color_calculation(self, basic_rect):
        """Test that hover color is calculated correctly."""
        color = (100, 100, 100)
        component = UIComponent(rect=basic_rect, color=color)
        
        # Hover color should be calculated by adding 30 to each channel
        expected_hover = tuple(min(c + 30, 255) for c in color)
        assert component.hover_color == expected_hover

    def test_active_color_calculation(self, basic_rect):
        """Test that active color is calculated correctly."""
        color = (100, 100, 100)
        component = UIComponent(rect=basic_rect, color=color)
        
        # Active color should be calculated by subtracting 40 from each channel
        expected_active = tuple(max(c - 40, 0) for c in color)
        assert component.color_active == expected_active

    def test_custom_active_color(self, basic_rect):
        """Test that custom active color overrides default."""
        color = (100, 100, 100)
        custom_active = (50, 50, 50)
        component = UIComponent(
            rect=basic_rect, 
            color=color,
            color_active=custom_active
        )
        
        assert component.color_active == custom_active

    def test_z_index_property(self, basic_rect):
        """Test z-index for layering."""
        component1 = UIComponent(rect=basic_rect, color=(255, 0, 0), z_index=1)
        component2 = UIComponent(rect=basic_rect, color=(0, 255, 0), z_index=2)
        
        assert component1.z_index == 1
        assert component2.z_index == 2
        assert component2.z_index > component1.z_index
