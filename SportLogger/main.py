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
from kivy.graphics.vertex_instructions import Line, Ellipse
from kivymd.uix.dialog import MDDialog
from kivy.graphics import Color
from gps_emulator import gps_emulator
from plyer import gps
import numpy as np
from functions import *

# Temporary lib import
from temp import *

# Set to True to just test the GUI (not the GPS functionality)
DEBUG = True
# To enable the trajectory line
ENABLE_TRAJECTORY = True

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1

#Calibrations
RUN_LOG_PERIOD = 1
BIKE_LOG_PERIOD = 1
MARKER_RADIUS = 15

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
    activity_type = StringProperty('')
    activity_date = StringProperty('')
    activity_start_time = StringProperty('')
    activity_duration = StringProperty('')
    activity_distance = StringProperty('')
    activity_speed = StringProperty('')

    # Floating button actions
    activities_record = {
        'Run': 'run',
        'Ride': 'bike'
    }

    def __init__(self, activities, **kwargs):
        super().__init__(**kwargs)
        self.activities = activities
        self.gps_location = {}
        self.canvas_points_x = np.array([])
        self.canvas_points_y = np.array([])
        self.trajectory_line = []


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
        self.theme_cls.primary_palette = "Red"

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
        for activity_id in self.activities:
            if self.activities[activity_id]['type'] == "ride":
                activity_entry = Ride_activity(date=f"Date: {self.activities[activity_id]['date']}", \
                                         start_time=f"Start time: {self.activities[activity_id]['start_time']}", \
                                         distance=f"Distance: {self.activities[activity_id]['distance']}", \
                                         duration=f"Duration: {self.activities[activity_id]['duration']}", \
                                         avg_spd=f"Avg speed: {self.activities[activity_id]['avg_spd']}", \
                                         id=activity_id)
            if self.activities[activity_id]['type'] == "run":
                activity_entry = Run_activity(date=f"Date: {self.activities[activity_id]['date']}", \
                                        start_time=f"Start time: {self.activities[activity_id]['start_time']}", \
                                        distance=f"Distance: {self.activities[activity_id]['distance']}", \
                                        duration=f"Duration: {self.activities[activity_id]['duration']}", \
                                        pace=f"Pace: {self.activities[activity_id]['pace']}", \
                                        id=activity_id)
            self.root.screens[0].ids['activity_overview'].add_widget(activity_entry)
            self.root.screens[0].ids['activity_overview'].add_widget(MDLabel(size_hint=(1, None), height=dp(5)))

    def callback(self, instance):
        self.root.current = self.root.screens[1].name
        if instance.icon == 'bike':
            self.activity_type = "Ride"
            Clock.schedule_interval(self.gps_log, BIKE_LOG_PERIOD)
            if DEBUG:
                self.gps_emulator = gps_emulator(gpx_filename='Ride_1.gpx')
            else:
                self.log_period = BIKE_LOG_PERIOD

        if instance.icon == 'run':
            self.activity_type = "Run"
            Clock.schedule_interval(self.gps_log, RUN_LOG_PERIOD)
            if DEBUG:
                self.gps_emulator = gps_emulator(gpx_filename='Run_1.gpx')
            else:
                self.log_period = RUN_LOG_PERIOD

        if DEBUG:
            self.debug_counter = 0
            gps_data = self.gps_emulator.get_gps_data(self.debug_counter)
            lat = gps_data.latitude
            lon = gps_data.longitude
        else:
            gps.start(self.log_period*1000, 0)
            # Should I add a wait of 1 second
            lat = self.gps_location['lat']
            lon = self.gps_location['lon']
        # Center the map on the init GPS position
        self.root.screens[1].ids['log_map'].center_on(lat, lon)

    @mainthread
    def on_location(self, **kwargs):
        for k, v in kwargs.items():
            self.gps_location[k] = v

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    def gps_log(self, dt):
        if DEBUG:
            self.debug_counter+=int(dt)
            gps_data = self.gps_emulator.get_gps_data(self.debug_counter)
            lat = gps_data.latitude
            lon = gps_data.longitude
        else:
            lat = self.gps_location['lat']
            lon = self.gps_location['lon']

        if ENABLE_TRAJECTORY:
            # Get the x, y position of the new marker position
            x, y = self.root.screens[1].ids['log_map'].get_window_xy_from(lat=lat, lon=lon, zoom=16)
            # Determine how much the map will move in x and y direction
            move_x = self.root.screens[1].ids['log_map'].center_x - x
            move_y = self.root.screens[1].ids['log_map'].center_y - y

        # Center the map on the marker position
        self.root.screens[1].ids['log_map'].center_on(lat, lon)

        if ENABLE_TRAJECTORY:
            # Modify all points because the map moved
            self.canvas_points_x = self.canvas_points_x + move_x
            self.canvas_points_y = self.canvas_points_y + move_y
            # Add a new point to the numpy array
            self.canvas_points_x = np.append(self.canvas_points_x, x)
            self.canvas_points_y = np.append(self.canvas_points_y, y)

            # Try except structure because the first iteration the trajectory line is not existing yet
            try:
                for line in self.trajectory_line:
                    self.root.screens[1].canvas.remove(line)
            except:
                pass

        # Update of marker and line
        with self.root.screens[1].canvas:
            if ENABLE_TRAJECTORY:
                # Update of trajectory line
                array_size = self.canvas_points_x.size
                if array_size >= 2:
                    self.trajectory_line = []
                    color = Color(0, 1, 0)
                    for i in range(len(self.canvas_points_x)-1):
                        # Only display if the points will be on the map
                        if (abs(self.root.screens[1].ids['log_map'].center_x - self.canvas_points_x[i]) <= self.root.screens[1].ids['log_map'].width/2 and \
                            abs(self.root.screens[1].ids['log_map'].center_y - self.canvas_points_y[i]) <= self.root.screens[1].ids['log_map'].height/2 and \
                            abs(self.root.screens[1].ids['log_map'].center_x - self.canvas_points_x[i+1]) <= self.root.screens[1].ids['log_map'].width/2 and \
                            abs(self.root.screens[1].ids['log_map'].center_y - self.canvas_points_y[i+1]) <= self.root.screens[1].ids['log_map'].height/2):
                            line = Line(points=(self.canvas_points_x[i], self.canvas_points_y[i], self.canvas_points_x[i+1], self.canvas_points_y[i+1]), width=3)
                            self.trajectory_line.append(line)
            # Update of red marker
            color = Color(1, 0, 0)
            x = self.root.screens[1].ids['log_map'].center_x-MARKER_RADIUS/2
            y = self.root.screens[1].ids['log_map'].center_y-MARKER_RADIUS/2
            self.marker = Ellipse(pos=[x,y], size=[MARKER_RADIUS, MARKER_RADIUS])

    def start_pressed(self):
        pass

    # Activity is stopped
    def stop_pressed(self):
        self.root.current = self.root.screens[2].name

    # About
    def call_about(self):
        self.about_dialog = MDDialog(title= "About",
                                     text=f"Sport logger version {MAJOR_VERSION}.{MINOR_VERSION} \n" \
                                          f"Sport logger is created by Bavo Denys \n" \
                                          f"Source code: https://github.com/bavodenys")
        self.about_dialog.open()

    # Function executed when activity is pressed on the homepage (data is fetched via the activity_id)
    def activity_pressed(self, activity_id):
        self.root.current = self.root.screens[2].name
        if self.activities[activity_id]['type'] == "run":
            self.activity_type = "Run"
            self.activity_speed = self.activities[activity_id]['pace']
        elif self.activities[activity_id]['type'] == "ride":
            self.activity_type = "Ride"
            self.activity_speed = self.activities[activity_id]['avg_spd']
        self.activity_date = self.activities[activity_id]['date']
        self.activity_start_time = self.activities[activity_id]['start_time']
        self.activity_duration = self.activities[activity_id]['duration']
        self.activity_distance = self.activities[activity_id]['distance']
        self.polyline = self.activities[activity_id]['polyline']
        # Center the map on the activity
        lat_center, lon_center, lat_lon_list = determine_lat_lon_from_polyline(self.polyline)
        self.root.screens[2].ids['act_map'].center_on(lat_center, lon_center)
        self.activity_line = []
        color = Color(0, 1, 0)
        for i in range(len(lat_lon_list)-1):
            x1, y1 = self.root.screens[2].ids['act_map'].get_window_xy_from(lat=lat_lon_list[i][0], lon=lat_lon_list[i][1], zoom=12)
            x2, y2 = self.root.screens[2].ids['act_map'].get_window_xy_from(lat=lat_lon_list[i+1][0], lon=lat_lon_list[i+1][1], zoom=12)
            line = Line(points=(x1, y1, x2, y2), width=3)
            self.activity_line.append(line)


    # Function to go back to the homepage with overview of all activities
    def go_back_home(self):
        self.root.current = self.root.screens[0].name


if __name__ == "__main__":
    try:
        app = MainApp(activities=activities)
        app.run()
    except:
        pass
