from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout


DEBUG = False

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1


# Calibrations window
if DEBUG:
    WINDOW_WIDTH = dp(500)
    WINDOW_HEIGHT = dp(800)

class WindowManager(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = NoTransition()
        if DEBUG:
            Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)

class MainWindow(Screen):
    pass


class Bike(ButtonBehavior, MDBoxLayout):
    pass


class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def build(self):
        self.title = "BikeChainSwapApp"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        kv = Builder.load_file("layout.kv")
        return kv

    # About
    def call_about(self):
        pass


# MAIN
if __name__ == "__main__":
    try:
        app = MainApp()
        app.run()
    except:
        pass
