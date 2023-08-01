from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
from copy import deepcopy
from functions import *
import random

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1

# Calibrations
DEBUG_MODE = True
OBSTACLE_WIDTH = 100
OBSTACLE_GAP_INIT = 500
START_POS_X = 300
START_POS_Y = 1000
FLAPPY_RADIUS = 50
FLAPPY_MASS = 0.5
UP_FORCE = 20 # N
SCALING = 5
LEVEL_0 = 10 # s
OBSTACLE_START_SPEED = 6
OBSTACLE_INC_SPEED = 2

# Constants
GRAV_ACC = 9.81

# Window size
WINDOW_WIDTH = 2500
WINDOW_HEIGHT = 1500


class Obstacle():

    def __init__(self, **kwargs):
        self.posx = WINDOW_WIDTH - OBSTACLE_WIDTH
        self.posy = 0
        random_gap_posy = random.randint(100, WINDOW_HEIGHT-100)
        self.gap = kwargs.get('gap', OBSTACLE_GAP_INIT)
        self.gap_posy = kwargs.get('gap_posy', random_gap_posy)
        self.width = OBSTACLE_WIDTH
        self.obstacle = {'up': Rectangle(pos=[self.posx,self.gap_posy+self.gap], size=(self.width, WINDOW_HEIGHT-(self.gap_posy+self.gap))),
                         'down':Rectangle(pos=[self.posx,self.posy], size=(self.width, self.gap_posy))}

    def update_parameters(self, dt):
        self.posx = self.posx - (OBSTACLE_START_SPEED*(dt*10) + 0*OBSTACLE_INC_SPEED)

    def update_obstacle(self):
        self.obstacle = {'up': Rectangle(pos=[self.posx,self.gap_posy+self.gap], size=(self.width, WINDOW_HEIGHT-(self.gap_posy+self.gap))),
                         'down':Rectangle(pos=[self.posx,self.posy], size=(self.width, self.gap_posy))}



class Flappy():

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
        self.pos_y = self.pos_y + self.spd_y*dt*SCALING
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
        Clock.schedule_interval(self.update, 1 / 20)
        self.obstacles = []
        self.last_update = 0
        self.time_count = 0
        with self.canvas:
            Color(1, 1, 0)  #Yellow
            Rectangle(pos=[0,0], size=(WINDOW_WIDTH, WINDOW_HEIGHT))
            self.flappy = Flappy()
            Color(0,0,1)
            self.obstacles.append(Obstacle(gap=400))

    def update(self, dt):
        self.flappy.calculate_inputs(self.key_up_active)
        self.flappy.update_acceleration()
        self.flappy.update_speed(dt)
        self.flappy.update_position(dt)
        for obstacle in self.obstacles:
            obstacle.update_parameters(dt)
        self.time_count +=dt
        if self.time_count - self.last_update >= LEVEL_0:
            self.last_update = deepcopy(self.time_count)
            self.obstacles.append(Obstacle(gap=400))

        with self.canvas:
            Color(1, 1, 0)
            Rectangle(pos=[0, 0], size=(WINDOW_WIDTH, WINDOW_HEIGHT))
            self.canvas.remove(self.flappy.ellipse)
            Color(0, 0, 0)
            self.flappy.update_flappy()
            Color(0, 0, 1)
            remove_obstacle = False
            for index, obstacle in enumerate(self.obstacles):
                # Determine if the obstacle leaves the window
                if obstacle.posx < (0 - obstacle.width):
                    remove_obstacle = True
                obstacle.update_obstacle()
            if remove_obstacle:
                del self.obstacles[0]


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
