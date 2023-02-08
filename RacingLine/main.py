from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import Ellipse
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle
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
        self.vehicle_pos_x = START_POS_X
        self.vehicle_pos_y = START_POS_Y
        self.orientation_angle = 90
        self.vehicle_speed = 0
        self.vehicle_acceleration = 0
        self.accelerating_force = 0
        self.braking_force = 0
        self.steering_angle = 0
        self.circuit = []
        # Create the racing track
        with self.canvas:
            Color(1, 0, 1)
            self.vehicle = Ellipse(pos=[START_POS_X, START_POS_Y], size=(ELLIPSE_DIAMETER, ELLIPSE_DIAMETER))
            Color(1, 1, 1)
            self.circuit.append(Rectangle(pos=(2800,420), size=(TRACK_WIDTH, 1280)))
            self.circuit.append(Ellipse(pos=[2800-(400-TRACK_WIDTH),1700-400/2], size=(400, 400), angle_start=0, angle_end=90))
            self.circuit.append(Rectangle(pos=(2400, 1800), size=(300,TRACK_WIDTH)))
            self.circuit.append(Ellipse(pos=(2400-600/2, 1800-(600-TRACK_WIDTH)), size=(600, 600), angle_start=315, angle_end=360))
            self.circuit.append(Ellipse(pos=[1747, 1653], size=(600, 600), angle_start=135, angle_end=180))
            self.circuit.append(Rectangle(pos=(1547, 1653), size=(500, TRACK_WIDTH)))
            self.circuit.append(Ellipse(pos=[1297, 1253], size=(500, 500), angle_start=180, angle_end=360))
            self.circuit.append(Rectangle(pos=(1547, 1253), size=(300, TRACK_WIDTH)))
            self.circuit.append(Ellipse(pos=(1722, 1103), size=(250, 250), angle_start=0, angle_end=90))
            self.circuit.append(Rectangle(pos=(1873, 1128), size=(TRACK_WIDTH, 100)))
            self.circuit.append(Ellipse(pos=(1723, 1003), size=(250, 250), angle_start=90, angle_end=180))
            self.circuit.append(Rectangle(pos=(1248, 1003), size=(600, TRACK_WIDTH)))
            self.circuit.append(Ellipse(pos=(848, 1003), size=(800, 800), angle_start=180, angle_end=270))
            self.circuit.append(Rectangle(pos=(848, 1403), size=(TRACK_WIDTH, 300)))
            self.circuit.append(Ellipse(pos=(599, 1527), size=(350, 350), angle_start=0, angle_end=90))
            self.circuit.append(Rectangle(pos=(674, 1777), size=(100, TRACK_WIDTH)))
            self.circuit.append(Ellipse(pos=(549, 1627), size=(250, 250), angle_start=270, angle_end=360))
            self.circuit.append(Rectangle(pos=(549, 1712), size=(TRACK_WIDTH, 40)))
            self.circuit.append(Ellipse(pos=(249, 1512), size=(400, 400), angle_start=90, angle_end=160))
            self.circuit.append(Ellipse(pos=(286, 1036), size=(600, 600), angle_start=270, angle_end=340))
            self.circuit.append(Rectangle(pos=(286, 686), size=(TRACK_WIDTH, 650)))
            self.circuit.append(Ellipse(pos=(286, 336), size=(700, 700), angle_start=235, angle_end=270))
            self.circuit.append(Ellipse(pos=(-297, -87), size=(800, 800), angle_start=90, angle_end=55))
            self.circuit.append(Ellipse(pos=(403, 113), size=(400, 400), angle_start=180, angle_end=270))
            self.circuit.append(Rectangle(pos=(603, 113), size=(497, TRACK_WIDTH)))
            self.circuit.append(Ellipse(pos=(900, 113), size=(400, 400), angle_start=-20, angle_end=180))
            self.circuit.append(Ellipse(pos=(865, 398), size=(300, 300), angle_start=160, angle_end=270))
            self.circuit.append(Rectangle(pos=(865, 548), size=(TRACK_WIDTH, 150)))
            self.circuit.append(Ellipse(pos=(865, 548), size=(300, 300), angle_start=270, angle_end=360))
            self.circuit.append(Rectangle(pos=(1015, 748), size=(1000, TRACK_WIDTH)))
            self.circuit.append(Ellipse(pos=(1715, 248), size=(600, 600), angle_start=0, angle_end=110))
            self.circuit.append(Ellipse(pos=(2179, -57), size=(800, 800), angle_start=270, angle_end=290))
            self.circuit.append(Rectangle(pos=(2179, 293), size=(TRACK_WIDTH, 50)))
            self.circuit.append(Ellipse(pos=(2179, 93), size=(400, 400), angle_start=180, angle_end=270))
            self.circuit.append(Rectangle(pos=(2379, 93), size=(171, TRACK_WIDTH)))
            self.circuit.append(Ellipse(pos=(2200, 93), size=(700, 700), angle_start=90, angle_end=180))
            Color(0, 0, 0)
            self.circuit.append(Ellipse(pos=[2800-((400-TRACK_WIDTH*2)/2)-TRACK_WIDTH,1700-(400-TRACK_WIDTH*2)/2], size=(400-TRACK_WIDTH*2, 400-TRACK_WIDTH*2), angle_start=0, angle_end=90))
            self.circuit.append(Ellipse(pos=(2400 - (600 / 2 - TRACK_WIDTH), 1400),size=(600 - TRACK_WIDTH * 2, 600 - TRACK_WIDTH * 2), angle_start=315,angle_end=360))
            self.circuit.append(Ellipse(pos=[1847, 1753], size=(600 - TRACK_WIDTH * 2, 600 - TRACK_WIDTH * 2), angle_start=135,angle_end=180))
            self.circuit.append(Ellipse(pos=[1397, 1352], size=(300, 300), angle_start=180, angle_end=360))
            self.circuit.append(Ellipse(pos=(1822, 1203), size=(50, 50), angle_start=0, angle_end=90))
            self.circuit.append(Ellipse(pos=(1822, 1103), size=(50, 50), angle_start=90, angle_end=180))
            self.circuit.append(Ellipse(pos=(948, 1103), size=(600, 600), angle_start=180, angle_end=270))
            self.circuit.append(Ellipse(pos=(699, 1627), size=(150, 150), angle_start=0, angle_end=90))
            self.circuit.append(Ellipse(pos=(649, 1727), size=(50, 50), angle_start=270, angle_end=360))
            self.circuit.append(Ellipse(pos=(349, 1612), size=(200, 200), angle_start=90, angle_end=160))
            self.circuit.append(Ellipse(pos=(386, 1136), size=(400, 400), angle_start=270, angle_end=340))
            self.circuit.append(Ellipse(pos=(386, 436), size=(500, 500), angle_start=235, angle_end=270))
            self.circuit.append(Ellipse(pos=(-197, 13), size=(600, 600), angle_start=90, angle_end=55))
            self.circuit.append(Ellipse(pos=(503, 213), size=(200, 200), angle_start=180, angle_end=270))
            self.circuit.append(Ellipse(pos=(1000, 213), size=(200, 200), angle_start=-20, angle_end=180))
            self.circuit.append(Ellipse(pos=(965, 498), size=(100, 100), angle_start=160, angle_end=270))
            self.circuit.append(Ellipse(pos=(965, 648), size=(100, 100), angle_start=270, angle_end=360))
            self.circuit.append(Ellipse(pos=(1815, 348), size=(400, 400), angle_start=0, angle_end=110))
            self.circuit.append(Ellipse(pos=(2279, 43), size=(600, 600), angle_start=270, angle_end=290))
            self.circuit.append(Ellipse(pos=(2279, 193), size=(200, 200), angle_start=180, angle_end=270))
            self.circuit.append(Ellipse(pos=(2300, 193), size=(500, 500), angle_start=90, angle_end=180))
            Color(0, 0, 1)





















































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
            Color(1, 0, 1)
            self.vehicle = Ellipse(pos=[self.vehicle_pos_x, self.vehicle_pos_y], size=(ELLIPSE_DIAMETER, ELLIPSE_DIAMETER))


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
