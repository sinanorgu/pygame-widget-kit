"""Integration tests for UIManager and multiple widgets."""
import pygame
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pygame_widget_kit.UIComponent import UIComponent
from pygame_widget_kit.Button import Button
from pygame_widget_kit.TextInput import TextInput
from pygame_widget_kit.UIManager import UIManager


@pytest.mark.integration
class TestIntegration:
    """Test multiple components working together."""

    def test_ui_manager_initialization(self, display_surface):
        """Test UIManager initialization."""
        root = UIComponent(rect=pygame.Rect(0, 0, 800, 600))
        manager = UIManager(root)
        
        assert manager is not None
        assert isinstance(manager, UIManager)
        assert manager.root == root

    def test_button_and_textinput_together(self, display_surface):
        """Test Button and TextInput coexisting."""
        root = UIComponent(rect=pygame.Rect(0, 0, 800, 600))
        manager = UIManager(root)
        
        button = Button(
            text_str="Submit",
            pos=(50, 50),
            size=(100, 40)
        )
        
        textinput = TextInput(
            rect=pygame.Rect(50, 100, 200, 40)
        )
        
        root.add_child(button)
        root.add_child(textinput)
        
        # Both should be created without errors
        assert button.text_str == "Submit"
        assert textinput.text_value == ""
        assert len(root.children) == 2

    def test_component_hierarchy(self, basic_rect):
        """Test parent-child component relationships."""
        parent = UIComponent(rect=basic_rect, color=(255, 0, 0))
        child1 = UIComponent(rect=pygame.Rect(10, 10, 50, 50), color=(0, 255, 0))
        child2 = UIComponent(rect=pygame.Rect(70, 10, 50, 50), color=(0, 0, 255))
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        assert len(parent.children) == 2
        assert child1.parent == parent
        assert child2.parent == parent
        
    def test_component_visibility_cascade(self, basic_rect):
        """Test that visibility affects component tree."""
        parent = UIComponent(rect=basic_rect, color=(255, 0, 0))
        child = UIComponent(rect=pygame.Rect(10, 10, 50, 50), color=(0, 255, 0))
        
        parent.add_child(child)
        
        parent.visible = False
        assert parent.visible is False
        assert child.visible is True  # Child's own visibility is independent
        
        parent.visible = True
        assert parent.visible is True
        assert child.visible is True
