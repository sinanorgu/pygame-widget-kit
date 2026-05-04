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



class __TextInput(UIComponent):
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
        self._typing_burst_active = False
        self._typing_burst_last_cursor = None
        self._delete_burst_active = False
        self._delete_burst_mode = None
        self._delete_burst_last_cursor = None
        self._delete_burst_word_char = None

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
        self._reset_typing_burst()
        self._ensure_cursor_visible()

    def _record_undo_state(self):
        state = self._snapshot_state()
        if self._undo_stack and self._undo_stack[-1] == state:
            return

        self._undo_stack.append(state)
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def _reset_typing_burst(self):
        self._typing_burst_active = False
        self._typing_burst_last_cursor = None
        self._reset_delete_burst()

    def _reset_typing_burst_only(self):
        self._typing_burst_active = False
        self._typing_burst_last_cursor = None

    def _reset_delete_burst(self):
        self._delete_burst_active = False
        self._delete_burst_mode = None
        self._delete_burst_last_cursor = None
        self._delete_burst_word_char = None

    def _begin_delete_burst(self, mode: str, cursor_index: int, is_word_char=None):
        should_continue = (
            self._delete_burst_active
            and self._delete_burst_mode == mode
            and self._delete_burst_last_cursor == cursor_index
            and self._delete_burst_word_char == is_word_char
            and not self.has_selection()
        )
        if not should_continue:
            self._record_undo_state()

    def _commit_delete_burst(self, mode: str, is_word_char=None):
        self._delete_burst_active = True
        self._delete_burst_mode = mode
        self._delete_burst_last_cursor = self.cursor_index
        self._delete_burst_word_char = is_word_char

    def _insert_typed_char(self, ch: str):
        is_word_char = self._is_word_char(ch)
        should_continue_word_burst = (
            is_word_char
            and self._typing_burst_active
            and self._typing_burst_last_cursor == self.cursor_index
            and not self.has_selection()
        )

        if not should_continue_word_burst:
            self._record_undo_state()

        if self.has_selection():
            self.delete_selection(record_history=False)

        self.text_value = (
            self.text_value[:self.cursor_index]
            + ch
            + self.text_value[self.cursor_index:]
        )
        self.cursor_index += 1
        self._ensure_cursor_visible()

        if is_word_char:
            self._typing_burst_active = True
            self._typing_burst_last_cursor = self.cursor_index
        else:
            self._reset_typing_burst()

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
        self._reset_typing_burst()
        self._ensure_cursor_visible()

    def _select_all(self):
        self.selection_start = 0
        self.selection_end = len(self.text_value)
        self.cursor_index = len(self.text_value)
        self._reset_typing_burst()
        self._ensure_cursor_visible()

    def _clear_selection(self):
        self.selection_start = None
        self.selection_end = None
        self._reset_typing_burst()

    def _move_cursor(self, target_index: int, keep_selection: bool):
        target_index = max(0, min(target_index, len(self.text_value)))

        if keep_selection:
            if self.selection_start is None:
                self.selection_start = self.cursor_index
            self.selection_end = target_index
        else:
            self._clear_selection()

        self.cursor_index = target_index
        self._reset_typing_burst()
        self._ensure_cursor_visible()

    def _delete_prev_word(self):
        start = self._prev_word_index(self.cursor_index)
        if start < self.cursor_index:
            self._begin_delete_burst("delete-prev-word", self.cursor_index)
            self._reset_typing_burst_only()
            self.text_value = self.text_value[:start] + self.text_value[self.cursor_index:]
            self.cursor_index = start
            self._ensure_cursor_visible()
            self._commit_delete_burst("delete-prev-word")

    def _delete_next_word(self):
        end = self._next_word_index(self.cursor_index)
        if end > self.cursor_index:
            self._begin_delete_burst("delete-next-word", self.cursor_index)
            self._reset_typing_burst_only()
            self.text_value = self.text_value[:self.cursor_index] + self.text_value[end:]
            self._ensure_cursor_visible()
            self._commit_delete_burst("delete-next-word")

    def _delete_to_line_start(self):
        if self.cursor_index > 0:
            self._begin_delete_burst("delete-to-start", self.cursor_index)
            self._reset_typing_burst_only()
            self.text_value = self.text_value[self.cursor_index:]
            self.cursor_index = 0
            self._ensure_cursor_visible()
            self._commit_delete_burst("delete-to-start")

    def _delete_to_line_end(self):
        if self.cursor_index < len(self.text_value):
            self._begin_delete_burst("delete-to-end", self.cursor_index)
            self._reset_typing_burst_only()
            self.text_value = self.text_value[:self.cursor_index]
            self._ensure_cursor_visible()
            self._commit_delete_burst("delete-to-end")

    def _delete_prev_char(self):
        if self.cursor_index <= 0:
            return
        deleted_char = self.text_value[self.cursor_index - 1]
        deleted_is_word = self._is_word_char(deleted_char)
        self._begin_delete_burst("delete-prev-char", self.cursor_index, deleted_is_word)
        self._reset_typing_burst_only()
        self.text_value = (
            self.text_value[:self.cursor_index - 1]
            + self.text_value[self.cursor_index:]
        )
        self.cursor_index -= 1
        self._ensure_cursor_visible()
        self._commit_delete_burst("delete-prev-char", deleted_is_word)

    def _delete_next_char(self):
        if self.cursor_index >= len(self.text_value):
            return
        deleted_char = self.text_value[self.cursor_index]
        deleted_is_word = self._is_word_char(deleted_char)
        self._begin_delete_burst("delete-next-char", self.cursor_index, deleted_is_word)
        self._reset_typing_burst_only()
        self.text_value = (
            self.text_value[:self.cursor_index]
            + self.text_value[self.cursor_index + 1:]
        )
        self._ensure_cursor_visible()
        self._commit_delete_burst("delete-next-char", deleted_is_word)

    def cut_selected_text(self):
        if not self.has_selection():
            return
        self._reset_typing_burst()
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
                self._reset_typing_burst()
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
                self._reset_typing_burst()
                idx = self._mouse_to_index(event.pos[0])
                self.selection_end = idx
                self.cursor_index = idx
                self._ensure_cursor_visible()

        if event.type == pygame.MOUSEBUTTONUP:
            button = getattr(event, "button", None)

            if button == 1:
                self._reset_typing_burst()
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
                mods = getattr(event, "mod", pygame.key.get_mods())
                has_shift = bool(mods & pygame.KMOD_SHIFT)
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
                    if has_shift:
                        anchor = self.selection_start if self.selection_start is not None else self.cursor_index
                        self.selection_start = anchor
                        self.selection_end = click_index
                        self.cursor_index = click_index
                    else:
                        self.cursor_index = click_index
                        self.selection_start = self.cursor_index
                        self.selection_end = None
                    self._reset_typing_burst()
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
                self._reset_typing_burst()
                self.copy_selected_text()
                return

            if has_ctrl_or_cmd and event.key == pygame.K_v:
                self._reset_typing_burst()
                self.paste_from_clipboard()
                self.text.set_text(self.text_value)
                return

            if has_ctrl_or_cmd and event.key == pygame.K_x:
                self._reset_typing_burst()
                self.cut_selected_text()
                self.text.set_text(self.text_value)
                return

            if has_ctrl_or_cmd and event.key == pygame.K_a:
                self._select_all()
                self.text.set_text(self.text_value)
                return

            if has_ctrl_or_cmd and event.key == pygame.K_z:
                self._reset_typing_burst()
                if has_shift:
                    self.redo()
                else:
                    self.undo()
                self.text.set_text(self.text_value)
                return

            if has_ctrl and not has_cmd and event.key == pygame.K_y:
                self._reset_typing_burst()
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
                    self._insert_typed_char(c)
                elif self.allowed_char_mode == TEXT_ONLY:
                    if c.isnumeric() == False:
                        self._insert_typed_char(c)
                elif self.allowed_char_mode == NUMBER_ONLY:
                    if c.isnumeric():
                        self._insert_typed_char(c)
                elif self.allowed_char_mode == HEX_ONLY:
                    if c.isnumeric() or c.capitalize() in "ABCDEF":
                        self._insert_typed_char(c)
                elif self.allowed_char_mode == BINARY_ONLY:
                    if c in "10":
                        self._insert_typed_char(c)
                elif self.allowed_char_mode == OCTAL_ONLY:
                    if c in "12345678":
                        self._insert_typed_char(c)
                
                
                

            

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
        self._reset_typing_burst()
        if record_history:
            self._record_undo_state()
        self.text_value = self.text_value[:a] + self.text_value[b:]
        self.cursor_index = a
        self.selection_start = self.selection_end = None
        self._ensure_cursor_visible()

    def insert_text(self, s, record_history=True):
        self._reset_typing_burst()
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
        effective_clip = inner_rect.clip(prev_clip)
        surface.set_clip(effective_clip)

        if effective_clip.width > 0 and effective_clip.height > 0:
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



