from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock, mainthread
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivy_garden.mapview import MapMarker
from gps_emulator import gps_emulator
from plyer import gps

# Temporary lib import
from temp import *

# Set to True to just test the GUI (not the GPS functionality)
DEBUG = True

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1

#Activity calibrations
RUN_LOG_PERIOD = 1
BIKE_LOG_PERIOD = 1

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

class ActivityWindow(Screen):
    pass

class Run_activity(ButtonBehavior, MDBoxLayout):
    date = StringProperty('')
    start_time = StringProperty('')
    distance = StringProperty('')
    duration = StringProperty('')
    pace = StringProperty('')
    id = NumericProperty(0)


class Ride_activity(ButtonBehavior, MDBoxLayout):
    date = StringProperty('')
    start_time = StringProperty('')
    distance = StringProperty('')
    duration = StringProperty('')
    avg_spd = StringProperty('')
    id = NumericProperty(0)


class MainApp(MDApp):
    activity_type = StringProperty('run')

    activities_record = {
        'Run': 'run',
        'Ride': 'bike'
    }

    def __init__(self, activities, **kwargs):
        super().__init__(**kwargs)
        self.activities = activities
        self.gps_location = {}
        if DEBUG:
            self.gps_emulator = gps_emulator(gpx_filename='Run_1.gpx')

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
                                         avg_spd=f"Avg speed: {activity['avg_spd']}", \
                                         id=activity['id'])
            if activity['type'] == "run":
                activity_entry = Run_activity(date=f"Date: {activity['date']}", \
                                        start_time=f"Start time: {activity['start_time']}", \
                                        distance=f"Distance: {activity['distance']}", \
                                        duration=f"Duration: {activity['duration']}", \
                                        pace=f"Pace: {activity['pace']}", \
                                        id=activity['id'])
            self.root.screens[0].ids['activity_overview'].add_widget(activity_entry)
            self.root.screens[0].ids['activity_overview'].add_widget(MDLabel(size_hint=(1, None), height=dp(5)))

    def callback(self, instance):
        self.root.current = self.root.screens[1].name
        if instance.icon == 'bike':
            self.activity_type = "bike"
            Clock.schedule_interval(self.gps_log, BIKE_LOG_PERIOD)
            if DEBUG:
                pass
            else:
                self.log_period = BIKE_LOG_PERIOD

        if instance.icon == 'run':
            self.activity_type = "run"
            Clock.schedule_interval(self.gps_log, RUN_LOG_PERIOD)
            if DEBUG:
                pass
            else:
                self.log_period = RUN_LOG_PERIOD

        if DEBUG:
            gps_data = self.gps_emulator.get_gps_data(0)
            lat = gps_data.latitude
            lon = gps_data.longitude
        else:
            gps.start(self.log_period*1000, 0)
            # Should I add a wait of 1 second
            lat = self.gps_location['lat']
            lon = self.gps_location['lon']
            print('BADE')

        self.root.screens[1].ids['log_map'].center_on(lat, lon)
        self.map_marker = MapMarker(lat=lat, lon=lon)
        self.root.screens[1].ids['log_map'].add_widget(self.map_marker)

    @mainthread
    def on_location(self, **kwargs):
        for k, v in kwargs.items():
            self.gps_location[k] = v

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)


    def gps_log(self, dt):
        print('GPS log')

    def call_about(self):
        self.about_dialog = MDDialog(title= "About",
                                     text=f"Sport logger version {MAJOR_VERSION}.{MINOR_VERSION} \n" \
                                          f"Sport logger is created by Bavo Denys \n" \
                                          f"The source code can be found at https://github.com/bavodenys")
        self.about_dialog.open()

    # Function executed when activity is pressed on the homepage (data is fetched via the activity_id)
    def activity_pressed(self, activity_id):
        self.root.current = self.root.screens[2].name


if __name__ == "__main__":
    try:
        app = MainApp(activities=activities)
        app.run()
    except:
        pass