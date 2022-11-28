from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from plyer import gps

from temp import *

# Set to True to just test the GUI (not the GPS functionality)
DEBUG = True

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1

# Calibrations window
if DEBUG:
    WINDOW_WIDTH = dp(500)
    WINDOW_HEIGHT = dp(800)

class WindowManager(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = NoTransition()
        if DEBUG:
            Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)

class MainWindow(Screen):
    pass

class RecordWindow(Screen):
    pass

class Run_activity(ButtonBehavior, MDBoxLayout):
    date = StringProperty('')
    start_time = StringProperty('')
    distance = StringProperty('')
    duration = StringProperty('')
    pace = StringProperty('')


class Ride_activity(ButtonBehavior, MDBoxLayout):
    date = StringProperty('')
    start_time = StringProperty('')
    distance = StringProperty('')
    duration = StringProperty('')
    avg_spd = StringProperty('')


class MainApp(MDApp):
    activity_type = StringProperty('Run')

    activities_record = {
        'Run': 'run',
        'Ride': 'bike'
    }

    def __init__(self, activities, **kwargs):
        super().__init__(**kwargs)
        self.activities = activities

    def request_android_permissions(self):
        """
        Since API 23, Android requires permission to be requested at runtime.
        This function requests permission and handles the response via a
        callback.
        The request will produce a popup if permissions have not already been
        been granted, otherwise it will do nothing.
        """
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            """
            Defines the callback to be fired when runtime permission
            has been granted or denied. This is not strictly required,
            but added for the sake of completeness.
            """
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)
        # # To request permissions without a callback, do:
        # request_permissions([Permission.ACCESS_COARSE_LOCATION,
        #                      Permission.ACCESS_FINE_LOCATION])

    def build(self):
        self.title = "Sport logger"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"

        if not(DEBUG):
            try:
                gps.configure(on_location=self.on_location,
                              on_status=self.on_status)
            except NotImplementedError:
                import traceback
                traceback.print_exc()
                self.gps_status = 'GPS is not implemented for your platform'

            if platform == "android":
                print("gps.py: Android detected. Requesting permissions")
                self.request_android_permissions()

        kv = Builder.load_file("layout.kv")
        return kv

    def on_start(self):
        Clock.schedule_once(self.init_gui, 1)

    def init_gui(self, dt):
        self.root.screens[0].ids['record_activity_menu'].icon = 'record'
        for activity in self.activities:
            if activity['type'] == "ride":
                activity_entry = Ride_activity(date=f"Date: {activity['date']}", \
                                         start_time=f"Start time: {activity['start_time']}", \
                                         distance=f"Distance: {activity['distance']}", \
                                         duration=f"Duration: {activity['duration']}", \
                                         avg_spd=f"Avg speed: {activity['avg_spd']}")
            if activity['type'] == "run":
                activity_entry = Run_activity(date=f"Date: {activity['date']}", \
                                        start_time=f"Start time: {activity['start_time']}", \
                                        distance=f"Distance: {activity['distance']}", \
                                        duration=f"Duration: {activity['duration']}", \
                                        pace=f"Pace: {activity['pace']}")
            self.root.screens[0].ids['activity_overview'].add_widget(activity_entry)
            #self.root.screens[0].ids['activity_overview'].add_widget(MDLabel(size_hint=(1, 0.1)))

    def callback(self, instance):
        if instance.icon == 'bike':
            self.root.current = self.root.screens[1].name
            self.activity_type = "Ride"

        if instance.icon == 'run':
            self.root.current = self.root.screens[1].name
            self.activity_type = "Run"

    def menu_callback(self):
        print('Menu callback')

    def activity_pressed(self):
        print('Activity pressed')


if __name__ == "__main__":
    try:
        app = MainApp(activities=activities)
        app.run()
    except:
        pass