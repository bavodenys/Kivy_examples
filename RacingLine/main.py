from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import Ellipse
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.graphics import Color
from kivy.clock import Clock
from functions import *
from calibrations import *


# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1

# Set window to screen size
Window.maximize()

class MainWindow(MDBoxLayout):
    dashboard_speed = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.on_keyboard_down)
        Window.bind(on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.update, 1 / 60)
        self.key_up_active = False
        self.key_down_active = False
        self.key_right_active = False
        self.key_left_active = False
        self.vehicle_pos_x = MAX_POS_X/2
        self.vehicle_pos_y = MAX_POS_Y/2
        self.orientation_angle = 90
        self.vehicle_speed = 0
        self.vehicle_acceleration = 0
        self.accelerating_force = 0
        self.braking_force = 0
        self.steering_angle = 0
        # Create the racing track
        with self.canvas:
            Color(1, 1, 1)
            self.vehicle = Ellipse(pos=[START_POS_X, START_POS_Y], size=(ELLIPSE_RADIUS, ELLIPSE_RADIUS))


    def update(self, dt):
        # Remove the vehicle from the canvas
        self.canvas.remove(self.vehicle)

        self.accelerating_force = ACCELERATING_FORCE if self.key_up_active else 0
        self.braking_force = BRAKING_FORCE if self.key_down_active else 0
        if self.key_left_active and self.key_right_active:
            pass
        else:
            if self.key_left_active:
                if self.steering_angle <= -MAX_STEERING_ANGLE:
                    pass
                else:
                    self.steering_angle -= ANGLE_INCREASE
            if self.key_right_active:
                if self.steering_angle >= MAX_STEERING_ANGLE:
                    pass
                else:
                    self.steering_angle += ANGLE_INCREASE

        # Calculate vehicle acceleration
        self.vehicle_acceleration = calculate_acceleration(self.accelerating_force, self.braking_force, self.vehicle_speed)
        # Calculate vehicle speed
        self.vehicle_speed = calculate_speed(self.vehicle_speed, self.vehicle_acceleration, dt)
        # calculate vehicle position
        self.vehicle_pos_x, self.vehicle_pos_y, self.orientation_angle = calculate_position(self.vehicle_pos_x,
                                                                                            self.vehicle_pos_y,
                                                                                            self.vehicle_speed,
                                                                                            self.steering_angle,
                                                                                            self.orientation_angle,
                                                                                            dt)


        with self.canvas:
            self.vehicle = Ellipse(pos=[self.vehicle_pos_x, self.vehicle_pos_y], size=(ELLIPSE_RADIUS, ELLIPSE_RADIUS))

        # Dashboard variables
        self.dashboard_speed = str(int(self.vehicle_speed * 3.6))

    def on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 82:  # Key UP
            self.key_up_active = True
        if keycode == 81:  # Key DOWN
            self.key_down_active = True
        if keycode == 80:  # Key LEFT
            self.key_left_active = True
        if keycode == 79:  # Key RIGHT
            self.key_right_active = True

    def on_keyboard_up(self, instance, keyboard, keycode):
        if keycode == 82:  # Key UP
            self.key_up_active = False
        if keycode == 81:  # Key DOWN
            self.key_down_active = False
        if keycode == 80:  # Key LEFT
            self.key_left_active = False
        if keycode == 79:  # Key RIGHT
            self.key_right_active = False

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
