from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
from functions import *

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1

# Calibrations
DEBUG_MODE = True
OBSTACLE_WIDTH = 500
OBSTACLE_WIDTH_DEC = 50
OBSTACLE_DIST_START = 500
OBSTACLE_DIST_DEC = 50
START_POS_X = 300
START_POS_Y = 1000
FLAPPY_RADIUS = 50
FLAPPY_MASS = 0.5
UP_FORCE = 20 # N

# Constants
GRAV_ACC = 9.81

# Window size
WINDOW_WIDTH = 2500
WINDOW_HEIGHT = 1500

class flappy():

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.flappy_mass = FLAPPY_MASS
        self.pos_x = START_POS_X
        self.pos_y = START_POS_Y
        self.acc_y = 0
        self.spd_y = 0
        self.ellipse = Ellipse(pos=[self.pos_x, self.pos_y],size=[FLAPPY_RADIUS, FLAPPY_RADIUS])

    def calculate_inputs(self, up):
        self.up_force = UP_FORCE if up else 0

    def update_acceleration(self):
        self.acc_y = (self.up_force - self.flappy_mass * GRAV_ACC) / (self.flappy_mass)

    def update_speed(self, dt):
        self.spd_y = self.spd_y + self.acc_y*dt

    def update_position(self, dt):
        self.pos_y = self.pos_y + self.spd_y*dt
        if self.pos_y<0:
            self.pos_y = 0

    def update_flappy(self):
        self.ellipse = Ellipse(pos=[self.pos_x, self.pos_y], size=[FLAPPY_RADIUS, FLAPPY_RADIUS])

    def update_score(self):
        pass



class MainWindow(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size =(dp(WINDOW_WIDTH), dp(WINDOW_HEIGHT))
        Window.bind(on_key_down=self.on_keyboard_down)
        Window.bind(on_key_up=self.on_keyboard_up)
        self.key_up_active = False
        Clock.schedule_interval(self.update, 1 / 60)
        with self.canvas:
            Color(1, 1, 0)  #Yellow
            Rectangle(pos=[0,0], size=(WINDOW_WIDTH, WINDOW_HEIGHT))
            self.flappy = flappy()

    def update(self, dt):
        self.flappy.calculate_inputs(self.key_up_active)
        self.flappy.update_acceleration()
        self.flappy.update_speed(dt)
        self.flappy.update_position(dt)
        with self.canvas:
            Color(1, 1, 0)
            Rectangle(pos=[0, 0], size=(WINDOW_WIDTH, WINDOW_HEIGHT))
            self.canvas.remove(self.flappy.ellipse)
            Color(0, 0, 0)
            self.flappy.update_flappy()


    def on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 82:  # Key UP
            self.key_up_active = True
        if keycode == 22:  # s -> start
            self.run_simulation()

    def on_keyboard_up(self, instance, keyboard, keycode):
        if keycode == 82:  # Key UP
            self.key_up_active = False


class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.title = "Flappy bird"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        Builder.load_file("layout.kv")
        return MainWindow()


# Main loop
if __name__ == "__main__":
    app = MainApp()
    app.run()
    app.stop()
