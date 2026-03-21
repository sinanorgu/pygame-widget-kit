import pygame
from .Widget import*
from .Animation import AnimationManager

class UIManager:
    def __init__(self, root):
        self.root = root
        self.focused = None
        self.active = None
        self.modal = None  #  dropdown / modal
        self.animation_manager = AnimationManager()
        self._bind_manager(root)
    
    def _bind_manager(self, component):
        component.ui_manager = self
        for child in component.children:
            self._bind_manager(child)

    def hit_test(self, component:UIComponent, pos):
        if not component.visible or not component.enabled:
            return None

        # modal varsa SADECE onun içi
        children = component.children
        if self.modal:
            children = self.modal.children

        children = sorted(children, key=lambda c: c.z_index)
        children.reverse()

        for child in children:
            if isinstance(child,Widget):
                hit = self.hit_test(child, pos)
                if hit:
                    return hit
            else:
                if child.is_in_rect(pos) and child.visible:
                    return child

        if component.is_in_rect(pos):
            return component

        return None
    

    def handle_event(self, event: pygame.event.Event):

        # 🔹 Event'in başlayacağı root
        root = self.modal if self.modal else self.root

        # -------------------------
        # MOUSE BUTTON DOWN
        # -------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            target = self.hit_test(root, event.pos)
            button = getattr(event, "button", None)

            if button == 1:
                # Sol tik: mevcut click/focus davranisi
                # 👉 Modal açık ama DIŞINA tıklandıysa
                if self.modal and not target:
                    # modal kapatılır
                    if hasattr(self.modal, "close"):
                        self.modal.close()
                    self.modal = None
                    return

                if target:
                    self.active = target
                    target.active = True
                    target.handle_event(event)

                    # focus yönetimi
                    if self.focused and self.focused != target:
                        self.focused.on_blur()

                    target.on_focus()
                    self.focused = target

            elif button == 2:
                # Orta tik (wheel click): ileride ozel davranis eklenebilir
                # Modal açıkken dışına tıklandıysa modal kapatılır
                if self.modal and not target:
                    if hasattr(self.modal, "close"):
                        self.modal.close()
                    self.modal = None
                pass

            elif button == 3:
                # Sag tik: ileride context-menu vb. davranis eklenebilir
                # Modal açıkken dışına tıklandıysa modal kapatılır
                if self.modal and not target:
                    if hasattr(self.modal, "close"):
                        self.modal.close()
                    self.modal = None
                    return

                # Sağ tık event'i hedef component'e iletilir (örn: context-menu açma)
                if target:
                    target.handle_event(event)

                    # Sag tikla da focus alinabilmesi icin
                    if self.focused and self.focused != target:
                        self.focused.on_blur()
                    target.on_focus()
                    self.focused = target

            else:
                # Diger butonlar (ornegin wheel up/down): simdilik islenmiyor
                # Modal açıkken dışına tıklandıysa modal kapatılır
                if self.modal and not target:
                    if hasattr(self.modal, "close"):
                        self.modal.close()
                    self.modal = None
                pass

            return

        # -------------------------
        # MOUSE BUTTON UP
        # -------------------------
        elif event.type == pygame.MOUSEBUTTONUP:
            button = getattr(event, "button", None)

            if button == 1:
                # Sol tik birakma: click tamamlanmasi
                if self.active:
                    self.active.active = False

                    # click sayılır mı?
                    if self.active.is_in_rect(event.pos):
                        self.active.on_click(event)

                    self.active = None

            elif button == 2:
                # Orta tik birakma: ileride ozel davranis eklenebilir
                pass

            elif button == 3:
                # Sag tik birakma: ileride context-menu acilisi vb. eklenebilir
                pass

            else:
                # Diger mouse butonlari: simdilik islenmiyor
                pass

            return

        # -------------------------
        # MOUSE MOVE (HOVER)
        # -------------------------
        elif event.type == pygame.MOUSEMOTION:

            target = self.hit_test(root, event.pos)

            # hover değiştiyse güncelle
            def clear_hover(widget):
                widget.hovered = False
                for c in widget.children:
                    clear_hover(c)

            clear_hover(self.root)

            if target:
                target.hovered = True

            if self.active and self.active.visible and self.active.enabled:
                self.active.handle_event(event)

        # -------------------------
        # KEYBOARD
        # -------------------------
        elif event.type == pygame.KEYDOWN:
            if self.focused:
                self.focused.handle_event(event)

    def _handle_hover(self, pos):
        target = self.hit_test(self.modal or self.root, pos)

        def clear_hover(widget):
            widget.hovered = False
            for c in widget.children:
                clear_hover(c)

        clear_hover(self.root)

        if target:
            target.hovered = True

    def update(self, dt: float):
        self.animation_manager.update(dt)
