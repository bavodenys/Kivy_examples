from kivymd.app import MDApp
from kivy.app import App
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
from kivy.storage.jsonstore import JsonStore
from gps_emulator import gps_emulator
from plyer import gps
from datetime import datetime
from copy import deepcopy
import numpy as np
from functions import *


# Set to True to just test the GUI (not the GPS functionality)
DEBUG = False
# To enable the trajectory line
ENABLE_TRAJECTORY = False

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1

#Calibrations
RUN_LOG_PERIOD = 1
BIKE_LOG_PERIOD = 1
MARKER_RADIUS = 15
RUN_SPEED_RC_FILTER = 0.05
RIDE_SPEED_RC_FILTER = 0.05
RUN_MOVING_THS_SPD = 1
RIDE_MOVING_THS_SPD = 1

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

    # Function executed when opening activity screen
    def on_enter(self):
        # Get the running App
        MDApp = App.get_running_app()
        # Set the zoom of the map
        MDApp.root.screens[2].ids['act_map'].set_zoom_at(MDApp.activity_zoom, 0, 0)
        # Center the map on the center of the activity
        MDApp.root.screens[2].ids['act_map'].center_on(MDApp.act_lat_center, MDApp.act_lon_center)
        with MDApp.root.screens[2].canvas:
            # Set the activity line color to red
            color = Color(1, 0, 0)
            # For loop over all points in the lat/lon list
            for i in range(len(MDApp.lat_lon_list)-1):
                x1, y1 = MDApp.root.screens[2].ids['act_map'].get_window_xy_from(lat=MDApp.lat_lon_list[i][0],
                                                                                 lon=MDApp.lat_lon_list[i][1],
                                                                                 zoom=MDApp.activity_zoom)
                x2, y2 = MDApp.root.screens[2].ids['act_map'].get_window_xy_from(lat=MDApp.lat_lon_list[i+1][0],
                                                                                 lon=MDApp.lat_lon_list[i+1][1],
                                                                                 zoom=MDApp.activity_zoom)
                line = Line(points=(x1,y1,x2,y2), width=3)
                MDApp.activity_line.append(line)


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
    record_duration = StringProperty('')
    record_distance = StringProperty('')
    record_speed = StringProperty('')
    record_type = StringProperty('')

    # Floating button actions
    activities_record = {
        'Run': 'run',
        'Ride': 'bike'
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.activities = JsonStore("activities.json")._data
        self.activities = JsonStore("activities.json")
        self.gps_location = {}
        self.canvas_points_x = np.array([])
        self.canvas_points_y = np.array([])
        self.trajectory_line = []
        self.record_gps_list = []
        self.record_active = False
        self.record_paused = False
        self.record_duration_s = 0
        self.record_distance_m = 0
        self.record_speed_m_s = 0
        self.record_type = ""
        self.record_saved = False


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
        self.root.screens[0].ids['activity_overview'].clear_widgets()  # Clear all activities from the overview
        for activity_id in self.activities:
            if self.activities[activity_id]['type'] == "ride":
                activity_entry = Ride_activity(date=f"Date: {self.activities[activity_id]['date']}", \
                                         start_time=f"Start time: {self.activities[activity_id]['start_time']}", \
                                         distance=f"Distance: {convert_m_to_km(self.activities[activity_id]['distance'])}", \
                                         duration=f"Duration: {convert_duration(self.activities[activity_id]['duration'])}", \
                                         avg_spd=f"Avg speed: {convert_speed_ride(self.activities[activity_id]['avg_spd'])}", \
                                         id=activity_id)
            if self.activities[activity_id]['type'] == "run":
                activity_entry = Run_activity(date=f"Date: {self.activities[activity_id]['date']}", \
                                        start_time=f"Start time: {self.activities[activity_id]['start_time']}", \
                                        distance=f"Distance: {convert_m_to_km(self.activities[activity_id]['distance'])}", \
                                        duration=f"Duration: {convert_duration(self.activities[activity_id]['duration'])}", \
                                        pace=f"Pace: {convert_speed_pace_run(self.activities[activity_id]['avg_spd'])}", \
                                        id=activity_id)
            self.root.screens[0].ids['activity_overview'].add_widget(activity_entry)
            self.root.screens[0].ids['activity_overview'].add_widget(MDLabel(size_hint=(1, None), height=dp(5)))

    def callback(self, instance):
        self.root.screens[0].ids['record_activity_menu'].close_stack()
        self.root.current = self.root.screens[1].name
        if instance.icon == 'bike':
            self.record_type = "Ride"
            self.root.screens[1].ids['record_speed'].text = 'Speed:'
            Clock.schedule_interval(self.gps_log, BIKE_LOG_PERIOD)
            if DEBUG:
                self.gps_emulator = gps_emulator(gpx_filename='Ride_1.gpx')
            else:
                self.log_period = BIKE_LOG_PERIOD

        if instance.icon == 'run':
            self.record_type = "Run"
            self.root.screens[1].ids['record_speed'].text = 'Pace:'
            Clock.schedule_interval(self.gps_log, RUN_LOG_PERIOD)
            if DEBUG:
                self.gps_emulator = gps_emulator(gpx_filename='Run_1.gpx')
            else:
                self.log_period = RUN_LOG_PERIOD

        if DEBUG:
            self.debug_counter = 0
            gps_data = self.gps_emulator.get_gps_data(self.debug_counter)
            self.lat = gps_data.latitude
            self.lon = gps_data.longitude
        else:
            gps.start(self.log_period*1000, 0)
            # Should I add a wait of 1 second
            self.lat = self.gps_location['lat']
            self.lon = self.gps_location['lon']
        # Copy the position to determine the distance
        self.lat_prev = deepcopy(self.lat)
        self.lon_prev = deepcopy(self.lon)
        # Center the map on the init GPS position
        self.root.screens[1].ids['log_map'].center_on(self.lat, self.lon)

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
            self.lat = gps_data.latitude
            self.lon = gps_data.longitude
        else:
            self.lat = self.gps_location['lat']
            self.lon = self.gps_location['lon']

        # Record activity list of (lat, lon)
        if self.record_active and not(self.record_paused):
            self.record_gps_list.append((self.lat, self.lon))

        # Activity duration
        if self.record_active and not(self.record_paused):
            self.record_duration_s += dt
            self.record_duration = convert_duration(self.record_duration_s)

        # Calculate the distance
        if self.record_active and not(self.record_paused):
            self.distance_covered = determine_distance(self.lat, self.lon, self.lat_prev, self.lon_prev)
            self.record_distance_m = self.record_distance_m + self.distance_covered
            self.record_distance = convert_distance(self.record_distance_m)
            self.lat_prev = deepcopy(self.lat)
            self.lon_prev = deepcopy(self.lon)

        # Calculate the speed
        if self.record_active and not(self.record_paused):
            if self.record_type == "Run":
                self.record_speed_m_s = rc_filter_speed(self.record_speed_m_s, self.distance_covered, dt,
                                                        RUN_SPEED_RC_FILTER)
                self.record_speed = f"{convert_speed_pace_run(self.record_speed_m_s)}"
            if self.record_type == "Ride":
                self.record_speed_m_s = rc_filter_speed(self.record_speed_m_s, self.distance_covered, dt,
                                                        RIDE_SPEED_RC_FILTER)
                self.record_speed = f"{convert_speed_ride(self.record_speed_m_s)}"

        if ENABLE_TRAJECTORY & self.record_active:
            # Get the x, y position of the new marker position
            x, y = self.root.screens[1].ids['log_map'].get_window_xy_from(lat=self.lat, lon=self.lon, zoom=16)
            # Determine how much the map will move in x and y direction
            move_x = self.root.screens[1].ids['log_map'].center_x - x
            move_y = self.root.screens[1].ids['log_map'].center_y - y

        # Center the map on the marker position
        self.root.screens[1].ids['log_map'].center_on(self.lat, self.lon)

        if ENABLE_TRAJECTORY & self.record_active:
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
            if ENABLE_TRAJECTORY & self.record_active:
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

    # Record start button pressed
    def start_pressed(self):
        if not(self.record_active):
            self.record_start_activity = datetime.now()

        # Start/Pause handling
        if self.root.screens[1].ids['record_start'].text == "Start":
            self.root.screens[1].ids['record_start'].text = 'Pause'
            self.record_paused = False
            self.record_active = True
        else:
            self.root.screens[1].ids['record_start'].text = 'Start'
            self.record_paused = True
            self.record_speed_m_s = 0

    # Record stop button is pressed
    def stop_pressed(self):
        if self.record_active:
            self.record_active = False
            record_polyline = polyline.encode(self.record_gps_list, 5)
            activity_id = len(self.activities)+1
            avg_spd = self.record_distance_m/self.record_duration_s
            # Save the activity in the json file
            self.activities.put(f"{activity_id}", type=f"{self.record_type.lower()}",
                date=f"{self.record_start_activity.day:02}/{self.record_start_activity.month:02}/{self.record_start_activity.year}",
                start_time=f"{self.record_start_activity.hour:02}:{self.record_start_activity.minute:02}",
                distance=f"{int(self.record_distance_m)}", duration=f"{int(self.record_duration_s)}",
                avg_spd=avg_spd, polyline=record_polyline)
            self.record_saved = True
            self.activity_pressed(activity_id)
        else:
            self.root.current = self.root.screens[0].name

    # About
    def call_about(self):
        self.about_dialog = MDDialog(title= "About",
                                     text=f"Sport logger version {MAJOR_VERSION}.{MINOR_VERSION} \n" \
                                          f"Sport logger is created by Bavo Denys \n" \
                                          f"Source code: https://github.com/bavodenys")
        self.about_dialog.open()

    # Function executed when activity is pressed on the homepage (data is fetched via the activity_id)
    def activity_pressed(self, activity_id_float):
        self.root.current = self.root.screens[2].name
        activity_id = str(int(activity_id_float))  # Don't understand why the activity id is a float
        if self.activities[activity_id]['type'] == "run":
            self.activity_type = "Run"
            self.root.screens[2].ids['activity_speed'].text = 'Pace:'
            self.activity_speed = convert_speed_pace_run(self.activities[activity_id]['avg_spd'])
        elif self.activities[activity_id]['type'] == "ride":
            self.activity_type = "Ride"
            self.root.screens[2].ids['activity_speed'].text = 'Avg Speed:'
            self.activity_speed = convert_speed_ride(self.activities[activity_id]['avg_spd'])
        self.activity_date = self.activities[activity_id]['date']
        self.activity_start_time = self.activities[activity_id]['start_time']
        self.activity_duration = convert_duration(self.activities[activity_id]['duration'])
        self.activity_distance = convert_m_to_km(self.activities[activity_id]['distance'])
        self.polyline = self.activities[activity_id]['polyline']
        # Determine from the polyline the lat/lon center and the list of coordinates
        self.act_lat_center, self.act_lon_center, self.lat_lon_list, self.activity_zoom = determine_lat_lon_from_polyline(self.polyline)
        self.activity_line = []

    # When starting to move the map -> remove the activity line
    def act_map_touch_down(self):
        for line in self.activity_line:
            self.root.screens[2].canvas.remove(line)
        self.activity_line = []

    # When the user stops moving the map -> draw the activity line again on the map
    def act_map_touch_up(self):
        with self.root.screens[2].canvas:
            color = Color(1, 0, 0)
            # For loop over all points in the lat/lon list
            for i in range(len(self.lat_lon_list)-1):
                x1, y1 = self.root.screens[2].ids['act_map'].get_window_xy_from(lat=self.lat_lon_list[i][0], lon=self.lat_lon_list[i][1], zoom=self.activity_zoom)
                x2, y2 = self.root.screens[2].ids['act_map'].get_window_xy_from(lat=self.lat_lon_list[i+1][0], lon=self.lat_lon_list[i+1][1], zoom=self.activity_zoom)
                line = Line(points=(x1,y1,x2,y2), width=3)
                self.activity_line.append(line)


    # Function to go back to the homepage with overview of all activities
    def go_back_home(self):
        self.root.current = self.root.screens[0].name
        if self.record_saved:  # Reload the activities when an activity was recorded
            Clock.schedule_once(self.init_gui, 1)
            self.record_saved = False
        # Remove the activity line on the MapView
        for line in self.activity_line:
            self.root.screens[2].canvas.remove(line)
        self.activity_line = []
        self.lat_lon_list = []


# MAIN
if __name__ == "__main__":
    try:
        app = MainApp()
        app.run()
    except:
        pass
