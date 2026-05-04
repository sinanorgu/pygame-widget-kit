"""Pytest configuration and shared fixtures."""
import pygame
import pytest
import sys
from pathlib import Path

# Add src to path so we can import pygame_widget_kit
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    """Initialize Pygame for all tests."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def display_surface():
    """Create a test display surface."""
    surface = pygame.display.set_mode((800, 600))
    yield surface
    # Clean up after test
    pygame.display.quit()
    pygame.init()  # Re-initialize for next test


@pytest.fixture
def basic_rect():
    """Create a basic rectangle for testing."""
    return pygame.Rect(10, 10, 100, 50)
