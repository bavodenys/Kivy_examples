from kivymd.app import MDApp
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.clock import Clock
from gen_functions import *

# Calibrations
WINDOW_WIDTH = dp(500)
WINDOW_HEIGHT = dp(800)

class WindowManager(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = NoTransition()
        Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)

    # Start workout
    def start_workout(self):
        # Check start conditions
        if self.screens[0].number_of_sets_int > 0 and \
            self.screens[0].rest_duration_s > 0 and \
            self.screens[0].workout_duration_s > 0:
            self.current = self.screens[1].name
            Clock.schedule_interval(self.update, 1)

            # Init of set label and workout timer
            self.current_set = self.screens[0].number_of_sets_int
            self.timer = self.screens[0].rest_duration_s
            self.workout_state = "REST"

            # Init values for workout screen
            self.screens[1].current_set = str(self.current_set)
            self.screens[1].timer_value = convert_s_to_min_s_str(self.timer)
            self.screens[1].workout_state = self.workout_state

        else:
            print('No workout')


    # Stop workout
    def stop_workout(self):
        self.current = self.screens[0].name
        Clock.unschedule(self.update)

    # Update the workout screen
    def update(self, dt):
        self.timer -= 1
        if self.timer == 0:
            if self.workout_state == "REST":
                self.workout_state = "WORKOUT"
                self.timer = self.screens[0].workout_duration_s
            else:
                self.workout_state = "REST"
                self.timer = self.screens[0].rest_duration_s
                self.current_set -= 1
        else:
            pass

        # Workout is finished
        if self.current_set == 0:
            self.stop_workout()

        # Update labels
        self.screens[1].current_set = str(self.current_set)
        self.screens[1].timer_value = convert_s_to_min_s_str(self.timer)
        self.screens[1].workout_state = self.workout_state


class MainWindow(Screen):
    number_of_sets = StringProperty('0')
    workout_duration = StringProperty('00:00')
    rest_duration = StringProperty('00:00')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.number_of_sets_int = 0
        self.number_of_sets = str(self.number_of_sets)
        self.workout_duration_s = 0
        self.workout_duration = convert_s_to_min_s_str(self.workout_duration_s)
        self.rest_duration_s = 0
        self.rest_duration = convert_s_to_min_s_str(self.rest_duration_s)


    def sets_plus(self):
        self.number_of_sets_int +=1
        self.number_of_sets = str(self.number_of_sets_int)

    def sets_minus(self):
        if self.number_of_sets_int <= 1:
            pass
        else:
            self.number_of_sets_int -=1
        self.number_of_sets = str(self.number_of_sets_int)

    def work_plus(self):
        self.workout_duration_s +=1
        self.workout_duration = convert_s_to_min_s_str(self.workout_duration_s)

    def work_minus(self):
        if self.workout_duration_s <= 0:
            pass
        else:
            self.workout_duration_s -= 1
        self.workout_duration = convert_s_to_min_s_str(self.workout_duration_s)

    def rest_plus(self):
        self.rest_duration_s +=1
        self.rest_duration = convert_s_to_min_s_str(self.rest_duration_s)

    def rest_minus(self):
        if self.rest_duration_s <= 0:
            pass
        else:
            self.rest_duration_s -= 1
        self.rest_duration = convert_s_to_min_s_str(self.rest_duration_s)


class WorkOutWindow(Screen):
    current_set = StringProperty("")
    timer_value = StringProperty("")
    workout_state = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)



class MainApp(MDApp):

    def build(self):
        self.title = "Workout"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        kv = Builder.load_file("layout.kv")
        return kv



if __name__ == "__main__":
    try:
        app = MainApp()
        app.run()
    except:
        pass
