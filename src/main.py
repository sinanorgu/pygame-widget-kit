import pygame
from pygame_widget_kit import *


SCREEN_WIDTH = 900
SCREEN_HEIGHT = 720


def update_label_from_input(input_box: TextInput, label: Text):
    label.set_text(f"Label: {input_box.text_value}")


def update_select_label(select: Select, label: Text):
    label.set_text(f"Selected: {select.selected_value}")


def update_slider_label(slider: Slider, label: Text):
    label.set_text(f"Slider Value: {round(slider.value, 2)}")


def update_toggle_label(toggle_button: ToggleButton, label: Text):
    state_text = "ON" if toggle_button.state else "OFF"
    label.set_text(f"Toggle: {state_text}")


def update_radio_label(radio: Radio, label: Text):
    label.set_text(f"Radio: {radio.get_value()}")


def increase_click_count(counter: dict, label: Text):
    counter["count"] += 1
    label.set_text(f"Button clicks: {counter['count']}")


def update_file_label(file_button: ChooseFileButton, label: Text):
    selected_file = file_button.chosen_file_path
    if not selected_file:
        label.set_text("File: (none)")
        return

    max_chars = 36
    if len(selected_file) > max_chars:
        selected_file = "..." + selected_file[-(max_chars - 3):]
    label.set_text(f"File: {selected_file}")


def toggle_scrollable(layout: LayoutContainer, label: Text):
    layout.set_scrollable(not layout.scrollable)
    state = "ON" if layout.scrollable else "OFF"
    label.set_text(f"Scrollable: {state}")


def toggle_scrollbar(layout: LayoutContainer, label: Text):
    layout.set_scrollbar_visible(not layout.show_scrollbar)
    state = "ON" if layout.show_scrollbar else "OFF"
    label.set_text(f"Scrollbar: {state}")


def toggle_smooth_scroll(layout: LayoutContainer, label: Text):
    layout.set_smooth_scroll(not layout.smooth_scroll)
    state = "ON" if layout.smooth_scroll else "OFF"
    label.set_text(f"Smooth: {state}")


def code_editor_completion_provider(full_text: str, cursor_pos: tuple[int, int], prefix: str):
    del full_text, cursor_pos
    base_tokens = [
        "for",
        "while",
        "if",
        "elif",
        "else",
        "def",
        "class",
        "return",
        "import",
        "from",
        "print",
        "range",
        "len",
    ]
    if not prefix:
        return []
    return [token for token in base_tokens if token.startswith(prefix)][:8]


def activate_download(progress_bars, status_label: Text):
    for progress_bar in progress_bars:
        progress_bar.activate()
    status_label.set_text("Download state: ACTIVE")


def deactivate_download(progress_bars, status_label: Text):
    for progress_bar in progress_bars:
        progress_bar.deactivate()
    status_label.set_text("Download state: PAUSED")


def increment_download_progress(progress_bars, amount: float = 5.0):
    for progress_bar in progress_bars:
        progress_bar.increment(amount)


def reset_download_progress(progress_bars, status_label: Text):
    for progress_bar in progress_bars:
        progress_bar.set_value(progress_bar.min_value)
    status_label.set_text("Download state: RESET")


def create_section(title: str, collapsed: bool = False, height: int = 220):
    return CollapsibleContainer(
        rect=(0, 0, 410, height),
        title=title,
        padding=10,
        spacing=8,
        header_height=32,
        collapsed=collapsed,
        color=(220, 220, 220),
        border_color=(110, 110, 110),
        show_body_when_collapsed=False,
    )


