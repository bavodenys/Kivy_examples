from kivymd.app import MDApp
from kivy.app import App
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.metrics import dp
import os

# Window size
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500

# Photo directory
directory = "/home/bavo/Pictures/"


class PhotoWindow(MDBoxLayout):
    photo_path = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (dp(WINDOW_WIDTH), dp(WINDOW_HEIGHT))
        self.index = 0
        self.photos = os.listdir(directory)
        self.number_photos = len(self.photos)
        self.photo_path = directory + self.photos[self.index]
        Window.bind(on_key_down=self.on_keyboard_down)

    def on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 79:  #  -> Next photo
            self.next_photo()
        if keycode == 80:  # <- Previous photo
            self.previous_photo()

    def next_photo(self):
        self.index += 1
        if self.index >= self.number_photos:
            self.index = 0
        self.photo_path = directory + self.photos[self.index]

    def previous_photo(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.number_photos-1
        self.photo_path = directory + self.photos[self.index]


class MainApp(MDApp):

    def build(self):
        self.title = "Photo viewer"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        Builder.load_file("layout.kv")
        return PhotoWindow()

if __name__ == "__main__":
    try:
        app = MainApp()
        app.run()
    except:
        pass
