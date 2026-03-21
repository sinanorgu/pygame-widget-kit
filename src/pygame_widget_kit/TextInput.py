import pygame
from .UIComponent import UIComponent
from .Text import Text
from .Widget import Widget
from .Button import Button
import time
import sys
import subprocess

""" 
class TextInput2(UIComponent):
    def __init__(
        self,
        rect,
        initial_text="",
        text_color=(0, 0, 0),
        bg_color=(220, 220, 220),
        hover_color=(240, 240, 240),
        caret_color=(0, 0, 0),
        padding=6,
        z_index=0
    ):
        super().__init__(
            rect=rect,
            z_index=z_index,
            color=bg_color,
            hover_color=hover_color
        )

        self.text_value = initial_text
        self.text_color = text_color
        self.caret_color = caret_color
        self.padding = padding

        # Text child
        self.text = Text(
            text_str=self.text_value,
            pos=(self.padding, self.padding),
            text_color=self.text_color
        )
        self.add_child(self.text)

        # caret
        self.caret_visible = True
        self._caret_timer = 0
        self._caret_interval = 500  # ms
    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return

        if event.type == pygame.KEYDOWN and self.focused:

            # ESC → blur
            if event.key == pygame.K_ESCAPE:
                if self.ui_manager:
                    self.ui_manager.focused = None
                self.on_blur()
                return

            # ENTER → blur (submit gibi düşünebilirsin)
            if event.key == pygame.K_RETURN:
                if self.ui_manager:
                    self.ui_manager.focused = None
                self.on_blur()
                return

            # BACKSPACE
            if event.key == pygame.K_BACKSPACE:
                self.text_value = self.text_value[:-1]

            # Printable characters
            else:
                if event.unicode and event.unicode.isprintable():
                    self.text_value += event.unicode

            self.text.set_text(self.text_value)
    def on_click(self, event):
        # sadece focus almak yeterli
        pass
    def update(self, dt):
        if not self.focused:
            self.caret_visible = False
            return

        self._caret_timer += dt
        if self._caret_timer >= self._caret_interval:
            self._caret_timer = 0
            self.caret_visible = not self.caret_visible
    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        # caret sadece focused iken
        if self.focused and self.caret_visible:
            text_w, text_h = self.text.render.get_size()

            caret_x = (
                self.absolute_rect[0]
                + self.padding
                + text_w
            )
            caret_y = (
                self.absolute_rect[1]
                + self.padding
            )

            caret_rect = pygame.Rect(
                caret_x,
                caret_y,
                2,
                text_h
            )

            pygame.draw.rect(surface, self.caret_color, caret_rect)
    def get_value(self):
        return self.text_value

    def set_value(self, value: str):
        self.text_value = value
        self.text.set_text(value)

    def clear(self):
        self.set_value("")
 """



ALLOW_ALL_CHARS = 0
NUMBER_ONLY = 1
TEXT_ONLY = 2
HEX_ONLY = 3
BINARY_ONLY = 4
OCTAL_ONLY = 5


class TextInputContextMenu(Widget):
    def __init__(self, owner_input: "TextInput", pos, size=(130, 70), z_index=10_000):
        super().__init__(
            rect=(pos[0], pos[1], size[0], size[1]),
            z_index=z_index,
            color=(245, 245, 245),
            border_color=(120, 120, 120),
            hover_color=(245, 245, 245),
            color_active=(245, 245, 245),
        )
        self.owner_input = owner_input

        button_width = size[0] - 8
        copy_button = Button(
            text_str="Kopyala",
            pos=(4, 4),
            size=(button_width, 28),
            color=(228, 228, 228),
            hover_color=(205, 205, 205),
            border_color=(160, 160, 160),
            text_color=(0, 0, 0),
            padding=(12, 5),
        )
        paste_button = Button(
            text_str="Yapistir",
            pos=(4, 36),
            size=(button_width, 28),
            color=(228, 228, 228),
            hover_color=(205, 205, 205),
            border_color=(160, 160, 160),
            text_color=(0, 0, 0),
            padding=(12, 5),
        )

        copy_button.click_bind(self._on_copy)
        paste_button.click_bind(self._on_paste)

        self.add_child(copy_button)
        self.add_child(paste_button)

    def _on_copy(self):
        self.owner_input.prepare_context_action_for_copy()
        self.owner_input.copy_selected_text()
        self.owner_input.close_context_menu()

    def _on_paste(self):
        self.owner_input.prepare_context_action_for_paste()
        self.owner_input.paste_from_clipboard()
        self.owner_input.close_context_menu()

    def close(self):
        self.owner_input.close_context_menu()