class TextInput(UIComponent):
    def __init__(
        self,
        rect,
        initial_text="",
        allow_multiline=True,
        allowed_char_mode: int = ALLOW_ALL_CHARS,
        text_color=(0, 0, 0),
        bg_color=(220, 220, 220),
        hover_color=(220, 220, 220),
        active_color=(220, 220, 220),
        border_color=(160, 160, 160),
        selection_color=(100, 150, 255),
        caret_color=(0, 0, 0),
        padding=6,
        font_size=25,
        font_type='Veranda',
        show_scrollbars=False,
        z_index=0
    ):
        super().__init__(
            rect=rect,
            z_index=z_index,
            color=bg_color,
            hover_color=hover_color,
            color_active=active_color,
            border_color=border_color
        )

        self.allow_multiline = allow_multiline
        self.allowed_char_mode = allowed_char_mode
        self.scrollable = True
        self.text_color = text_color
        self.selection_color = selection_color
        self.caret_color = caret_color
        self.padding = padding
        self.font_size = font_size
        self.font_type = font_type
        self.font = pygame.font.SysFont(self.font_type, self.font_size)
        self.show_scrollbars = show_scrollbars
        self._scrollbar_size = 12
        self._scrollbar_min_thumb = 20
        self._scrollbar_track_color = (210, 210, 210)
        self._scrollbar_thumb_color = (150, 150, 150)

        self.lines = initial_text.split('\n') if initial_text else ['']
        self.cursor_line = 0
        self.cursor_col = 0
        if self.lines:
            self.cursor_line = len(self.lines) - 1
            self.cursor_col = len(self.lines[self.cursor_line])

        self.selection_start = None
        self.selection_end = None
        self.dragging = False
        self._preferred_col = None

        # caret blink
        self.caret_visible = True
        self._caret_interval = 0.5
        self.last_blinked_at = time.time()

        self.context_menu: TextInputContextMenu | None = None
        self._clipboard_cache = ""
        self._context_click_pos = (self.cursor_line, self.cursor_col)
        self._last_click_time = 0.0
        self._last_click_pos = (0, 0)
        self._click_count = 0
        self._multi_click_interval = 0.35
        self._multi_click_distance = 6

        self._undo_stack = []
        self._redo_stack = []
        self._max_history = 200
        self._typing_burst_active = False
        self._typing_burst_last_offset = None
        self._delete_burst_active = False
        self._delete_burst_mode = None
        self._delete_burst_last_offset = None
        self._delete_burst_word_char = None

        self._scroll_x = 0
        self._scroll_y = 0
        self._scroll_drag_mode = None
        self._scroll_drag_offset = 0
        self._tab_spaces = 4

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

    def _get_line_height(self):
        return self.font.get_height()

    def _get_text_width(self, text):
        return self.font.size(text)[0]

    def _get_inner_rect(self):
        return pygame.Rect(
            self.absolute_rect[0] + self.padding,
            self.absolute_rect[1] + self.padding,
            max(1, self.absolute_rect[2] - self.padding * 2),
            max(1, self.absolute_rect[3] - self.padding * 2),
        )

    def _line_y(self, line_index: int) -> int:
        _, content_rect, _, _ = self._get_content_layout()
        return content_rect.y + line_index * self._get_line_height() - self._scroll_y

    def _get_text(self) -> str:
        return "\n".join(self.lines)

    def _get_content_layout(self):
        inner = self._get_inner_rect()

        if not self.show_scrollbars:
            return inner, inner, False, False

        line_height = self._get_line_height()
        total_h = len(self.lines) * line_height
        max_line_width = 0
        for line in self.lines:
            max_line_width = max(max_line_width, self._get_text_width(line))

        show_h = False
        show_v = False

        # Resolve coupling: vertical bar shrinks width, horizontal bar shrinks height.
        for _ in range(3):
            content_w = max(1, inner.width - (self._scrollbar_size if show_v else 0))
            content_h = max(1, inner.height - (self._scrollbar_size if show_h else 0))

            next_show_h = max_line_width > content_w
            next_show_v = total_h > content_h

            if next_show_h == show_h and next_show_v == show_v:
                break
            show_h, show_v = next_show_h, next_show_v

        content_rect = pygame.Rect(
            inner.x,
            inner.y,
            max(1, inner.width - (self._scrollbar_size if show_v else 0)),
            max(1, inner.height - (self._scrollbar_size if show_h else 0)),
        )
        return inner, content_rect, show_h, show_v

    def get_text(self):
        return self._get_text()

    def get_value(self):
        return self._get_text()

    def set_value(self, value: str):
        self.set_text(value)

    def _normalize_pos(self, pos):
        line, col = pos
        line = max(0, min(line, len(self.lines) - 1))
        col = max(0, min(col, len(self.lines[line])))
        return line, col

    def _pos_to_offset(self, pos):
        line, col = self._normalize_pos(pos)
        offset = 0
        for i in range(line):
            offset += len(self.lines[i]) + 1
        return offset + col

    def _offset_to_pos(self, offset):
        text = self._get_text()
        offset = max(0, min(offset, len(text)))

        running = 0
        for i, line in enumerate(self.lines):
            line_end = running + len(line)
            if offset <= line_end:
                return i, offset - running
            running = line_end + 1
        return len(self.lines) - 1, len(self.lines[-1])

    def _set_text_and_cursor_offset(self, text: str, cursor_offset: int):
        if not self.allow_multiline:
            text = text.replace("\r", "").replace("\n", "")
        else:
            text = text.replace("\r\n", "\n").replace("\r", "\n")

        self.lines = text.split("\n") if text else [""]
        self.cursor_line, self.cursor_col = self._offset_to_pos(cursor_offset)
        self._preferred_col = None
        self._ensure_cursor_visible()

    def set_text(self, text):
        self._set_text_and_cursor_offset(text if text is not None else "", 0)
        self._clear_selection()

    def clear(self):
        self.set_text("")

    def _is_word_char(self, ch: str) -> bool:
        return ch.isalnum() or ch == "_"

    def _find_word_bounds_offset(self, index: int):
        text = self._get_text()
        n = len(text)
        if n == 0:
            return 0, 0

        index = max(0, min(index, n))
        probe = index if index < n else n - 1

        if not self._is_word_char(text[probe]):
            return probe, probe + 1

        start = probe
        end = probe + 1
        while start > 0 and self._is_word_char(text[start - 1]):
            start -= 1
        while end < n and self._is_word_char(text[end]):
            end += 1
        return start, end

    def _next_word_offset(self, index: int):
        text = self._get_text()
        n = len(text)
        i = max(0, min(index, n))
        while i < n and self._is_word_char(text[i]):
            i += 1
        while i < n and not self._is_word_char(text[i]):
            i += 1
        return i

    def _prev_word_offset(self, index: int):
        text = self._get_text()
        i = max(0, min(index, len(text)))
        while i > 0 and not self._is_word_char(text[i - 1]):
            i -= 1
        while i > 0 and self._is_word_char(text[i - 1]):
            i -= 1
        return i

    def _max_scroll_x(self):
        _, content_rect, _, _ = self._get_content_layout()
        max_line_width = 0
        for line in self.lines:
            max_line_width = max(max_line_width, self._get_text_width(line))
        return max(0, max_line_width - content_rect.width)

    def _max_scroll_y(self):
        _, content_rect, _, _ = self._get_content_layout()
        total_h = len(self.lines) * self._get_line_height()
        return max(0, total_h - content_rect.height)

    def _clamp_scroll(self):
        self._scroll_x = max(0, min(self._scroll_x, self._max_scroll_x()))
        self._scroll_y = max(0, min(self._scroll_y, self._max_scroll_y()))

    def _ensure_cursor_visible(self):
        _, content_rect, _, _ = self._get_content_layout()
        line = self.lines[self.cursor_line]
        caret_x = self._get_text_width(line[:self.cursor_col])
        left_visible = self._scroll_x
        right_visible = self._scroll_x + content_rect.width - 2

        if caret_x < left_visible:
            self._scroll_x = caret_x
        elif caret_x > right_visible:
            self._scroll_x = caret_x - (content_rect.width - 2)

        caret_top = self.cursor_line * self._get_line_height()
        caret_bottom = caret_top + self._get_line_height()
        top_visible = self._scroll_y
        bottom_visible = self._scroll_y + content_rect.height

        if caret_top < top_visible:
            self._scroll_y = caret_top
        elif caret_bottom > bottom_visible:
            self._scroll_y = caret_bottom - content_rect.height

        self._clamp_scroll()

    def _mouse_to_pos(self, mouse_x, mouse_y):
        _, content_rect, _, _ = self._get_content_layout()
        local_x = mouse_x - content_rect.x + self._scroll_x
        local_y = mouse_y - content_rect.y + self._scroll_y

        line_height = self._get_line_height()
        line = int(local_y // line_height)
        line = max(0, min(line, len(self.lines) - 1))

        line_text = self.lines[line]
        if local_x <= 0:
            return line, 0

        col = len(line_text)
        for i in range(len(line_text) + 1):
            if self._get_text_width(line_text[:i]) >= local_x:
                col = i
                break

        return line, col

    def _snapshot_state(self):
        return (
            self._get_text(),
            self.cursor_line,
            self.cursor_col,
            self.selection_start,
            self.selection_end,
            self._scroll_x,
            self._scroll_y,
        )

    def _restore_state(self, state):
        (
            text,
            self.cursor_line,
            self.cursor_col,
            self.selection_start,
            self.selection_end,
            self._scroll_x,
            self._scroll_y,
        ) = state

        self.lines = text.split("\n") if text else [""]
        self.cursor_line, self.cursor_col = self._normalize_pos((self.cursor_line, self.cursor_col))
        self._clamp_scroll()
        self._reset_typing_burst()
        self._ensure_cursor_visible()

    def _record_undo_state(self):
        state = self._snapshot_state()
        if self._undo_stack and self._undo_stack[-1] == state:
            return
        self._undo_stack.append(state)
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def _reset_typing_burst(self):
        self._typing_burst_active = False
        self._typing_burst_last_offset = None
        self._reset_delete_burst()

    def _reset_typing_burst_only(self):
        self._typing_burst_active = False
        self._typing_burst_last_offset = None

    def _reset_delete_burst(self):
        self._delete_burst_active = False
        self._delete_burst_mode = None
        self._delete_burst_last_offset = None
        self._delete_burst_word_char = None

    def _begin_delete_burst(self, mode: str, cursor_offset: int, is_word_char=None):
        should_continue = (
            self._delete_burst_active
            and self._delete_burst_mode == mode
            and self._delete_burst_last_offset == cursor_offset
            and self._delete_burst_word_char == is_word_char
            and not self.has_selection()
        )
        if not should_continue:
            self._record_undo_state()

    def _commit_delete_burst(self, mode: str, is_word_char=None):
        self._delete_burst_active = True
        self._delete_burst_mode = mode
        self._delete_burst_last_offset = self._pos_to_offset((self.cursor_line, self.cursor_col))
        self._delete_burst_word_char = is_word_char

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

    def _selection_bounds(self):
        if not self.has_selection():
            return None
        a = self._pos_to_offset(self.selection_start)
        b = self._pos_to_offset(self.selection_end)
        if a <= b:
            return self.selection_start, self.selection_end, a, b
        return self.selection_end, self.selection_start, b, a

    def has_selection(self):
        return (
            self.selection_start is not None
            and self.selection_end is not None
            and self.selection_start != self.selection_end
        )

    def get_selection_range(self):
        bounds = self._selection_bounds()
        if bounds is None:
            return None
        start_pos, end_pos, _, _ = bounds
        return start_pos, end_pos

    def get_selected_text(self):
        bounds = self._selection_bounds()
        if bounds is None:
            return ""
        _, _, a, b = bounds
        return self._get_text()[a:b]

    def _clear_selection(self):
        self.selection_start = None
        self.selection_end = None
        self._reset_typing_burst()

    def _set_cursor_pos(self, pos, keep_selection=False):
        pos = self._normalize_pos(pos)
        if keep_selection:
            if self.selection_start is None:
                self.selection_start = (self.cursor_line, self.cursor_col)
            self.selection_end = pos
        else:
            self._clear_selection()

        self.cursor_line, self.cursor_col = pos
        self._ensure_cursor_visible()

    def _select_range(self, start_pos, end_pos):
        self.selection_start = self._normalize_pos(start_pos)
        self.selection_end = self._normalize_pos(end_pos)
        self.cursor_line, self.cursor_col = self.selection_end
        self._reset_typing_burst()
        self._ensure_cursor_visible()

    def _select_all(self):
        end_pos = (len(self.lines) - 1, len(self.lines[-1]))
        self._select_range((0, 0), end_pos)

    def delete_selection(self, record_history=True):
        bounds = self._selection_bounds()
        if bounds is None:
            return

        _, _, a, b = bounds
        if record_history:
            self._record_undo_state()

        self._reset_typing_burst()
        text = self._get_text()
        new_text = text[:a] + text[b:]
        self._set_text_and_cursor_offset(new_text, a)
        self.selection_start = None
        self.selection_end = None

    def _filter_text(self, incoming_text: str) -> str:
        if incoming_text is None:
            return ""

        text = incoming_text.replace("\r\n", "\n").replace("\r", "\n")
        out = []
        for ch in text:
            if ch == "\n":
                if self.allow_multiline:
                    out.append(ch)
                continue

            if not ch.isprintable():
                continue

            if self.allowed_char_mode == ALLOW_ALL_CHARS:
                out.append(ch)
            elif self.allowed_char_mode == TEXT_ONLY:
                if not ch.isnumeric():
                    out.append(ch)
            elif self.allowed_char_mode == NUMBER_ONLY:
                if ch.isnumeric():
                    out.append(ch)
            elif self.allowed_char_mode == HEX_ONLY:
                if ch.isnumeric() or ch.capitalize() in "ABCDEF":
                    out.append(ch)
            elif self.allowed_char_mode == BINARY_ONLY:
                if ch in "10":
                    out.append(ch)
            elif self.allowed_char_mode == OCTAL_ONLY:
                if ch in "01234567":
                    out.append(ch)

        return "".join(out)

    def insert_text(self, s, record_history=True):
        self._reset_typing_burst()
        if self.has_selection():
            self.delete_selection(record_history=record_history)
            record_history = False

        if not s:
            return

        filtered = self._filter_text(s)
        if not filtered:
            return

        if record_history:
            self._record_undo_state()

        text = self._get_text()
        cursor_offset = self._pos_to_offset((self.cursor_line, self.cursor_col))
        new_text = text[:cursor_offset] + filtered + text[cursor_offset:]
        self._set_text_and_cursor_offset(new_text, cursor_offset + len(filtered))

    def _insert_typed_char(self, ch: str):
        is_word_char = self._is_word_char(ch)
        cursor_offset = self._pos_to_offset((self.cursor_line, self.cursor_col))

        should_continue_word_burst = (
            is_word_char
            and self._typing_burst_active
            and self._typing_burst_last_offset == cursor_offset
            and not self.has_selection()
        )

        if not should_continue_word_burst:
            self._record_undo_state()

        if self.has_selection():
            self.delete_selection(record_history=False)

        self.insert_text(ch, record_history=False)

        new_offset = self._pos_to_offset((self.cursor_line, self.cursor_col))
        if is_word_char:
            self._typing_burst_active = True
            self._typing_burst_last_offset = new_offset
        else:
            self._reset_typing_burst()

    def _delete_prev_char(self):
        cursor_offset = self._pos_to_offset((self.cursor_line, self.cursor_col))
        if cursor_offset <= 0:
            return
        text = self._get_text()
        deleted_is_word = self._is_word_char(text[cursor_offset - 1])
        self._begin_delete_burst("delete-prev-char", cursor_offset, deleted_is_word)
        self._reset_typing_burst_only()
        new_text = text[:cursor_offset - 1] + text[cursor_offset:]
        self._set_text_and_cursor_offset(new_text, cursor_offset - 1)
        self._commit_delete_burst("delete-prev-char", deleted_is_word)

    def _delete_next_char(self):
        text = self._get_text()
        cursor_offset = self._pos_to_offset((self.cursor_line, self.cursor_col))
        if cursor_offset >= len(text):
            return
        deleted_is_word = self._is_word_char(text[cursor_offset])
        self._begin_delete_burst("delete-next-char", cursor_offset, deleted_is_word)
        self._reset_typing_burst_only()
        new_text = text[:cursor_offset] + text[cursor_offset + 1:]
        self._set_text_and_cursor_offset(new_text, cursor_offset)
        self._commit_delete_burst("delete-next-char", deleted_is_word)

    def _delete_prev_word(self):
        cursor_offset = self._pos_to_offset((self.cursor_line, self.cursor_col))
        start = self._prev_word_offset(cursor_offset)
        if start >= cursor_offset:
            return
        self._begin_delete_burst("delete-prev-word", cursor_offset)
        self._reset_typing_burst_only()
        text = self._get_text()
        new_text = text[:start] + text[cursor_offset:]
        self._set_text_and_cursor_offset(new_text, start)
        self._commit_delete_burst("delete-prev-word")

    def _delete_next_word(self):
        cursor_offset = self._pos_to_offset((self.cursor_line, self.cursor_col))
        end = self._next_word_offset(cursor_offset)
        if end <= cursor_offset:
            return
        self._begin_delete_burst("delete-next-word", cursor_offset)
        self._reset_typing_burst_only()
        text = self._get_text()
        new_text = text[:cursor_offset] + text[end:]
        self._set_text_and_cursor_offset(new_text, cursor_offset)
        self._commit_delete_burst("delete-next-word")

    def _delete_to_line_start(self):
        if self.cursor_col <= 0:
            return
        cursor_offset = self._pos_to_offset((self.cursor_line, self.cursor_col))
        self._begin_delete_burst("delete-to-start", cursor_offset)
        self._reset_typing_burst_only()
        line = self.lines[self.cursor_line]
        self.lines[self.cursor_line] = line[self.cursor_col:]
        self.cursor_col = 0
        self._ensure_cursor_visible()
        self._commit_delete_burst("delete-to-start")

    def _delete_to_line_end(self):
        line = self.lines[self.cursor_line]
        if self.cursor_col >= len(line):
            return
        cursor_offset = self._pos_to_offset((self.cursor_line, self.cursor_col))
        self._begin_delete_burst("delete-to-end", cursor_offset)
        self._reset_typing_burst_only()
        self.lines[self.cursor_line] = line[:self.cursor_col]
        self._ensure_cursor_visible()
        self._commit_delete_burst("delete-to-end")

    def _current_line_start_pos(self):
        return self.cursor_line, 0

    def _current_line_end_pos(self):
        return self.cursor_line, len(self.lines[self.cursor_line])

    def _doc_start_pos(self):
        return 0, 0

    def _doc_end_pos(self):
        return len(self.lines) - 1, len(self.lines[-1])

    def _move_by_offset_delta(self, delta: int, keep_selection: bool):
        current = self._pos_to_offset((self.cursor_line, self.cursor_col))
        target = current + delta
        self._set_cursor_pos(self._offset_to_pos(target), keep_selection=keep_selection)

    def copy_selected_text(self):
        text_to_copy = self.get_selected_text() if self.has_selection() else self._get_text()
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

        if not paste_text:
            return

        filtered = self._filter_text(paste_text)
        should_edit = self.has_selection() or bool(filtered)
        if not should_edit:
            return

        self._record_undo_state()
        if self.has_selection():
            self.delete_selection(record_history=False)
        if filtered:
            self.insert_text(filtered, record_history=False)

    def cut_selected_text(self):
        if not self.has_selection():
            return
        self._reset_typing_burst()
        self.copy_selected_text()
        self.delete_selection()

    def prepare_context_action_for_copy(self):
        if self.ui_manager is not None:
            if self.ui_manager.focused and self.ui_manager.focused != self:
                self.ui_manager.focused.on_blur()
            self.ui_manager.focused = self
        self.on_focus()

    def prepare_context_action_for_paste(self):
        self.prepare_context_action_for_copy()
        if not self.has_selection():
            self.cursor_line, self.cursor_col = self._context_click_pos
            self._ensure_cursor_visible()

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

        menu_x = max(root_rect[0], min(menu_x, max_x))
        menu_y = max(root_rect[1], min(menu_y, max_y))

        self._context_click_pos = self._mouse_to_pos(pos[0], pos[1])

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

    def on_click(self, event):
        self.handle_event(event)

    def handle_event(self, event: pygame.event.Event):
        if not self.enabled:
            return

        if event.type == pygame.MOUSEMOTION and self._scroll_drag_mode is not None:
            self._scrollbar_set_from_pointer(self._scroll_drag_mode, event.pos, self._scroll_drag_offset)
            return

        if event.type == pygame.MOUSEBUTTONUP and getattr(event, "button", None) == 1 and self._scroll_drag_mode is not None:
            self._scroll_drag_mode = None
            self._scroll_drag_offset = 0
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            button = getattr(event, "button", None)

            if button == 1 and self.show_scrollbars:
                geometry = self._get_scrollbar_geometry()
                inner_rect = geometry["inner_rect"]
                content_rect = geometry["content_rect"]

                v_track = geometry["v_track"]
                v_thumb = geometry["v_thumb"]
                if v_track is not None and v_track.collidepoint(event.pos):
                    self.dragging = False
                    if v_thumb is not None and v_thumb.collidepoint(event.pos):
                        self._scroll_drag_mode = "v"
                        self._scroll_drag_offset = event.pos[1] - v_thumb.y
                    elif v_thumb is not None:
                        self._scroll_drag_mode = "v"
                        self._scroll_drag_offset = v_thumb.height // 2
                        self._scrollbar_set_from_pointer("v", event.pos, self._scroll_drag_offset)
                    return

                h_track = geometry["h_track"]
                h_thumb = geometry["h_thumb"]
                if h_track is not None and h_track.collidepoint(event.pos):
                    self.dragging = False
                    if h_thumb is not None and h_thumb.collidepoint(event.pos):
                        self._scroll_drag_mode = "h"
                        self._scroll_drag_offset = event.pos[0] - h_thumb.x
                    elif h_thumb is not None:
                        self._scroll_drag_mode = "h"
                        self._scroll_drag_offset = h_thumb.width // 2
                        self._scrollbar_set_from_pointer("h", event.pos, self._scroll_drag_offset)
                    return

                # Scrollbar region (including bottom-right corner) should never start text selection.
                if inner_rect.collidepoint(event.pos) and not content_rect.collidepoint(event.pos):
                    self.dragging = False
                    return

            if button == 3:
                self._reset_typing_burst()
                clicked_pos = self._mouse_to_pos(event.pos[0], event.pos[1])
                self._context_click_pos = clicked_pos
                if not self.has_selection():
                    self.cursor_line, self.cursor_col = clicked_pos
                    self._ensure_cursor_visible()
                self.open_context_menu(event.pos)
                return

            if button == 4:
                self._scroll_y = max(0, self._scroll_y - self._get_line_height() * 3)
                self._clamp_scroll()
                return
            if button == 5:
                self._scroll_y += self._get_line_height() * 3
                self._clamp_scroll()
                return

        if event.type == pygame.MOUSEWHEEL and self.focused:
            self._scroll_y -= event.y * self._get_line_height() * 3
            self._clamp_scroll()
            return

        if not self.focused:
            return

        if event.type == pygame.MOUSEMOTION and self.dragging:
            self._reset_typing_burst()
            pos = self._mouse_to_pos(event.pos[0], event.pos[1])
            self.selection_end = pos
            self.cursor_line, self.cursor_col = pos
            self._preferred_col = None
            self._ensure_cursor_visible()

        if event.type == pygame.MOUSEBUTTONUP:
            button = getattr(event, "button", None)
            if button == 1:
                self._reset_typing_burst()
                self.dragging = False
                if self.selection_start == self.selection_end:
                    self.selection_start = self.selection_end = None
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            button = getattr(event, "button", None)
            if button == 1:
                _, content_rect, _, _ = self._get_content_layout()
                if not content_rect.collidepoint(event.pos):
                    self.dragging = False
                    return

                mods = getattr(event, "mod", pygame.key.get_mods())
                has_shift = bool(mods & pygame.KMOD_SHIFT)
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

                click_cursor = self._mouse_to_pos(event.pos[0], event.pos[1])
                click_offset = self._pos_to_offset(click_cursor)

                if self._click_count >= 3:
                    line_idx = click_cursor[0]
                    self._select_range((line_idx, 0), (line_idx, len(self.lines[line_idx])))
                    self.dragging = False
                elif self._click_count == 2:
                    start_off, end_off = self._find_word_bounds_offset(click_offset)
                    self._select_range(self._offset_to_pos(start_off), self._offset_to_pos(end_off))
                    self.dragging = False
                else:
                    self.dragging = True
                    if has_shift:
                        anchor = self.selection_start if self.selection_start is not None else (self.cursor_line, self.cursor_col)
                        self.selection_start = anchor
                        self.selection_end = click_cursor
                        self.cursor_line, self.cursor_col = click_cursor
                    else:
                        self.cursor_line, self.cursor_col = click_cursor
                        self.selection_start = (self.cursor_line, self.cursor_col)
                        self.selection_end = None

                    self._preferred_col = None
                    self._reset_typing_burst()
                    self._ensure_cursor_visible()
                return

        if event.type != pygame.KEYDOWN:
            return

        mods = getattr(event, "mod", pygame.key.get_mods())
        has_ctrl_or_cmd = bool(mods & (pygame.KMOD_CTRL | pygame.KMOD_META))
        has_ctrl = bool(mods & pygame.KMOD_CTRL)
        has_cmd = bool(mods & pygame.KMOD_META)
        has_word_mod = bool(mods & (pygame.KMOD_CTRL | pygame.KMOD_ALT))
        has_shift = bool(mods & pygame.KMOD_SHIFT)

        if has_ctrl_or_cmd and event.key == pygame.K_c:
            self._reset_typing_burst()
            self.copy_selected_text()
            return

        if has_ctrl_or_cmd and event.key == pygame.K_v:
            self._reset_typing_burst()
            self.paste_from_clipboard()
            return

        if has_ctrl_or_cmd and event.key == pygame.K_x:
            self._reset_typing_burst()
            self.cut_selected_text()
            return

        if has_ctrl_or_cmd and event.key == pygame.K_a:
            self._select_all()
            return

        if has_ctrl_or_cmd and event.key == pygame.K_z:
            self._reset_typing_burst()
            if has_shift:
                self.redo()
            else:
                self.undo()
            return

        if has_ctrl and not has_cmd and event.key == pygame.K_y:
            self._reset_typing_burst()
            self.redo()
            return

        if event.key == pygame.K_ESCAPE:
            self._clear_selection()
            return

        if event.key == pygame.K_RETURN:
            if self.allow_multiline:
                if self.has_selection():
                    self.delete_selection()
                self.insert_text("\n")
            return

        if event.key == pygame.K_TAB:
            self.insert_text(" " * self._tab_spaces)
            return

        if event.key == pygame.K_BACKSPACE:
            if self.has_selection():
                self.delete_selection()
            elif has_cmd:
                self._delete_to_line_start()
            elif has_word_mod:
                self._delete_prev_word()
            else:
                self._delete_prev_char()
            return

        if event.key == pygame.K_DELETE:
            if self.has_selection():
                self.delete_selection()
            elif has_cmd:
                self._delete_to_line_end()
            elif has_word_mod:
                self._delete_next_word()
            else:
                self._delete_next_char()
            return

        if event.key == pygame.K_RIGHT:
            self._reset_typing_burst()
            if self.has_selection() and not has_shift and not has_word_mod and not has_cmd:
                _, end_pos, _, _ = self._selection_bounds()
                self._set_cursor_pos(end_pos, keep_selection=False)
            else:
                if has_cmd:
                    target = self._current_line_end_pos()
                    self._set_cursor_pos(target, keep_selection=has_shift)
                elif has_word_mod:
                    current = self._pos_to_offset((self.cursor_line, self.cursor_col))
                    target = self._offset_to_pos(self._next_word_offset(current))
                    self._set_cursor_pos(target, keep_selection=has_shift)
                else:
                    self._move_by_offset_delta(1, keep_selection=has_shift)
            self._preferred_col = None
            return

        if event.key == pygame.K_LEFT:
            self._reset_typing_burst()
            if self.has_selection() and not has_shift and not has_word_mod and not has_cmd:
                start_pos, _, _, _ = self._selection_bounds()
                self._set_cursor_pos(start_pos, keep_selection=False)
            else:
                if has_cmd:
                    target = self._current_line_start_pos()
                    self._set_cursor_pos(target, keep_selection=has_shift)
                elif has_word_mod:
                    current = self._pos_to_offset((self.cursor_line, self.cursor_col))
                    target = self._offset_to_pos(self._prev_word_offset(current))
                    self._set_cursor_pos(target, keep_selection=has_shift)
                else:
                    self._move_by_offset_delta(-1, keep_selection=has_shift)
            self._preferred_col = None
            return

        if event.key == pygame.K_UP:
            self._reset_typing_burst()
            if has_cmd:
                self._set_cursor_pos(self._doc_start_pos(), keep_selection=has_shift)
                self._preferred_col = None
            else:
                preferred = self.cursor_col if self._preferred_col is None else self._preferred_col
                target_line = max(0, self.cursor_line - 1)
                target_col = min(preferred, len(self.lines[target_line]))
                self._set_cursor_pos((target_line, target_col), keep_selection=has_shift)
                self._preferred_col = preferred
            return

        if event.key == pygame.K_DOWN:
            self._reset_typing_burst()
            if has_cmd:
                self._set_cursor_pos(self._doc_end_pos(), keep_selection=has_shift)
                self._preferred_col = None
            else:
                preferred = self.cursor_col if self._preferred_col is None else self._preferred_col
                target_line = min(len(self.lines) - 1, self.cursor_line + 1)
                target_col = min(preferred, len(self.lines[target_line]))
                self._set_cursor_pos((target_line, target_col), keep_selection=has_shift)
                self._preferred_col = preferred
            return

        if event.unicode and (event.unicode.isprintable() or (self.allow_multiline and event.unicode == "\n")):
            c = event.unicode
            if c == "\n" and not self.allow_multiline:
                return
            filtered = self._filter_text(c)
            if filtered:
                self._insert_typed_char(filtered)
            self._preferred_col = None

    def update(self):
        if not self.focused:
            self.caret_visible = False
            return

        if time.time() - self.last_blinked_at >= self._caret_interval:
            self.last_blinked_at = time.time()
            self.caret_visible = not self.caret_visible

    def _draw_selection(self, surface):
        bounds = self._selection_bounds()
        if bounds is None:
            return

        _, content_rect, _, _ = self._get_content_layout()

        start_pos, end_pos, _, _ = bounds
        start_line, start_col = start_pos
        end_line, end_col = end_pos

        for line_idx in range(start_line, end_line + 1):
            line_text = self.lines[line_idx]
            if line_idx == start_line:
                a = start_col
            else:
                a = 0

            if line_idx == end_line:
                b = end_col
            else:
                b = len(line_text)

            if b < a:
                a, b = b, a

            x1 = content_rect.x + self._get_text_width(line_text[:a]) - self._scroll_x
            x2 = content_rect.x + self._get_text_width(line_text[:b]) - self._scroll_x
            y = self._line_y(line_idx)
            h = self._get_line_height()

            if x2 == x1:
                continue

            pygame.draw.rect(surface, self.selection_color, (x1, y, x2 - x1, h))

    def _get_scrollbar_geometry(self):
        inner_rect, content_rect, show_h, show_v = self._get_content_layout()

        geometry = {
            "inner_rect": inner_rect,
            "content_rect": content_rect,
            "show_h": show_h,
            "show_v": show_v,
            "v_track": None,
            "v_thumb": None,
            "h_track": None,
            "h_thumb": None,
        }

        if not self.show_scrollbars:
            return geometry

        if show_v:
            v_track = pygame.Rect(content_rect.right, inner_rect.y, self._scrollbar_size, content_rect.height)
            total_h = max(1, len(self.lines) * self._get_line_height())
            thumb_h = max(self._scrollbar_min_thumb, int((content_rect.height / total_h) * v_track.height))
            thumb_h = min(v_track.height, thumb_h)

            max_scroll_y = self._max_scroll_y()
            if max_scroll_y <= 0:
                thumb_y = v_track.y
            else:
                thumb_y = v_track.y + int((self._scroll_y / max_scroll_y) * (v_track.height - thumb_h))

            geometry["v_track"] = v_track
            geometry["v_thumb"] = pygame.Rect(v_track.x, thumb_y, v_track.width, thumb_h)

        if show_h:
            h_track = pygame.Rect(inner_rect.x, content_rect.bottom, content_rect.width, self._scrollbar_size)
            max_line_width = max((self._get_text_width(line) for line in self.lines), default=1)
            total_w = max(1, max_line_width)
            thumb_w = max(self._scrollbar_min_thumb, int((content_rect.width / total_w) * h_track.width))
            thumb_w = min(h_track.width, thumb_w)

            max_scroll_x = self._max_scroll_x()
            if max_scroll_x <= 0:
                thumb_x = h_track.x
            else:
                thumb_x = h_track.x + int((self._scroll_x / max_scroll_x) * (h_track.width - thumb_w))

            geometry["h_track"] = h_track
            geometry["h_thumb"] = pygame.Rect(thumb_x, h_track.y, thumb_w, h_track.height)

        return geometry

    def _scrollbar_set_from_pointer(self, mode: str, pointer_pos, drag_offset: int):
        geometry = self._get_scrollbar_geometry()

        if mode == "v" and geometry["v_track"] is not None and geometry["v_thumb"] is not None:
            track = geometry["v_track"]
            thumb = geometry["v_thumb"]
            max_scroll = self._max_scroll_y()
            available = max(0, track.height - thumb.height)
            rel = pointer_pos[1] - track.y - drag_offset
            rel = max(0, min(rel, available))
            self._scroll_y = 0 if available <= 0 or max_scroll <= 0 else int((rel / available) * max_scroll)
            self._clamp_scroll()
            return

        if mode == "h" and geometry["h_track"] is not None and geometry["h_thumb"] is not None:
            track = geometry["h_track"]
            thumb = geometry["h_thumb"]
            max_scroll = self._max_scroll_x()
            available = max(0, track.width - thumb.width)
            rel = pointer_pos[0] - track.x - drag_offset
            rel = max(0, min(rel, available))
            self._scroll_x = 0 if available <= 0 or max_scroll <= 0 else int((rel / available) * max_scroll)
            self._clamp_scroll()
            return

    def _draw_scrollbars(self, surface, inner_rect: pygame.Rect, content_rect: pygame.Rect, show_h: bool, show_v: bool):
        if not self.show_scrollbars:
            return

        geometry = self._get_scrollbar_geometry()

        if geometry["show_v"] and geometry["v_track"] is not None and geometry["v_thumb"] is not None:
            pygame.draw.rect(surface, self._scrollbar_track_color, geometry["v_track"])
            pygame.draw.rect(surface, self._scrollbar_thumb_color, geometry["v_thumb"])

        if geometry["show_h"] and geometry["h_track"] is not None and geometry["h_thumb"] is not None:
            pygame.draw.rect(surface, self._scrollbar_track_color, geometry["h_track"])
            pygame.draw.rect(surface, self._scrollbar_thumb_color, geometry["h_thumb"])

        if geometry["show_h"] and geometry["show_v"]:
            corner = pygame.Rect(content_rect.right, content_rect.bottom, self._scrollbar_size, self._scrollbar_size)
            pygame.draw.rect(surface, self._scrollbar_track_color, corner)

    def draw(self, surface):
        super().draw(surface)
        self.update()

        inner_rect, content_rect, show_h, show_v = self._get_content_layout()

        prev_clip = surface.get_clip()
        effective_clip = content_rect.clip(prev_clip)
        surface.set_clip(effective_clip)

        if effective_clip.width > 0 and effective_clip.height > 0:
            self._draw_selection(surface)

            start_line = max(0, int(self._scroll_y // self._get_line_height()) - 1)
            visible_count = int(content_rect.height // self._get_line_height()) + 3
            end_line = min(len(self.lines), start_line + visible_count)

            for i in range(start_line, end_line):
                line = self.lines[i]
                render = self.font.render(line, True, self.text_color)
                draw_x = content_rect.x - self._scroll_x
                draw_y = self._line_y(i)
                surface.blit(render, (draw_x, draw_y))

            if self.focused and self.caret_visible:
                line_text = self.lines[self.cursor_line]
                caret_x = content_rect.x + self._get_text_width(line_text[:self.cursor_col]) - self._scroll_x
                caret_y = self._line_y(self.cursor_line)
                pygame.draw.rect(surface, self.caret_color, (caret_x, caret_y, 2, self._get_line_height()))

        surface.set_clip(prev_clip)
        self._draw_scrollbars(surface, inner_rect, content_rect, show_h, show_v)


