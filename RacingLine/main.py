from kivymd.app import MDApp
from kivy.core.window import Window


# Set window to screen size
Window.maximize()


class MainApp(MDApp):
    pass


# Main loop
if __name__ == "__main__":
    app = MainApp()
    app.run()
    app.stop()