class TextInput(UIComponent):
    def __init__(
        self,
        rect,
        initial_text="",
        allowed_char_mode:int=0,
        text_color=(0, 0, 0),
        bg_color=(220, 220, 220),
        hover_color=(240, 240, 240),
        selection_color=(100, 150, 255),
        caret_color=(0, 0, 0),
        padding=6,
        z_index=0
    ):
        
        super().__init__(
            rect=rect,
            z_index=z_index,
            color=bg_color,
            hover_color=hover_color
        )

        self.text_value = initial_text
        self.text_color = text_color
        self.selection_color = selection_color
        self.caret_color = caret_color
        self.padding = padding
        self.allowed_char_mode=allowed_char_mode

        # text render
        self.text = Text(
            text_str=self.text_value,
            pos=(self.padding, self.padding),
            text_color=self.text_color
        )
        self.add_child(self.text)
        self.text.visible = False

        # caret & selection
        self.cursor_index = len(self.text_value)
        self.selection_start = None
        self.selection_end = None
        self.dragging = False

        # caret blink
        self.caret_visible = True
        self._caret_timer = 0
        self._caret_interval = 0.5
        self.last_blinked_at = time.time()
        self.context_menu: TextInputContextMenu | None = None
        self._clipboard_cache = ""
        self._context_click_index = self.cursor_index
        self._last_click_time = 0.0
        self._last_click_pos = (0, 0)
        self._click_count = 0
        self._multi_click_interval = 0.35
        self._multi_click_distance = 6
        self._undo_stack = []
        self._redo_stack = []
        self._max_history = 200
        self._scroll_x = 0

        #Keyboard repeat settings
        pygame.key.set_repeat(400, 50)

    def _ensure_scrap(self):
        try:
            if not pygame.scrap.get_init():
                pygame.scrap.init()
            return True
        except Exception:
            return False

    def _set_os_clipboard_text(self, text: str):
        if sys.platform == "darwin":
            try:
                process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                process.communicate(text.encode("utf-8"))
                return process.returncode == 0
            except Exception:
                return False
        return False

    def _get_os_clipboard_text(self):
        if sys.platform == "darwin":
            try:
                result = subprocess.run(
                    ["pbpaste"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    return None
                return result.stdout
            except Exception:
                return None
        return None

    def copy_selected_text(self):
        text_to_copy = self.get_selected_text() if self.has_selection() else self.text_value
        if not text_to_copy:
            return

        self._clipboard_cache = text_to_copy

        if self._ensure_scrap():
            try:
                pygame.scrap.put(pygame.SCRAP_TEXT, text_to_copy.encode("utf-8"))
            except Exception:
                pass

        self._set_os_clipboard_text(text_to_copy)

    def paste_from_clipboard(self):
        paste_text = None

        os_clipboard_text = self._get_os_clipboard_text()
        if os_clipboard_text:
            paste_text = os_clipboard_text

        try:
            if not paste_text and self._ensure_scrap():
                raw_text = pygame.scrap.get(pygame.SCRAP_TEXT)
                if raw_text is not None:
                    paste_text = raw_text.decode("utf-8", errors="ignore").replace("\x00", "")
        except Exception:
            paste_text = None

        if not paste_text:
            paste_text = self._clipboard_cache

        try:
            if not paste_text:
                return

            filtered_text = ""
            if self.allowed_char_mode == ALLOW_ALL_CHARS:
                filtered_text = paste_text
            elif self.allowed_char_mode == TEXT_ONLY:
                filtered_text = "".join(ch for ch in paste_text if not ch.isnumeric())
            elif self.allowed_char_mode == NUMBER_ONLY:
                filtered_text = "".join(ch for ch in paste_text if ch.isnumeric())
            elif self.allowed_char_mode == HEX_ONLY:
                filtered_text = "".join(
                    ch for ch in paste_text if ch.isnumeric() or ch.capitalize() in "ABCDEF"
                )
            elif self.allowed_char_mode == BINARY_ONLY:
                filtered_text = "".join(ch for ch in paste_text if ch in "10")
            elif self.allowed_char_mode == OCTAL_ONLY:
                filtered_text = "".join(ch for ch in paste_text if ch in "12345678")

            should_edit = self.has_selection() or bool(filtered_text)
            if should_edit:
                self._record_undo_state()

            # Paste davranisi: secili kisim varsa once sil, sonra yeni icerigi ekle.
            if self.has_selection():
                self.delete_selection(record_history=False)

            if filtered_text:
                self.insert_text(filtered_text, record_history=False)

            self.text.set_text(self.text_value)
        except Exception:
            pass

    def prepare_context_action_for_copy(self):
        # Context menuden sonra fokus tekrar TextInput'a donmeli.
        if self.ui_manager is not None:
            if self.ui_manager.focused and self.ui_manager.focused != self:
                self.ui_manager.focused.on_blur()
            self.ui_manager.focused = self

        self.on_focus()

    def prepare_context_action_for_paste(self):
        # Context menuden sonra fokus tekrar TextInput'a donmeli.
        self.prepare_context_action_for_copy()

        # Secim varsa paste secimi replace etsin (selection korunur).
        # Secim yoksa menu acilan konumdaki index'e paste yap.
        if not self.has_selection():
            self.cursor_index = self._context_click_index

    def open_context_menu(self, pos):
        if self.ui_manager is None:
            return

        self.close_context_menu()

        root_rect = self.ui_manager.root.absolute_rect
        menu_width, menu_height = 130, 70
        menu_x = pos[0]
        menu_y = pos[1]

        max_x = root_rect[0] + root_rect[2] - menu_width
        max_y = root_rect[1] + root_rect[3] - menu_height

        if menu_x > max_x:
            menu_x = max_x
        if menu_y > max_y:
            menu_y = max_y

        menu_x = max(root_rect[0], menu_x)
        menu_y = max(root_rect[1], menu_y)

        self._context_click_index = self._mouse_to_index(pos[0])

        self.context_menu = TextInputContextMenu(self, (menu_x, menu_y))
        self.ui_manager.root.add_child(self.context_menu)
        self.ui_manager.modal = self.context_menu

    def close_context_menu(self):
        if self.context_menu is None:
            return

        menu_parent = self.context_menu.parent
        if menu_parent is not None and self.context_menu in menu_parent.children:
            menu_parent.children.remove(self.context_menu)

        if self.ui_manager is not None and self.ui_manager.modal is self.context_menu:
            self.ui_manager.modal = None

        self.context_menu = None

    
    def _mouse_to_index(self, mouse_x):
        local_x = mouse_x - self.absolute_rect[0] - self.padding + self._scroll_x
        if local_x <= 0:
            return 0

        for i in range(len(self.text_value) + 1):
            w = self.text.font.size(self.text_value[:i])[0]
            if local_x < w:
                return i

        return len(self.text_value)

    def _get_inner_rect(self):
        inner_x = self.absolute_rect[0] + self.padding
        inner_y = self.absolute_rect[1] + self.padding
        inner_w = max(1, self.absolute_rect[2] - (self.padding * 2))
        inner_h = max(1, self.absolute_rect[3] - (self.padding * 2))
        return pygame.Rect(inner_x, inner_y, inner_w, inner_h)

    def _text_width_until(self, index: int) -> int:
        clamped = max(0, min(index, len(self.text_value)))
        return self.text.font.size(self.text_value[:clamped])[0]

    def _ensure_cursor_visible(self):
        inner_rect = self._get_inner_rect()
        inner_w = inner_rect.width

        total_text_width = self.text.render.get_width()
        max_scroll = max(0, total_text_width - inner_w)

        caret_x_in_text = self._text_width_until(self.cursor_index)
        left_visible = self._scroll_x
        right_visible = self._scroll_x + inner_w - 2

        if caret_x_in_text < left_visible:
            self._scroll_x = caret_x_in_text
        elif caret_x_in_text > right_visible:
            self._scroll_x = caret_x_in_text - (inner_w - 2)

        self._scroll_x = max(0, min(self._scroll_x, max_scroll))

    def _is_word_char(self, ch: str) -> bool:
        return ch.isalnum() or ch == "_"

    def _snapshot_state(self):
        return (
            self.text_value,
            self.cursor_index,
            self.selection_start,
            self.selection_end,
        )

    def _restore_state(self, state):
        self.text_value, self.cursor_index, self.selection_start, self.selection_end = state
        self._ensure_cursor_visible()

    def _record_undo_state(self):
        state = self._snapshot_state()
        if self._undo_stack and self._undo_stack[-1] == state:
            return

        self._undo_stack.append(state)
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self):
        if not self._undo_stack:
            return

        current_state = self._snapshot_state()
        previous_state = self._undo_stack.pop()

        if current_state != previous_state:
            self._redo_stack.append(current_state)
            if len(self._redo_stack) > self._max_history:
                self._redo_stack.pop(0)

        self._restore_state(previous_state)

    def redo(self):
        if not self._redo_stack:
            return

        current_state = self._snapshot_state()
        next_state = self._redo_stack.pop()

        if current_state != next_state:
            self._undo_stack.append(current_state)
            if len(self._undo_stack) > self._max_history:
                self._undo_stack.pop(0)

        self._restore_state(next_state)

    def _find_word_bounds(self, index: int):
        n = len(self.text_value)
        if n == 0:
            return 0, 0

        index = max(0, min(index, n))

        probe = index
        if probe == n:
            probe = n - 1

        if probe < 0:
            return 0, 0

        if not self._is_word_char(self.text_value[probe]):
            return probe, probe + 1

        start = probe
        end = probe + 1

        while start > 0 and self._is_word_char(self.text_value[start - 1]):
            start -= 1
        while end < n and self._is_word_char(self.text_value[end]):
            end += 1

        return start, end

    def _next_word_index(self, index: int) -> int:
        n = len(self.text_value)
        i = max(0, min(index, n))

        while i < n and self._is_word_char(self.text_value[i]):
            i += 1
        while i < n and not self._is_word_char(self.text_value[i]):
            i += 1
        return i

    def _prev_word_index(self, index: int) -> int:
        i = max(0, min(index, len(self.text_value)))

        while i > 0 and not self._is_word_char(self.text_value[i - 1]):
            i -= 1
        while i > 0 and self._is_word_char(self.text_value[i - 1]):
            i -= 1
        return i

    def _select_range(self, start: int, end: int):
        start = max(0, min(start, len(self.text_value)))
        end = max(0, min(end, len(self.text_value)))
        self.selection_start = start
        self.selection_end = end
        self.cursor_index = end
        self._ensure_cursor_visible()

    def _select_all(self):
        self.selection_start = 0
        self.selection_end = len(self.text_value)
        self.cursor_index = len(self.text_value)
        self._ensure_cursor_visible()

    def _clear_selection(self):
        self.selection_start = None
        self.selection_end = None

    def _move_cursor(self, target_index: int, keep_selection: bool):
        target_index = max(0, min(target_index, len(self.text_value)))

        if keep_selection:
            if self.selection_start is None:
                self.selection_start = self.cursor_index
            self.selection_end = target_index
        else:
            self._clear_selection()

        self.cursor_index = target_index
        self._ensure_cursor_visible()

    def _delete_prev_word(self):
        start = self._prev_word_index(self.cursor_index)
        if start < self.cursor_index:
            self._record_undo_state()
            self.text_value = self.text_value[:start] + self.text_value[self.cursor_index:]
            self.cursor_index = start
            self._ensure_cursor_visible()

    def _delete_next_word(self):
        end = self._next_word_index(self.cursor_index)
        if end > self.cursor_index:
            self._record_undo_state()
            self.text_value = self.text_value[:self.cursor_index] + self.text_value[end:]
            self._ensure_cursor_visible()

    def _delete_to_line_start(self):
        if self.cursor_index > 0:
            self._record_undo_state()
            self.text_value = self.text_value[self.cursor_index:]
            self.cursor_index = 0
            self._ensure_cursor_visible()

    def _delete_to_line_end(self):
        if self.cursor_index < len(self.text_value):
            self._record_undo_state()
            self.text_value = self.text_value[:self.cursor_index]
            self._ensure_cursor_visible()

    def _delete_prev_char(self):
        if self.cursor_index <= 0:
            return
        self._record_undo_state()
        self.text_value = (
            self.text_value[:self.cursor_index - 1]
            + self.text_value[self.cursor_index:]
        )
        self.cursor_index -= 1
        self._ensure_cursor_visible()

    def _delete_next_char(self):
        if self.cursor_index >= len(self.text_value):
            return
        self._record_undo_state()
        self.text_value = (
            self.text_value[:self.cursor_index]
            + self.text_value[self.cursor_index + 1:]
        )
        self._ensure_cursor_visible()

    def cut_selected_text(self):
        if not self.has_selection():
            return
        self.copy_selected_text()
        self.delete_selection()
    
    def on_click(self, event):
        # self.dragging = True
        # self.cursor_index = self._mouse_to_index(event.pos[0])
        # self.selection_start = self.cursor_index
        # self.selection_end = None
        #print("onclick tetiklendi")
        self.handle_event(event)


    def handle_event(self, event:pygame.event.Event):
        if not self.enabled:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            button = getattr(event, "button", None)

            if button == 3:
                # Sag tik: context-menu ac
                clicked_index = self._mouse_to_index(event.pos[0])
                self._context_click_index = clicked_index

                # Secim yoksa imleci sag tiklanan pozisyona tasir.
                if not self.has_selection():
                    self.cursor_index = clicked_index
                    self._ensure_cursor_visible()
                self.open_context_menu(event.pos)
                return

        if not self.focused:
            return

        # MOUSE DRAG SELECTION
        if event.type == pygame.MOUSEMOTION:
            if self.dragging:
                idx = self._mouse_to_index(event.pos[0])
                self.selection_end = idx
                self.cursor_index = idx
                self._ensure_cursor_visible()

        if event.type == pygame.MOUSEBUTTONUP:
            button = getattr(event, "button", None)

            if button == 1:
                # Sol tik birakma: secim drag'i bitir
                self.dragging = False
                if self.selection_start == self.selection_end:
                    self.selection_start = self.selection_end = None
                #print(self.get_selected_text())
                #print("mouseup tetiklendi")
            elif button == 2:
                # Orta tik birakma: ileride davranis eklenebilir
                pass
            elif button == 3:
                # Sag tik birakma: ileride context-menu davranisi eklenebilir
                pass
            else:
                # Diger butonlar: simdilik islenmiyor
                pass
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            button = getattr(event, "button", None)

            if button == 1:
                now = time.time()
                click_pos = event.pos
                dx = click_pos[0] - self._last_click_pos[0]
                dy = click_pos[1] - self._last_click_pos[1]
                close_enough = (dx * dx + dy * dy) <= (self._multi_click_distance * self._multi_click_distance)

                if now - self._last_click_time <= self._multi_click_interval and close_enough:
                    self._click_count += 1
                else:
                    self._click_count = 1

                self._last_click_time = now
                self._last_click_pos = click_pos

                click_index = self._mouse_to_index(event.pos[0])

                if self._click_count >= 3:
                    self._select_all()
                    self.dragging = False
                elif self._click_count == 2:
                    start, end = self._find_word_bounds(click_index)
                    self._select_range(start, end)
                    self.dragging = False
                else:
                    self.dragging = True
                    self.cursor_index = click_index
                    self.selection_start = self.cursor_index
                    self.selection_end = None
                    self._ensure_cursor_visible()
            elif button == 2:
                # Orta tik: ileride davranis eklenebilir
                pass
            elif button == 3:
                # Sag tik birakma: context-menu zaten mousedown'da aciliyor
                pass
            else:
                # Diger butonlar: simdilik islenmiyor
                pass


        if event.type == pygame.KEYDOWN:
            mods = getattr(event, "mod", pygame.key.get_mods())
            has_ctrl_or_cmd = bool(mods & (pygame.KMOD_CTRL | pygame.KMOD_META))
            has_ctrl = bool(mods & pygame.KMOD_CTRL)
            has_cmd = bool(mods & pygame.KMOD_META)
            has_word_mod = bool(mods & (pygame.KMOD_CTRL | pygame.KMOD_ALT))
            has_shift = bool(mods & pygame.KMOD_SHIFT)

            # Kopyala / Yapistir kisayollari (Windows/Linux: Ctrl, macOS: Command)
            if has_ctrl_or_cmd and event.key == pygame.K_c:
                self.copy_selected_text()
                return

            if has_ctrl_or_cmd and event.key == pygame.K_v:
                self.paste_from_clipboard()
                self.text.set_text(self.text_value)
                return

            if has_ctrl_or_cmd and event.key == pygame.K_x:
                self.cut_selected_text()
                self.text.set_text(self.text_value)
                return

            if has_ctrl_or_cmd and event.key == pygame.K_a:
                self._select_all()
                self.text.set_text(self.text_value)
                return

            if has_ctrl_or_cmd and event.key == pygame.K_z:
                if has_shift:
                    self.redo()
                else:
                    self.undo()
                self.text.set_text(self.text_value)
                return

            if has_ctrl and not has_cmd and event.key == pygame.K_y:
                self.redo()
                self.text.set_text(self.text_value)
                return

            if event.key == pygame.K_ESCAPE:
                self._clear_selection()
                self.text.set_text(self.text_value)
                return

            # BACKSPACE
            if event.key == pygame.K_BACKSPACE:
                if self.has_selection():
                    self.delete_selection()
                elif has_cmd:
                    self._delete_to_line_start()
                elif has_word_mod:
                    self._delete_prev_word()
                elif self.cursor_index > 0:
                    self._delete_prev_char()

            elif event.key == pygame.K_DELETE:
                if self.has_selection():
                    self.delete_selection()
                elif has_cmd:
                    self._delete_to_line_end()
                elif has_word_mod:
                    self._delete_next_word()
                elif self.cursor_index < len(self.text_value):
                    self._delete_next_char()


            #arrow keys
            elif event.key == pygame.K_UP:
                self._move_cursor(0, keep_selection=has_shift)
            elif event.key == pygame.K_DOWN:
                self._move_cursor(len(self.text_value), keep_selection=has_shift)
            elif event.key == pygame.K_RIGHT:
                if self.has_selection() and not has_shift and not has_word_mod and not has_cmd:
                    _, end = self.get_selection_range()
                    self._move_cursor(end, keep_selection=False)
                else:
                    if has_cmd:
                        target = len(self.text_value)
                    elif has_word_mod:
                        target = self._next_word_index(self.cursor_index)
                    else:
                        target = min(len(self.text_value), self.cursor_index + 1)
                    self._move_cursor(target, keep_selection=has_shift)
            elif event.key == pygame.K_LEFT:
                if self.has_selection() and not has_shift and not has_word_mod and not has_cmd:
                    start, _ = self.get_selection_range()
                    self._move_cursor(start, keep_selection=False)
                else:
                    if has_cmd:
                        target = 0
                    elif has_word_mod:
                        target = self._prev_word_index(self.cursor_index)
                    else:
                        target = max(0, self.cursor_index - 1)
                    self._move_cursor(target, keep_selection=has_shift)
            
            
            
            # NORMAL CHARACTER
            elif event.unicode and event.unicode.isprintable():
                c:str = event.unicode
                if self.allowed_char_mode == ALLOW_ALL_CHARS:
                    self.insert_text(c)
                elif self.allowed_char_mode == TEXT_ONLY:
                    if c.isnumeric() == False:
                        self.insert_text(c)
                elif self.allowed_char_mode == NUMBER_ONLY:
                    if c.isnumeric():
                        self.insert_text(c)
                elif self.allowed_char_mode == HEX_ONLY:
                    if c.isnumeric() or c.capitalize() in "ABCDEF":
                        self.insert_text(c)
                elif self.allowed_char_mode == BINARY_ONLY:
                    if c in "10":
                        self.insert_text(c)
                elif self.allowed_char_mode == OCTAL_ONLY:
                    if c in "12345678":
                        self.insert_text(c)
                
                
                

            

            self.text.set_text(self.text_value)


    def has_selection(self):
        return (
            self.selection_start is not None
            and self.selection_end is not None
            and self.selection_start != self.selection_end
        )

    def get_selection_range(self):
        return sorted((self.selection_start, self.selection_end))

    def get_selected_text(self):
        try:
            a, b = self.get_selection_range()
            return self.text_value[a:b]
        except:
            return ""

    def delete_selection(self, record_history=True):
        a, b = self.get_selection_range()
        if record_history:
            self._record_undo_state()
        self.text_value = self.text_value[:a] + self.text_value[b:]
        self.cursor_index = a
        self.selection_start = self.selection_end = None
        self._ensure_cursor_visible()

    def insert_text(self, s, record_history=True):
        if self.has_selection():
            self.delete_selection(record_history=record_history)
            record_history = False

        if not s:
            return

        if record_history:
            self._record_undo_state()

        self.text_value = (
            self.text_value[:self.cursor_index]
            + s
            + self.text_value[self.cursor_index:]
        )
        self.cursor_index += len(s)
        self._ensure_cursor_visible()
    def update(self):
        if not self.focused:
            self.caret_visible = False
            return

        
        if time.time() - self.last_blinked_at >= self._caret_interval:
            self.last_blinked_at = time.time()
            self.caret_visible = not self.caret_visible

    def draw(self, surface):
        super().draw(surface)
        self.update()
        self._ensure_cursor_visible()

        inner_rect = self._get_inner_rect()
        text_x = self.absolute_rect[0] + self.padding - self._scroll_x
        text_y = self.absolute_rect[1] + self.padding

        prev_clip = surface.get_clip()
        surface.set_clip(inner_rect)

        # SELECTION
        if self.has_selection():
            a, b = self.get_selection_range()
            x1 = self.absolute_rect[0] + self.padding + self._text_width_until(a) - self._scroll_x
            x2 = self.absolute_rect[0] + self.padding + self._text_width_until(b) - self._scroll_x

            h = self.text.render.get_height()
            y = self.absolute_rect[1] + self.padding

            pygame.draw.rect(
                surface,
                self.selection_color,
                (x1, y, x2 - x1, h)
            )

        surface.blit(self.text.render, (text_x, text_y))

        # CARET
        if self.focused and self.caret_visible:
            cx = self.absolute_rect[0] + self.padding + self._text_width_until(self.cursor_index) - self._scroll_x
            cy = self.absolute_rect[1] + self.padding

            pygame.draw.rect(
                surface,
                self.caret_color,
                (cx, cy, 2, self.text.render.get_height())
            )

        surface.set_clip(prev_clip)



class TextInput2D(UIComponent):
    def __init__(
        self,
        rect,
        initial_text="",
        text_color=(0, 0, 0),
        bg_color=(220, 220, 220),
        hover_color=(240, 240, 240),
        selection_color=(100, 150, 255),
        caret_color=(0, 0, 0),
        padding=6,
        font_size=25,
        font_type='Veranda',
        z_index=0
    ):
        super().__init__(
            rect=rect,
            z_index=z_index,
            color=bg_color,
            hover_color=hover_color
        )

        self.text_color = text_color
        self.selection_color = selection_color
        self.caret_color = caret_color
        self.padding = padding
        self.font_size = font_size
        self.font_type = font_type
        self.font = pygame.font.SysFont(self.font_type, self.font_size)

        self.lines = initial_text.split('\n') if initial_text else ['']
        self.cursor_line = 0
        self.cursor_col = 0

        self.selection_start = None
        self.selection_end = None
        self.dragging = False

        # caret blink
        self.caret_visible = True
        self._caret_timer = 0
        self._caret_interval = 0.5
        self.last_blinked_at = time.time()
    
        #Keyboard repeat settings
    

    def get_text(self):
        return '\n'.join(self.lines)

    def set_text(self, text):
        self.lines = text.split('\n') if text else ['']
        self.cursor_line = min(self.cursor_line, len(self.lines) - 1)
        self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_line]))

    def _get_line_height(self):
        return self.font.get_height()

    def _get_text_width(self, text):
        return self.font.size(text)[0]

    def _mouse_to_pos(self, mouse_x, mouse_y):
        local_x = mouse_x - self.absolute_rect[0] - self.padding
        local_y = mouse_y - self.absolute_rect[1] - self.padding

        line_height = self._get_line_height()
        line = int(local_y // line_height)
        line = max(0, min(line, len(self.lines) - 1))

        line_text = self.lines[line]
        col = 0
        for i in range(len(line_text) + 1):
            if self._get_text_width(line_text[:i]) > local_x:
                col = i - 1
                break
        else:
            col = len(line_text)

        return line, col

    def on_click(self, event):
        self.dragging = True
        self.cursor_line, self.cursor_col = self._mouse_to_pos(event.pos[0], event.pos[1])
        self.selection_start = (self.cursor_line, self.cursor_col)
        self.selection_end = None

    def handle_event(self, event: pygame.event.Event):
        if not self.focused or not self.enabled:
            return

        # MOUSE DRAG SELECTION
        if event.type == pygame.MOUSEMOTION and self.dragging:
            line, col = self._mouse_to_pos(event.pos[0], event.pos[1])
            self.selection_end = (line, col)
            self.cursor_line, self.cursor_col = line, col

        if event.type == pygame.MOUSEBUTTONUP:
            button = getattr(event, "button", None)

            if button == 1:
                # Sol tik birakma: secim drag'i bitir
                self.dragging = False
                if self.selection_start == self.selection_end:
                    self.selection_start = self.selection_end = None
            elif button == 2:
                # Orta tik birakma: ileride davranis eklenebilir
                pass
            elif button == 3:
                # Sag tik birakma: ileride davranis eklenebilir
                pass
            else:
                # Diger butonlar: simdilik islenmiyor
                pass

        if event.type == pygame.KEYDOWN:
            # BACKSPACE
            if event.key == pygame.K_BACKSPACE:
                if self.has_selection():
                    self.delete_selection()
                elif self.cursor_col > 0:
                    self.lines[self.cursor_line] = (
                        self.lines[self.cursor_line][:self.cursor_col - 1]
                        + self.lines[self.cursor_line][self.cursor_col:]
                    )
                    self.cursor_col -= 1
                elif self.cursor_line > 0:
                    # Join with previous line
                    prev_line = self.lines[self.cursor_line - 1]
                    self.cursor_col = len(prev_line)
                    self.lines[self.cursor_line - 1] += self.lines[self.cursor_line]
                    del self.lines[self.cursor_line]
                    self.cursor_line -= 1

            # ENTER
            elif event.key == pygame.K_RETURN:
                if self.has_selection():
                    self.delete_selection()
                line = self.lines[self.cursor_line]
                self.lines[self.cursor_line] = line[:self.cursor_col]
                self.lines.insert(self.cursor_line + 1, line[self.cursor_col:])
                self.cursor_line += 1
                self.cursor_col = 0

            # ARROW KEYS
            elif event.key == pygame.K_LEFT:
                if self.cursor_col > 0:
                    self.cursor_col -= 1
                elif self.cursor_line > 0:
                    self.cursor_line -= 1
                    self.cursor_col = len(self.lines[self.cursor_line])
            elif event.key == pygame.K_RIGHT:
                if self.cursor_col < len(self.lines[self.cursor_line]):
                    self.cursor_col += 1
                elif self.cursor_line < len(self.lines) - 1:
                    self.cursor_line += 1
                    self.cursor_col = 0
            elif event.key == pygame.K_UP:
                if self.cursor_line > 0:
                    self.cursor_line -= 1
                    self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_line]))
            elif event.key == pygame.K_DOWN:
                if self.cursor_line < len(self.lines) - 1:
                    self.cursor_line += 1
                    self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_line]))

            # TYPING
            elif event.unicode and event.unicode.isprintable():
                if self.has_selection():
                    self.delete_selection()
                line = self.lines[self.cursor_line]
                self.lines[self.cursor_line] = line[:self.cursor_col] + event.unicode + line[self.cursor_col:]
                self.cursor_col += 1

    def has_selection(self):
        return (
            self.selection_start is not None
            and self.selection_end is not None
            and self.selection_start != self.selection_end
        )

    def get_selection_range(self):
        # For simplicity, assume single line selection or handle multi-line later
        # This is complex, for now assume same line
        if not self.has_selection():
            return None
        start_line, start_col = self.selection_start
        end_line, end_col = self.selection_end
        if start_line != end_line:
            # Multi-line selection, for now just clear
            return None
        return sorted((start_col, end_col))

    def delete_selection(self):
        if not self.has_selection():
            return
        start_line, start_col = self.selection_start
        end_line, end_col = self.selection_end
        if start_line == end_line:
            line = self.lines[start_line]
            a, b = sorted((start_col, end_col))
            self.lines[start_line] = line[:a] + line[b:]
            self.cursor_line = start_line
            self.cursor_col = a
        # Multi-line delete not implemented yet
        self.selection_start = self.selection_end = None

    def update(self):
        if not self.focused:
            self.caret_visible = False
            return

        if time.time() - self.last_blinked_at >= self._caret_interval:
            self.last_blinked_at = time.time()
            self.caret_visible = not self.caret_visible

    def draw(self, surface):
        super().draw(surface)
        self.update()

        line_height = self._get_line_height()
        y = self.absolute_rect[1] + self.padding

        for i, line in enumerate(self.lines):
            render = self.font.render(line, True, self.text_color)
            surface.blit(render, (self.absolute_rect[0] + self.padding, y))
            y += line_height

        # CARET
        if self.focused and self.caret_visible:
            caret_x = self.absolute_rect[0] + self.padding + self._get_text_width(self.lines[self.cursor_line][:self.cursor_col])
            caret_y = self.absolute_rect[1] + self.padding + self.cursor_line * line_height

            pygame.draw.rect(
                surface,
                self.caret_color,
                (caret_x, caret_y, 2, line_height)
            )

        # SELECTION - simplified, only same line
        if self.has_selection():
            sel_range = self.get_selection_range()
            if sel_range:
                a, b = sel_range
                line = self.lines[self.cursor_line]
                x1 = self.absolute_rect[0] + self.padding + self._get_text_width(line[:a])
                x2 = self.absolute_rect[0] + self.padding + self._get_text_width(line[:b])
                y = self.absolute_rect[1] + self.padding + self.cursor_line * line_height

                pygame.draw.rect(
                    surface,
                    self.selection_color,
                    (x1, y, x2 - x1, line_height)
                )


