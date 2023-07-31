from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle, Rotate
from kivy.clock import Clock
from functions import *
from calibrations import *
import random

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1

# Calibrations
DEBUG_MODE = False

# Set window to screen size
Window.maximize()

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

        Color(0, 1, 0)
        self.rotate = Rotate(origin=[START_POS_X,START_POS_Y],
                             angle=self.or_ang-START_ORIENTATION_ANGLE)
        self.rectangle = Rectangle(pos=[START_POS_X-(VEHICLE_WIDTH/2), START_POS_Y-(VEHICLE_LENGTH/2)],
                                   size=(VEHICLE_WIDTH,VEHICLE_LENGTH))

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
    dashboard_st_ang = StringProperty('')
    dashboard_veh_spd = StringProperty('')

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
        if DEBUG_MODE:
            self.veh_pos_x = START_POS_X
            self.veh_pos_y = START_POS_Y
            self.or_ang = START_ORIENTATION_ANGLE
            self.dur = 0
            self.dist = 0
            self.acc_frc = 0
            self.brk_frc = 0
            self.veh_spd = 0
            self.veh_acc = 0
            self.or_ang = START_ORIENTATION_ANGLE
            self.st_ang = 0
            self.on_track = True
        # Auto control
        self.first_run_simulation = True
        self.vehicles_crashed = 0
        self.top_10 = {}
        self.circuit = []
        self.simulation_started = False
        # Create the racing track
        with self.canvas:
            Color(1, 1, 0)  #Yellow
            Rectangle(pos=[0,0], size=(MAX_POS_X, MAX_POS_Y))
            Color(0,0,0)  # Black
            for seg in TRACK:
                self.circuit.append(Rectangle(pos=[TRACK[seg]['TRACK_POS_X'], TRACK[seg]['TRACK_POS_Y']],
                                              size=(TRACK[seg]['TRACK_SIZE_X'], TRACK[seg]['TRACK_SIZE_Y'])))
            if DEBUG_MODE:
                Color(0, 1, 0)
                self.rotate = Rotate(origin=[START_POS_X, START_POS_Y],
                                     angle=self.or_ang - START_ORIENTATION_ANGLE)
                self.rectangle = Rectangle(pos=[START_POS_X - (VEHICLE_WIDTH / 2), START_POS_Y - (VEHICLE_LENGTH / 2)],
                                           size=(VEHICLE_WIDTH, VEHICLE_LENGTH))

    def update(self, dt):
        if DEBUG_MODE:
            if self.on_track:
                # Remove vehicle from canvas
                self.canvas.remove(self.rectangle)
                # Calculate the inputs
                self.acc_frc = ACCELERATING_FORCE if self.key_up_active else 0
                self.brk_frc = BRAKING_FORCE if self.key_down_active else 0
                if self.key_left_active and self.key_right_active:
                    pass
                else:
                    if self.key_left_active:
                        if self.st_ang <= -MAX_STEERING_ANGLE:
                            pass
                        else:
                            self.st_ang -= ANGLE_INCREASE
                    if self.key_right_active:
                        if self.st_ang >= MAX_STEERING_ANGLE:
                            pass
                        else:
                            self.st_ang += ANGLE_INCREASE
                # Calculate vehicle acceleration
                self.veh_acc = calculate_acceleration(self.acc_frc, self.brk_frc, self.veh_spd)
                # Calculate vehicle speed
                self.veh_spd = calculate_speed(self.veh_spd, self.veh_acc, dt)
                # Calculate vehicle position
                self.veh_pos_x, self.veh_pos_y, self.or_ang, self.dist = calculate_position(self.veh_pos_x,
                                                                                            self.veh_pos_y,
                                                                                            self.veh_spd,
                                                                                            self.st_ang,
                                                                                            self.or_ang, dt)
                # Determine if the vehicle is on the canvas
                veh_on_canvas = determine_in_rectangle(self.veh_pos_x,
                                                       self.veh_pos_y,
                                                       self.or_ang,
                                                       0, 0, MAX_POS_X, MAX_POS_Y)

                veh_on_circuit = determine_on_track(self.veh_pos_x, self.veh_pos_y, self.or_ang, TRACK)

                if not(veh_on_canvas) or not(veh_on_circuit):
                    self.on_track = False
                else:
                    pass

                with self.canvas:
                    Color(0, 1, 0)
                    self.rotate.origin = [self.veh_pos_x, self.veh_pos_y]
                    self.rotate.angle = self.or_ang - START_ORIENTATION_ANGLE
                    # self.vehicles[i].or_ang-START_ORIENTATION_ANGLE
                    self.rectangle = Rectangle(pos=[self.veh_pos_x - (VEHICLE_WIDTH / 2),
                                                    self.veh_pos_y - (VEHICLE_LENGTH / 2)],
                                                size=(VEHICLE_WIDTH, VEHICLE_LENGTH))

                self.dashboard_st_ang = str(self.st_ang)
                self.dashboard_veh_spd = str(self.veh_spd*3.6)

        else:
            if self.simulation_started and int(self.iteration) < ITERATIONS:
                for i in range(VEHICLE_POPULATION):
                    if self.vehicles[i].on_track:
                        self.canvas.remove(self.vehicles[i].rectangle)
                        # Calculate the inputs
                        self.vehicles[i].calculate_inputs(int(self.iteration))
                        # Calculate vehicle acceleration
                        self.vehicles[i].update_acceleration()
                        # Calculate vehicle speed
                        self.vehicles[i].update_speed(dt)
                        # Calculate vehicle position
                        self.vehicles[i].update_position_orientation(dt)
                        # Update vehicle stats
                        self.vehicles[i].update_veh_stats(dt)

                        veh_on_canvas = determine_in_rectangle(self.vehicles[i].veh_pos_x,
                                                               self.vehicles[i].veh_pos_y,
                                                               self.vehicles[i].or_ang,
                                                               0, 0, MAX_POS_X, MAX_POS_Y)
                        if veh_on_canvas and False:
                            veh_on_track = determine_on_track(self.vehicles[i].veh_pos_x,
                                                              self.vehicles[i].veh_pos_y,
                                                              self.vehicles[i].or_ang,
                                                              TRACK)
                        else:
                            veh_on_track = True
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
                            self.vehicles[i].rotate.origin = [self.vehicles[i].veh_pos_x, self.vehicles[i].veh_pos_y]
                            self.vehicles[i].rotate.angle = self.vehicles[i].or_ang - START_ORIENTATION_ANGLE
                            # self.vehicles[i].or_ang-START_ORIENTATION_ANGLE
                            self.vehicles[i].rectangle=Rectangle(pos=[self.vehicles[i].veh_pos_x-(VEHICLE_WIDTH/2),
                                                                      self.vehicles[i].veh_pos_y-(VEHICLE_LENGTH/2)],
                                                                 size=(VEHICLE_WIDTH, VEHICLE_LENGTH))


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


    def run_simulation(self):
        if not(self.simulation_started):
            if self.first_run_simulation:
                self.vehicles = {}
            else:
                pass

            with self.canvas:
                Color(0, 1, 0)
                for i in range(VEHICLE_POPULATION):
                    if self.first_run_simulation:
                        throttle = [1 for j in range(80)]
                        brake = [0 for j in range(80)]
                        left = [0 for j in range(80)]
                        right = [0 for j in range(80)]
                        for j in range(ITERATIONS-80):
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
                        self.canvas.remove(self.vehicles[i].rectangle)
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
                        self.vehicles[i].rectangle = Rectangle(pos=[self.vehicles[i].veh_pos_x-(VEHICLE_WIDTH/2),
                                                                  self.vehicles[i].veh_pos_y-(VEHICLE_LENGTH/2)],
                                                             size=(VEHICLE_WIDTH, VEHICLE_LENGTH))

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
