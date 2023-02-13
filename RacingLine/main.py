from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import Ellipse
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.core.image import Image
from kivy.metrics import dp
from functions import *
from calibrations import *
from copy import deepcopy
import random

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1

# Mode
AUTO_MODE = True

# Window dimensions
WINDOW_WIDTH = 1848
WINDOW_HEIGHT = 968

# Set window to screen size
Window.maximize()
#Window.borderless = True


class vehicle():

    def __init__(self, throttle, brake, left, right, **kwargs):
        super().__init__(**kwargs)
        self.throttle = throttle
        self.brake = brake
        self.left = left
        self.right = right
        self.veh_pos_x = START_POS_X
        self.veh_pos_y = START_POS_Y
        self.dur = 0
        self.dist = 0
        self.acc_frc = 0
        self.brk_frc = 0
        self.veh_spd = 0
        self.veh_acc = 0
        self.or_ang = START_ORIENTATION_ANGLE
        self.st_ang = 0
        self.on_track = True
        self.it_out = 0
        self.ranking = 0
        self.score = 0
        self.ellipse = Ellipse(pos=[START_POS_X, START_POS_Y], size=(ELLIPSE_DIAMETER,ELLIPSE_DIAMETER))

    def calculate_inputs(self, iteration):
        self.acc_frc = ACCELERATING_FORCE if self.throttle[iteration] else 0
        self.brk_frc = BRAKING_FORCE if self.brake[iteration] else 0
        if self.left[iteration] and self.right[iteration]:
            pass
        else:
            if self.left[iteration]:
                if self.st_ang <= -MAX_STEERING_ANGLE:
                    pass
                else:
                    self.st_ang -= ANGLE_INCREASE
            if self.right[iteration]:
                if self.st_ang >= MAX_STEERING_ANGLE:
                    pass
                else:
                    self.st_ang += ANGLE_INCREASE

    def update_acceleration(self):
        self.veh_acc = calculate_acceleration(self.acc_frc, self.brk_frc, self.veh_spd)

    def update_speed(self, dt):
        self.veh_spd = calculate_speed(self.veh_spd, self.veh_acc, dt)

    def update_position_orientation(self, dt):
        self.veh_pos_x, self.veh_pos_y, self.or_ang, dist = calculate_position(self.veh_pos_x,
                                                                           self.veh_pos_y,
                                                                           self.veh_spd,
                                                                           self.st_ang,
                                                                           self.or_ang,
                                                                           dt)
        self.dist += dist

    def update_veh_stats(self, dt):
        self.dur += dt

    def update_score(self):
        self.score = self.dist/self.dur


