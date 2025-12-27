# pygame-widget-kit

[![PyPI](https://img.shields.io/pypi/v/pygame-widget-kit.svg)](https://pypi.org/project/pygame-widget-kit/)

A GUI framework built on Pygame. pygame-widget-kit is a retained-mode UI system with a component tree, event routing, focus and modal management, and extensible widgets such as Select/Dropdown and TextInput with mouse-based text selection and clipboard support.

PyPI: https://pypi.org/project/pygame-widget-kit/

## Features

- Retained-mode component tree with nested children
- Event routing with hover, focus, and active state handling
- Modal/dropdown support via `UIManager`
- Built-in widgets: `Button`, `Text`, `Select`, `TextInput`
- Clipboard copy/paste in `TextInput` (requires `pygame.scrap`)

## Installation

```bash
pip install pygame-widget-kit
```

Pygame is listed as a dependency (pygame >= 2.0.0). Make sure you call `pygame.init()` before creating widgets.

## Usage

```python
import pygame
from pygame_widget_kit import UIManager, Widget, Button, Text, Select, TextInput

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Root container for the UI tree
    root = Widget((0, 0, 800, 600), border_color=None)
    ui = UIManager(root)

    title = Text("pygame-widget-kit demo", pos=(20, 20), text_color=(0, 0, 0))
    root.add_child(title)

    button = Button("Click me", pos=(20, 70), size=(160, 40))
    root.add_child(button)

    select = Select(
        rect=(20, 130, 200, 32),
        options=[("Easy", "easy"), ("Hard", "hard")],
        default_index=0,
    )
    select.z_index = 2
    root.add_child(select)

    input_box = TextInput(
        rect=(20, 180, 240, 36),
        initial_text="Type here",
    )
    root.add_child(input_box)

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            ui.handle_event(event)

        # Caret blink and selection updates
        input_box.update(dt)

        screen.fill((0, 0, 0))
        root.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
```

## Usage notes

- Use `UIManager` to handle events and manage focus/active state.
- Call `root.add_child(...)` to build a component tree. Child positions are relative to their parent.
- Call `TextInput.update(dt)` every frame to animate the caret.
- `Select` uses modal behavior through `UIManager`; clicks outside the dropdown close it.

## Creating custom widgets

Subclass `UIComponent` and override any of the following hooks:

- `draw(surface)` for custom rendering
- `handle_event(event)` for keyboard/mouse logic
- `on_click(event)` for click behavior

## License

MIT
