from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.graphics import Color

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1


# Set window to screen size
Window.maximize()

class MainWindow(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create the racing track
        with self.canvas:
            Color(1, 1, 1)
            Rectangle(pos=self.pos, size=self.size)

class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.title = "Racing Line"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        Builder.load_file("layout.kv")
        return MainWindow()


# Main loop
if __name__ == "__main__":
    app = MainApp()
    app.run()
    app.stop()