class MainWindow(MDBoxLayout):
    dashboard_speed = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.on_keyboard_down)
        Window.bind(on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.update, 1 / 60)
        # Manual control
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

        self.first_run_simulation = True
        self.vehicles_crashed = 0
        self.top_10 = {}
        self.circuit = []
        self.printscreen_available = False
        self.simulation_started = False
        # Create the racing track
        with self.canvas:
            if 1:
                if not(AUTO_MODE):
                    Color(1, 0, 1)
                    self.vehicle = Ellipse(pos=[START_POS_X, START_POS_Y], size=(ELLIPSE_DIAMETER, ELLIPSE_DIAMETER))
                Color(1, 1, 0)  # White
                Rectangle(pos=[0,0], size=(MAX_POS_X, MAX_POS_Y))
                Color(0,0,0)
                for seg in TRACK:
                    self.circuit.append(Rectangle(pos=[TRACK[seg]['TRACK_POS_X'], TRACK[seg]['TRACK_POS_Y']],
                                                  size=(TRACK[seg]['TRACK_SIZE_X'], TRACK[seg]['TRACK_SIZE_Y'])))



    def update(self, dt):

        if not(AUTO_MODE):
            # Remove the vehicle from the canvas
            self.canvas.remove(self.vehicle)
            # Get the vehicle inputs
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


            # Draw vehicle back on the canvas
            with self.canvas:
                Color(1, 0, 1)
                self.vehicle = Ellipse(pos=[self.vehicle_pos_x, self.vehicle_pos_y], size=(ELLIPSE_DIAMETER, ELLIPSE_DIAMETER))

            # Dashboard variables
            self.dashboard_speed = str(int(self.vehicle_speed * 3.6))






        # Auto mode
        else:
            if self.simulation_started and int(self.iteration/10) < ITERATIONS:
                for i in range(VEHICLE_POPULATION):
                    if self.vehicles[i].on_track:
                        self.canvas.remove(self.vehicles[i].ellipse)
                        # Calculate the inputs
                        self.vehicles[i].calculate_inputs(int(self.iteration/10))
                        # Calculate vehicle acceleration
                        self.vehicles[i].update_acceleration()
                        # Calculate vehicle speed
                        self.vehicles[i].update_speed(dt)
                        # Calculate vehicle position
                        self.vehicles[i].update_position_orientation(dt)
                        # Update vehicle stats
                        self.vehicles[i].update_veh_stats(dt)

                        veh_on_canvas = determine_in_rectangle(self.vehicles[i].veh_pos_x, self.vehicles[i].veh_pos_y, 0, 0, MAX_POS_X, MAX_POS_Y)
                        if veh_on_canvas:
                            veh_on_track = determine_on_track(self.vehicles[i].veh_pos_x, self.vehicles[i].veh_pos_y,TRACK)
                        else:
                            pass
                        if not(veh_on_canvas) or not(veh_on_track):
                            self.vehicles[i].on_track = False
                            self.vehicles[i].it_out = int(self.iteration)
                            self.vehicles_crashed += 1
                            self.vehicles[i].update_score()
                            if len(self.top_10) < 10:
                                self.top_10[self.vehicles[i].score] = i
                            else:
                                self.top_10.pop(min(self.top_10))
                                self.top_10[self.vehicles[i].score] = i
                            print(f'GAME OVER! Score: {self.vehicles[i].score} {i}')

                        # Draw vehicle back on the canvas
                        with self.canvas:
                            Color(0, 1, 0)
                            self.vehicles[i].ellipse = Ellipse(pos=[self.vehicles[i].veh_pos_x, self.vehicles[i].veh_pos_y],size=(ELLIPSE_DIAMETER, ELLIPSE_DIAMETER))


                if self.vehicles_crashed == VEHICLE_POPULATION:
                    self.simulation_started = False
                    if self.first_run_simulation:
                        self.first_run_simulation = False
                    print(sorted(self.top_10))

                self.iteration +=1



    def on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 82:  # Key UP
            self.key_up_active = True
        if keycode == 81:  # Key DOWN
            self.key_down_active = True
        if keycode == 80:  # Key LEFT
            self.key_left_active = True
        if keycode == 79:  # Key RIGHT
            self.key_right_active = True
        if keycode == 19:  # p -> printscreen
            self.make_printscreen()
        if keycode == 22:  # s -> start
            self.run_simulation()

    def on_keyboard_up(self, instance, keyboard, keycode):
        if keycode == 82:  # Key UP
            self.key_up_active = False
        if keycode == 81:  # Key DOWN
            self.key_down_active = False
        if keycode == 80:  # Key LEFT
            self.key_left_active = False
        if keycode == 79:  # Key RIGHT
            self.key_right_active = False


    # Function to make printscreen
    def make_printscreen(self):
        im = Window.screenshot('racetrack.png')
        self.m = Image.load(im, keep_data=True)
        self.printscreen_available = True
        Window.borderless = False

    def run_simulation(self):
        if not(self.simulation_started):
            if self.first_run_simulation:
                self.make_printscreen()
                self.vehicles = {}
            else:
                pass

            with self.canvas:
                Color(0, 1, 0)
                for i in range(VEHICLE_POPULATION):
                    if self.first_run_simulation:
                        throttle = [1 for j in range(20)]
                        brake = [0 for j in range(20)]
                        left = [0 for j in range(20)]
                        right = [0 for j in range(20)]
                        for j in range(ITERATIONS-20):
                            a = random.randint(0,1)
                            b = random.randint(0,1)
                            c = random.randint(0,1)
                            throttle.append(a)
                            brake.append(int(not(a)))
                            if b:
                                left.append(c)
                                right.append(int(not(c)))
                            else:
                                left.append(0)
                                right.append(0)
                        self.vehicles[i] = vehicle(throttle=throttle, brake=brake, left=left, right=right)
                    else:
                        self.canvas.remove(self.vehicles[i].ellipse)
                        self.vehicles[i].veh_pos_x = START_POS_X
                        self.vehicles[i].veh_pos_y = START_POS_Y
                        self.vehicles[i].dur = 0
                        self.vehicles[i].dist = 0
                        self.vehicles[i].acc_frc = 0
                        self.vehicles[i].brk_frc = 0
                        self.vehicles[i].veh_spd = 0
                        self.vehicles[i].veh_acc = 0
                        self.vehicles[i].or_ang = START_ORIENTATION_ANGLE
                        self.vehicles[i].st_ang = 0
                        self.vehicles[i].on_track = True
                        self.vehicles[i].ranking = 0
                        self.vehicles[i].ellipse = Ellipse(pos=[START_POS_X, START_POS_Y], size=(ELLIPSE_DIAMETER, ELLIPSE_DIAMETER))

            self.simulation_started = True
            self.vehicles_crashed = 0
            self.iteration = 0
        else:
            pass  # Simulation ongoing

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
