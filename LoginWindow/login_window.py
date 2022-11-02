from kivymd.app import MDApp
from kivy.app import App
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton
from kivy.properties import StringProperty, BooleanProperty
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.clock import Clock


class FocusButton(MDRectangleFlatButton, FocusBehavior):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == 'enter':
            return True
        if keycode[1] == 'tab':
            next_w = self.get_focus_next()
            next_w.focus = True
            return True
        return False

class LoginWindow(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (dp(500), dp(200))
        Window.bind(on_key_down=self.on_keyboard_down)

    def ok_pressed(self):
        MDApp = App.get_running_app()
        MDApp.username = self.ids['username'].text
        MDApp.password = self.ids['password'].text
        MDApp.confirm = True
        MDApp.stop()

    def cancel_pressed(self):
        MDApp = App.get_running_app()
        MDApp.confirm = False
        self.parent.close()

    def on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40:  # ENTER
            self.ok_pressed()
        if keycode == 43:  # TAB
            pass


class MainApp(MDApp):
    username = StringProperty(None)
    password = StringProperty(None)
    confirm = BooleanProperty(False)

    def build(self):
        self.title = "Login"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        Builder.load_file("layout.kv")
        return LoginWindow()

    def on_start(self):
        # create a delay to allow the animation before setting focus
        Clock.schedule_once(self.focus_username, 1)

    def focus_username(self, _):
        self.root.ids.username.focus = True

# Example how to use Login Window
if __name__ == "__main__":
    try:
        app = MainApp()
        app.run()
        if app.confirm:
            print(f'Username: {app.username}')
            print(f'Password: {app.password}')
    except:
        pass
