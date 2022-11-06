from kivymd.app import MDApp
from kivy.app import App
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import NumericProperty, BooleanProperty
from kivy.graphics.vertex_instructions import Ellipse
from kivy.graphics import Color

# Calibrations
WINDOW_WIDTH = dp(500)
WINDOW_HEIGHT = dp(800)
PIN_POSITIONS = 4
MAX_ATTEMPTS = 3


class PinWindow(MDBoxLayout):
    PIN_radius_out = NumericProperty(50)
    PIN_radius_in = NumericProperty(40)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.pin_pos = 1
        self.pin_OK = True
        self.pin_attempts = 0
        MDApp = App.get_running_app()
        self.pin_code = MDApp.pin_code

    def ok_pressed(self):
        self.validate_pin()

    def c_pressed(self):
        self.reset_pin_attempt()

    def number_pressed(self, number):
        self.fill_pin_pos()
        if self.pin_code[self.pin_pos-1] == str(number):
            pass
        else:
            self.pin_OK = False
        if self.pin_pos >= PIN_POSITIONS:
            pass
        else:
            self.pin_pos+=1

    def fill_pin_pos(self):
        with self.canvas:
            color = Color(1, 1, 1, 1)
            Ellipse(pos=[self.ids['pin'].pos[0] + ((self.pin_pos*2)-1)*self.ids['pin'].size[0]/8 - \
                         self.PIN_radius_in/2, self.ids['pin'].pos[1] + self.ids['pin'].size[1]/2 - \
                         self.PIN_radius_in/2], size=[self.PIN_radius_in, self.PIN_radius_in])

    def reset_pin_attempt(self):
        with self.canvas:
            color = Color(0, 0, 0, 1)
            for i in range(PIN_POSITIONS):
                Ellipse(pos=[self.ids['pin'].pos[0] + (((i+1) * 2) - 1) * self.ids['pin'].size[0] / 8 - \
                             self.PIN_radius_in / 2,self.ids['pin'].pos[1] + self.ids['pin'].size[1] / 2 - \
                             self.PIN_radius_in / 2],size=[self.PIN_radius_in, self.PIN_radius_in])
        self.pin_pos = 1
        self.pin_OK = True

    def validate_pin(self):
        if self.pin_pos < PIN_POSITIONS:
            pass
        else:
            if self.pin_pos == PIN_POSITIONS and self.pin_OK:
                MDApp = App.get_running_app()
                MDApp.pin_ok = True
                MDApp.stop()
            else:
                self.pin_attempts+=1
                if self.pin_attempts >= MAX_ATTEMPTS:
                    MDApp = App.get_running_app()
                    MDApp.pin_ok = False
                    MDApp.stop()
                else:
                    self.reset_pin_attempt()

class MainApp(MDApp):
    pin_ok = BooleanProperty(False)

    def __init__(self, pin_code, **kwargs):
        super().__init__(**kwargs)
        self.pin_code = pin_code

    def build(self):
        self.title = "Enter PIN"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        Builder.load_file("layout.kv")
        return PinWindow()

# Example how to use the PIN window
if __name__ == "__main__":
    try:
        pin_code = '0356'
        app = MainApp(pin_code)
        app.run()
        if app.pin_ok:
            print('PIN is OK')
        else:
            print('PIN is NOK')
    except:
        pass
