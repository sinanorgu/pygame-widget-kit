import pygame
from .Text import *
from .UIComponent import *
from functools import partial
import tkinter as tk
from tkinter import filedialog


import multiprocessing


def file_choser_process(queue):
    try:
        root = tk.Tk()
        root.withdraw() 
        
        root.attributes('-topmost', True)
        
        root.lift()
        root.focus_force()
        
        dosya_yolu = filedialog.askopenfilename(
            title="Chose File",
            filetypes=[("Tüm Dosyalar", "*.*")]
        )
        
        queue.put(dosya_yolu)
        
        root.destroy()
    except Exception as e:
        queue.put(None) 



class Button(UIComponent):
    def __init__(self, text_str = "Button",
                pos = (0,0),
                size = (200,40),
                style=None,
                z_index=0, 
                color=(175,175,175), 
                border_color = (100,100,100), 
                hover_color=(150,150,150),
                text_color = (0,0,0),
                padding = (20,10)
                ):
        self.text_str = text_str
        self.size = size
        self.text_color =text_color
        self.padding = padding
        self.text = Text(self.text_str,pos = self.padding,text_color=text_color,bg_color=None)
        
        self.click_function = None

        
        rect = (pos[0],pos[1],self.size[0],self.size[1])
        
        super().__init__(rect, style, z_index, color, border_color, hover_color)
        self.add_child(self.text)
    
    def click_bind(self, func, *args):
        self.click_function = partial(func, *args)


    def draw(self, surface):
        if self.visible == False:
            return
        
        color = self.color
        if self.hovered:
            color=self.hover_color

        if color is not None:
            pygame.draw.rect(surface,color,self.absolute_rect,0)
        if self.border_color:
            pygame.draw.rect(surface,self.border_color,self.absolute_rect,2)


        self.text.draw(surface)


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.active = False

    def on_click(self, event):
        if self.click_function is not None:
            self.click_function()
        else:
            print("Button clicked")
    



class ChooseFileButton(Button):
    def __init__(self, text_str="Button", pos=(0, 0), size=(200, 40), style=None, z_index=0, color=(175, 175, 175), border_color=(100, 100, 100), hover_color=(150, 150, 150), text_color=(0, 0, 0), padding=(20, 10)):
        super().__init__(text_str, pos, size, style, z_index, color, border_color, hover_color, text_color, padding)
    
        self.chosen_file_path = None
    
    def on_click(self, event):
        print("Dosya seçici ayrı işlemde başlatılıyor...")
                        
        q = multiprocessing.Queue()
        
        p = multiprocessing.Process(target=file_choser_process, args=(q,))
        
        p.start()
        p.join()
        if not q.empty():
            sonuc = q.get()
            if sonuc: 
                secilen_dosya = sonuc
                print(f"Gelen dosya: {secilen_dosya}")
                self.chosen_file_path = secilen_dosya
                self.text.set_text(secilen_dosya)
                if self.click_function is not None:
                    self.click_function()
                else:
                    print("islem iptal")
        else:
            print("İşlem iptal edildi veya hata oluştu.")


        
        
    