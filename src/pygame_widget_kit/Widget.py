import pygame
from .UIComponent import *


class Widget(UIComponent):
    def __init__(self, rect, style=None, z_index=0, color=None, border_color = None , hover_color=None, color_active=None):
        if hover_color is None:
            hover_color = color
        super().__init__(rect, style, z_index, color, border_color, hover_color, color_active)
    
    def draw(self, surface):

        return super().draw(surface)
    
    