def create_clipping_stress_section():
    stress = create_section("Clipping Stress Lab", collapsed=False, height=760)
    stress.add_child(Text("Case 0: Scrollable layout controls", pos=(0, 0), text_color=(0, 0, 0)))

    scroll_case = VBoxLayout(
        rect=(0, 0, 300, 140),
        spacing=6,
        padding=6,
        color=(235, 235, 235),
        border_color=(140, 140, 140),
        align="left",
        scrollable=True,
        show_scrollbar=True,
        smooth_scroll=True,
        smooth_scroll_factor=0.1,
    )
    for i in range(1, 121):
        label = f"Scrollable row {i:03d}"
        if i % 20 == 0:
            label += "  < milestone"
        scroll_case.add_child(Text(label, pos=(0, 0), text_color=(0, 0, 0)))

    scrollable_state = Text("Scrollable: ON", pos=(0, 0), text_color=(0, 0, 0))
    scrollbar_state = Text("Scrollbar: ON", pos=(0, 0), text_color=(0, 0, 0))
    smooth_state = Text("Smooth: ON", pos=(0, 0), text_color=(0, 0, 0))
    btn_toggle_scrollable = Button("Toggle Scrollable", pos=(0, 0), size=(170, 30))
    btn_toggle_scrollbar = Button("Toggle Scrollbar", pos=(0, 0), size=(170, 30))
    btn_toggle_smooth = Button("Toggle Smooth", pos=(0, 0), size=(170, 30))
    btn_toggle_scrollable.click_bind(toggle_scrollable, scroll_case, scrollable_state)
    btn_toggle_scrollbar.click_bind(toggle_scrollbar, scroll_case, scrollbar_state)
    btn_toggle_smooth.click_bind(toggle_smooth_scroll, scroll_case, smooth_state)

    stress.add_child(scroll_case)
    stress.add_child(btn_toggle_scrollable)
    stress.add_child(scrollable_state)
    stress.add_child(btn_toggle_scrollbar)
    stress.add_child(scrollbar_state)
    stress.add_child(btn_toggle_smooth)
    stress.add_child(smooth_state)

    stress.add_child(Text("Case 1: Oversized widgets in a small container", pos=(0, 0), text_color=(0, 0, 0)))

    case1 = VBoxLayout(
        rect=(0, 0, 290, 125),
        spacing=6,
        padding=6,
        color=(235, 235, 235),
        border_color=(140, 140, 140),
        align="left",
    )
    case1.add_child(Button("THIS BUTTON IS WIDER THAN ITS PARENT CONTAINER", pos=(0, 0), size=(480, 30)))
    case1.add_child(TextInput(rect=(0, 0, 430, 30), initial_text="Very long input that should be clipped by parent bounds."))
    case1.add_child(TextArea((0, 0, 440, 60), "Long TextArea content that exceeds small viewport.", text_color=(0, 0, 0), max_chars_per_line=60))
    stress.add_child(case1)

    stress.add_child(Text("Case 2: Collapsible inside collapsible (mixed overflow)", pos=(0, 0), text_color=(0, 0, 0)))

    nested_outer = CollapsibleContainer(
        rect=(0, 0, 300, 230),
        title="Nested Outer",
        padding=8,
        spacing=6,
        header_height=28,
        collapsed=False,
        color=(225, 225, 225),
        border_color=(120, 120, 120),
        show_body_when_collapsed=False,
    )

    nested_outer.add_child(Text("Outer child text", pos=(0, 0), text_color=(0, 0, 0)))
    nested_outer.add_child(Button("Outer oversized button for clipping check", pos=(0, 0), size=(360, 28)))

    nested_inner = CollapsibleContainer(
        rect=(0, 0, 260, 150),
        title="Nested Inner",
        padding=6,
        spacing=6,
        header_height=26,
        collapsed=True,
        color=(232, 232, 232),
        border_color=(130, 130, 130),
        show_body_when_collapsed=False,
    )
    nested_inner.add_child(TextInput(rect=(0, 0, 350, 30), initial_text="Inner long input"))
    nested_inner.add_child(Button("Inner long button xxxxxxxxxxxxxxxxxxxxx", pos=(0, 0), size=(380, 30)))
    nested_inner.add_child(TextArea((0, 0, 360, 70), "Nested inner text area with long content lines.", text_color=(0, 0, 0), max_chars_per_line=70))
    nested_outer.add_child(nested_inner)
    stress.add_child(nested_outer)

    stress.add_child(Text("Case 3: Wide row layout overflow", pos=(0, 0), text_color=(0, 0, 0)))

    case3 = HBoxLayout(
        rect=(0, 0, 300, 80),
        spacing=8,
        padding=6,
        color=(236, 236, 236),
        border_color=(140, 140, 140),
        align="center",
    )
    case3.add_child(Button("Wide A", pos=(0, 0), size=(180, 32)))
    case3.add_child(Button("Wide B", pos=(0, 0), size=(180, 32)))
    case3.add_child(Button("Wide C", pos=(0, 0), size=(180, 32)))
    stress.add_child(case3)

    stress.add_child(Text("Case 4: Select + dropdown near clipped regions", pos=(0, 0), text_color=(0, 0, 0)))

    case4 = VBoxLayout(
        rect=(0, 0, 300, 120),
        spacing=6,
        padding=6,
        color=(236, 236, 236),
        border_color=(140, 140, 140),
    )
    case4.add_child(Text("Open dropdown to check overlay clipping behavior", pos=(0, 0), text_color=(0, 0, 0)))
    case4.add_child(Select(rect=(0, 0, 210, 32), options=["one", "two", "three", "four", "five"], default_index=0, z_index=8))
    case4.add_child(TextInput(rect=(0, 0, 330, 30), initial_text="Input under select for overlap test"))
    stress.add_child(case4)

    stress.add_child(Text("Case 5: Deep chain (3 levels)", pos=(0, 0), text_color=(0, 0, 0)))

    level1 = VBoxLayout(
        rect=(0, 0, 300, 180),
        spacing=6,
        padding=6,
        color=(236, 236, 236),
        border_color=(140, 140, 140),
    )
    level2 = VBoxLayout(
        rect=(0, 0, 280, 150),
        spacing=6,
        padding=6,
        color=(232, 232, 232),
        border_color=(130, 130, 130),
    )
    level3 = VBoxLayout(
        rect=(0, 0, 260, 120),
        spacing=6,
        padding=6,
        color=(228, 228, 228),
        border_color=(120, 120, 120),
    )

    level3.add_child(Button("L3 button too wide ................................", pos=(0, 0), size=(420, 28)))
    level3.add_child(TextInput(rect=(0, 0, 420, 30), initial_text="L3 very long input value"))
    level3.add_child(TextArea((0, 0, 420, 52), "L3 long text area", text_color=(0, 0, 0), max_chars_per_line=80))

    level2.add_child(level3)
    level1.add_child(level2)
    stress.add_child(level1)

    stress.add_child(Text("Case 6: Ultra long rapid-scroll playground", pos=(0, 0), text_color=(0, 0, 0)))

    marathon_case = VBoxLayout(
        rect=(0, 0, 300, 220),
        spacing=4,
        padding=6,
        color=(236, 236, 236),
        border_color=(140, 140, 140),
        align="left",
        scrollable=True,
        show_scrollbar=True,
        smooth_scroll=True,
        smooth_scroll_factor=0.12,
        smooth_snap_threshold=2.0,
    )
    marathon_case.wheel_step = 44

    marathon_case.add_child(Text("Scroll fast with wheel/trackpad and try repeated bursts.", pos=(0, 0), text_color=(0, 0, 0)))
    for i in range(1, 281):
        row = f"Rapid test row {i:03d}"
        if i % 25 == 0:
            row += "  [checkpoint]"
        marathon_case.add_child(Text(row, pos=(0, 0), text_color=(0, 0, 0)))

    stress.add_child(marathon_case)

    return stress


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    root = Widget((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), border_color=None)
    ui = UIManager(root)

    title = Text("pygame-widget-kit / grouped component demo", pos=(20, 16), text_color=(0, 0, 0))
    root.add_child(title)

    page = HBoxLayout(
        rect=(20, 56, 860, 650),
        spacing=16,
        padding=8,
        color=(242, 242, 242),
        align="top",
    )

    left_column = VBoxLayout(
        rect=(0, 0, 418, 630),
        spacing=12,
        padding=0,
        color=None,
        border_color=None,
        align="left",
    )

    right_column = VBoxLayout(
        rect=(0, 0, 418, 630),
        spacing=12,
        padding=0,
        color=None,
        border_color=None,
        align="left",
        scrollable=True,
        show_scrollbar=True,
        smooth_scroll=True,
        smooth_scroll_factor=0.12,
    )
    

    page.add_child(left_column)
    page.add_child(right_column)
    root.add_child(page)

    input_section = create_section("Inputs", collapsed=False, height=190)
    input_box = TextInput(rect=(0, 0, 220, 500), initial_text="a",show_scrollbars=True)
    update_button = Button("Update label", pos=(0, 0), size=(150, 34))
    value_label = Text("Label: (empty)", pos=(0, 0), text_color=(0, 0, 0))
    update_button.click_bind(update_label_from_input, input_box, value_label)

    input_section.add_child(Text("Basic text input:", pos=(0, 0), text_color=(0, 0, 0)))
    input_section.add_child(input_box)
    input_section.add_child(update_button)
    input_section.add_child(value_label)

    input_modes_section = create_section("Input Modes (char filters)", collapsed=True, height=340)
    mode_rows = [
        ("Allow all", ALLOW_ALL_CHARS),
        ("Text only", TEXT_ONLY),
        ("Number only", NUMBER_ONLY),
        ("Hex only", HEX_ONLY),
        ("Binary only", BINARY_ONLY),
        ("Octal only", OCTAL_ONLY),
    ]

    for mode_label, mode_type in mode_rows:
        input_modes_section.add_child(Text(f"{mode_label}:", pos=(0, 0), text_color=(0, 0, 0)))
        input_modes_section.add_child(TextInput(rect=(0, 0, 260, 30), allowed_char_mode=mode_type,allow_multiline=False))

    selection_section = create_section("Selection Components", collapsed=False, height=320)
    select_label = Text("Select difficulty:", pos=(0, 0), text_color=(0, 0, 0))
    select = Select(
        rect=(0, 0, 180, 32),
        options=["Easy", "Hard", "Expert"],
        default_index=0,
        z_index=5,
    )
    select_value = Text("Selected: Easy", pos=(0, 0), text_color=(0, 0, 0))
    select.bind_on_option_chance(update_select_label, select, select_value)

    radio_label = Text("Radio options:", pos=(0, 0), text_color=(0, 0, 0))
    radio = Radio((0, 0, 220, 84), options=["OPTION A", "OPTION B", "OPTION C"], default_index=0)
    radio_value = Text(f"Radio: {radio.get_value()}", pos=(0, 0), text_color=(0, 0, 0))

    selection_section.add_child(select_label)
    selection_section.add_child(select)
    selection_section.add_child(select_value)
    selection_section.add_child(radio_label)
    selection_section.add_child(radio)
    selection_section.add_child(radio_value)

    controls_section = create_section("Buttons & Toggle", collapsed=False, height=250)
    click_counter = {"count": 0}
    normal_button = Button("Click me", pos=(0, 0), size=(140, 34))
    button_count_label = Text("Button clicks: 0", pos=(0, 0), text_color=(0, 0, 0))
    normal_button.click_bind(increase_click_count, click_counter, button_count_label)

    toggle_button = ToggleButton(pos=(0, 0), size=(90, 38), state=False)
    toggle_value = Text("Toggle: OFF", pos=(0, 0), text_color=(0, 0, 0))
    toggle_button.bind_on_toggle(update_toggle_label, toggle_button, toggle_value)

    controls_section.add_child(Text("Standard button:", pos=(0, 0), text_color=(0, 0, 0)))
    controls_section.add_child(normal_button)
    controls_section.add_child(button_count_label)
    controls_section.add_child(Text("Toggle button:", pos=(0, 0), text_color=(0, 0, 0)))
    controls_section.add_child(toggle_button)
    controls_section.add_child(toggle_value)

    file_section = create_section("File Picker Button", collapsed=False, height=190)
    choose_file_button = ChooseFileButton("Choose file", pos=(0, 0), size=(220, 34))
    chosen_file_label = Text("File: (none)", pos=(0, 0), text_color=(0, 0, 0))
    choose_file_button.click_bind(update_file_label, choose_file_button, chosen_file_label)

    file_section.add_child(Text("ChooseFileButton demo:", pos=(0, 0), text_color=(0, 0, 0)))
    file_section.add_child(choose_file_button)
    file_section.add_child(chosen_file_label)

    slider_section = create_section("Slider", collapsed=False, height=190)
    slider = Slider((0, 0), size=(260, 24), min_value=50, max_value=2000)
    slider_value = Text("Slider Value: 50", pos=(0, 0), text_color=(0, 0, 0))
    slider.change_bind(update_slider_label, slider, slider_value)

    slider_section.add_child(Text("Drag slider handle:", pos=(0, 0), text_color=(0, 0, 0)))
    slider_section.add_child(slider)
    slider_section.add_child(slider_value)

    text_area_section = create_section("TextArea", collapsed=True, height=280)
    text_area_str = "This is a multiline TextArea sample. Open/close sections to test dynamic layout behavior."
    text_area = TextArea((0, 0, 300, 120), text_area_str, text_color=(0, 0, 0), max_chars_per_line=28)
    text_area_section.add_child(Text("TextArea content:", pos=(0, 0), text_color=(0, 0, 0)))
    text_area_section.add_child(text_area)

    code_editor_section = create_section("CodeEditor (Highlighter Demo)", collapsed=False, height=360)
    code_editor_section.add_child(Text("Type python-like keywords and watch colors/styles.", pos=(0, 0), text_color=(0, 0, 0)))

    code_editor = CodeEditor(
        rect=(0, 0, 360, 220),
        initial_text=(
            "for i in range(5):\n"
            "    if i % 2 == 0:\n"
            "        print(i)\n"
            "    else:\n"
            "        return None"
        ),
        keyword_styles={
            "for": {"color": (0, 120, 255), "bold": True},
            "if": {"color": (0, 120, 255), "bold": True},
            "else": {"color": (0, 120, 255), "bold": True},
            "in": {"color": (0, 120, 255), "bold": True},
            "return": {"color": (205, 90, 35), "bold": True},
            "range": {"color": (120, 50, 150), "italic": True},
            "print": {"color": (30, 140, 70)},
            "None": {"color": (140, 80, 110), "italic": True},
        },
        token_styles={
            "(": {"color": (90, 90, 90)},
            ")": {"color": (90, 90, 90)},
            ":": {"color": (90, 90, 90)},
        },
        show_scrollbars=True,
        allow_multiline=True,
        font_size=22,
    )
    code_editor.set_autocomplete_provider(code_editor_completion_provider)

    code_editor_section.add_child(code_editor)
    code_editor_section.add_child(Text("Shortcut: Ctrl/Cmd + Space completion trigger", pos=(0, 0), text_color=(0, 0, 0)))

    progress_section = create_section("Download Status Bar", collapsed=False, height=500)
    progress_bar = ProgressBar(
        rect=(0, 0, 330, 50),
        min_value=0,
        max_value=100,
        value=0,
        bar_type=THIN_LINE_BAR,
        show_text=True,
        text_display_mode=TEXT_MODE_VALUE_MAX,
        text_position=TEXT_POSITION_RIGHT,
        animate_value_change=True,
        value_animation_duration=0.35,
        activity_animation_enabled=True,
        shimmer_cycles_per_sec=1.1,
        track_color=(214, 214, 214),
    )
    segmented_progress_bar = ProgressBar(
        rect=(0, 0, 330, 50),
        min_value=0,
        max_value=100,
        value=0,
        bar_type=SEGMENTED_BAR,
        show_text=True,
        text_display_mode=TEXT_MODE_PERCENT,
        text_position=TEXT_POSITION_RIGHT,
        animate_value_change=True,
        value_animation_duration=0.35,
        activity_animation_enabled=True,
    )
    striped_progress_bar = ProgressBar(
        rect=(0, 0, 330, 50),
        min_value=0,
        max_value=100,
        value=0,
        bar_type=STRIPED_BAR,
        show_text=True,
        text_display_mode=TEXT_MODE_PERCENT,
        text_position=TEXT_POSITION_RIGHT,
        animate_value_change=True,
        value_animation_duration=0.35,
        activity_animation_enabled=True,
    )
    glow_progress_bar = ProgressBar(
        rect=(0, 0, 330, 50),
        min_value=0,
        max_value=100,
        value=0,
        bar_type=GLOW_LINE_BAR,
        show_text=True,
        text_display_mode=TEXT_MODE_VALUE_MAX,
        text_position=TEXT_POSITION_RIGHT,
        animate_value_change=True,
        value_animation_duration=0.35,
        activity_animation_enabled=True,
    )
    progress_bars = [
        progress_bar,
        segmented_progress_bar,
        striped_progress_bar,
        glow_progress_bar,
    ]
    progress_state = Text("Download state: PAUSED", pos=(0, 0), text_color=(0, 0, 0))

    btn_start = Button("Start", pos=(0, 0), size=(90, 30))
    btn_pause = Button("Pause", pos=(0, 0), size=(90, 30))
    btn_plus_5 = Button("+5%", pos=(0, 0), size=(90, 30))
    btn_plus_20 = Button("+20%", pos=(0, 0), size=(90, 30))
    btn_reset = Button("Reset", pos=(0, 0), size=(90, 30))

    btn_start.click_bind(activate_download, progress_bars, progress_state)
    btn_pause.click_bind(deactivate_download, progress_bars, progress_state)
    btn_plus_5.click_bind(increment_download_progress, progress_bars, 5.0)
    btn_plus_20.click_bind(increment_download_progress, progress_bars, 20.0)
    btn_reset.click_bind(reset_download_progress, progress_bars, progress_state)

    progress_section.add_child(Text("Thin Line:", pos=(0, 0), text_color=(0, 0, 0)))
    progress_section.add_child(progress_bar)
    progress_section.add_child(Text("Segmented:", pos=(0, 0), text_color=(0, 0, 0)))
    progress_section.add_child(segmented_progress_bar)
    progress_section.add_child(Text("Striped:", pos=(0, 0), text_color=(0, 0, 0)))
    progress_section.add_child(striped_progress_bar)
    progress_section.add_child(Text("Glow Line:", pos=(0, 0), text_color=(0, 0, 0)))
    progress_section.add_child(glow_progress_bar)
    progress_section.add_child(progress_state)

    progress_buttons = HBoxLayout(
        rect=(0, 0, 360, 40),
        spacing=8,
        padding=0,
        color=None,
        border_color=None,
        align="top",
    )
    progress_buttons.add_child(btn_start)
    progress_buttons.add_child(btn_pause)
    progress_buttons.add_child(btn_plus_5)
    progress_buttons.add_child(btn_plus_20)
    progress_buttons.add_child(btn_reset)
    progress_section.add_child(progress_buttons)

    loading_section = create_section("Loading Spinner Types", collapsed=True, height=1450)
    
    loading_circular_spokes = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Circular Spokes",
        icon_type=CIRCULAR_SPOKES,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(40, 40, 40),
        speed_deg_per_sec=120,
    )
    
    loading_circular_dots = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Circular Dots",
        icon_type=CIRCULAR_DOTS,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(50, 100, 180),
        track_color=(210, 220, 240),
        speed_deg_per_sec=130,
        spoke_count=8,
    )
    
    loading_triangle_dots = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Triangle Dots",
        icon_type=TRIANGLE_DOTS,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(180, 50, 100),
        track_color=(240, 210, 220),
        speed_deg_per_sec=110,
    )
    
    loading_wave_dots = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Wave Dots",
        icon_type=WAVE_DOTS,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(100, 180, 50),
        speed_deg_per_sec=180,
    )
    
    loading_pulsing_ring = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Pulsing Ring",
        icon_type=PULSING_RING,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(180, 100, 50),
        speed_deg_per_sec=90,
    )
    
    loading_bar_wave = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Bar Wave",
        icon_type=BAR_WAVE,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(50, 180, 180),
        speed_deg_per_sec=150,
    )
    
    loading_rotating_quad = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Rotating Quad",
        icon_type=ROTATING_QUAD,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(180, 150, 50),
        speed_deg_per_sec=200,
        spoke_width=2,
    )
    
    loading_orbiting_dots = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Orbiting Dots",
        icon_type=ORBITING_DOTS,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(100, 50, 180),
        speed_deg_per_sec=160,
    )
    
    loading_spiral_dots = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Spiral Dots",
        icon_type=SPIRAL_DOTS,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(180, 180, 50),
        speed_deg_per_sec=140,
    )
    
    loading_bounce_dots = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Bounce Dots",
        icon_type=BOUNCE_DOTS,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(50, 100, 50),
        speed_deg_per_sec=180,
    )
    
    loading_dots_scale = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Dots Scale",
        icon_type=DOTS_SCALE,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(150, 100, 200),
        speed_deg_per_sec=170,
    )
    
    loading_rotating_lines = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Rotating Lines",
        icon_type=ROTATING_LINES,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(100, 150, 200),
        speed_deg_per_sec=200,
        spoke_width=2,
    )
    
    loading_double_bounce = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Double Bounce",
        icon_type=DOUBLE_BOUNCE,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(200, 100, 150),
        speed_deg_per_sec=190,
    )
    
    loading_pendulum = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Pendulum",
        icon_type=PENDULUM,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(100, 200, 100),
        speed_deg_per_sec=120,
        spoke_width=2,
    )
    
    loading_expanding_ring = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Expanding Ring",
        icon_type=EXPANDING_RING,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(200, 200, 100),
        speed_deg_per_sec=100,
        spoke_width=1,
    )
    
    loading_flip_dots = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Flip Dots",
        icon_type=FLIP_DOTS,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(200, 150, 100),
        speed_deg_per_sec=150,
    )
    
    loading_rotating_plane = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Rotating Plane",
        icon_type=ROTATING_PLANE,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(150, 200, 100),
        speed_deg_per_sec=160,
        spoke_width=1,
    )
    
    loading_radar = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Radar",
        icon_type=RADAR,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(50, 150, 200),
        track_color=(200, 220, 240),
        speed_deg_per_sec=180,
        spoke_width=2,
    )
    
    loading_shifting_dots = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Shifting Dots",
        icon_type=SHIFTING_DOTS,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(150, 50, 200),
        speed_deg_per_sec=140,
    )
    
    loading_grid_dots = LoadingSpinner(
        rect=(0, 0, 280, 56),
        text="Grid Dots",
        icon_type=GRID_DOTS,
        color=(238, 238, 238),
        border_color=(140, 140, 140),
        icon_color=(200, 100, 50),
        speed_deg_per_sec=130,
    )
    
    loading_section.add_child(Text("Indeterminate loading demo - 20 icon types:", pos=(0, 0), text_color=(0, 0, 0)))
    loading_section.add_child(loading_circular_spokes)
    loading_section.add_child(loading_circular_dots)
    loading_section.add_child(loading_triangle_dots)
    loading_section.add_child(loading_wave_dots)
    loading_section.add_child(loading_pulsing_ring)
    loading_section.add_child(loading_bar_wave)
    loading_section.add_child(loading_rotating_quad)
    loading_section.add_child(loading_orbiting_dots)
    loading_section.add_child(loading_spiral_dots)
    loading_section.add_child(loading_bounce_dots)
    loading_section.add_child(loading_dots_scale)
    loading_section.add_child(loading_rotating_lines)
    loading_section.add_child(loading_double_bounce)
    loading_section.add_child(loading_pendulum)
    loading_section.add_child(loading_expanding_ring)
    loading_section.add_child(loading_flip_dots)
    loading_section.add_child(loading_rotating_plane)
    loading_section.add_child(loading_radar)
    loading_section.add_child(loading_shifting_dots)
    loading_section.add_child(loading_grid_dots)

    stress_section = create_clipping_stress_section()

    left_column.add_child(input_section)
    left_column.add_child(input_modes_section)
    left_column.add_child(selection_section)
    left_column.add_child(controls_section)
    left_column.add_child(file_section)
    left_column.add_child(slider_section)
    left_column.add_child(code_editor_section)

    right_column.add_child(loading_section)
    right_column.add_child(progress_section)
    right_column.add_child(stress_section)
    right_column.add_child(text_area_section)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        ui.update(dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            ui.handle_event(event)

        update_radio_label(radio, radio_value)

        screen.fill((250, 250, 250))
        root.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
