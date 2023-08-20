from kivymd.app import MDApp
from kivy.app import App
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from plyer import accelerometer, gps, gravity
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.clock import mainthread
from android import mActivity
import time

# Window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 1600

# - buildozer android debug deploy run

class PlyerWindow(MDBoxLayout):
    recording_active = BooleanProperty(False)
    recording_button_text = StringProperty("START")
    recording_text = StringProperty("OFF")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #Window.size = (dp(WINDOW_WIDTH), dp(WINDOW_HEIGHT))
        self.recording_active = False
        self.recording_button_text = "START"
        self.recording_text = "OFF"
        self.log_values_array = []
        Clock.schedule_interval(self.update, 1 / 20)

    def start_stop(self):
        MDApp = App.get_running_app()
        if not(self.recording_active):
            # Start recording
            self.recording_active = True
            self.recording_button_text = "STOP"
            self.recording_text = "Recording"
            MDApp.start_gps(50,0)
            accelerometer.enable()
            gravity.enable()
        else:
            # Stop recording
            MDApp.stop_gps()
            self.recording_active = False
            self.recording_button_text = "START"
            self.recording_text = "OFF"
            accelerometer.disable()
            gravity.disable()
            self.save_data()

    def update(self, dt):
        if self.recording_active:
            current_time = time.time()
            timestamp = f"Time: {current_time:.2f};"
            MDApp = App.get_running_app()
            gps_values = f"lat: {MDApp.lat}; lon: {MDApp.lon}; "
            # Acceleration
            val = accelerometer.acceleration[:3]
            if not val == (None, None, None):
                accelerometer_values = f"accx: {(val[0])}; accy: {(val[1])}; accz: {(val[2])}; "
            else:
                accelerometer_values = f"accx: Nan; accy: Nan; accz: Nan; "
            # Gravity
            val = gravity.gravity
            if not val == (None, None, None):
                gravity_values = f"grax: {val[0]}; gray: {val[1]}; graz: {val[2]}; "
            else:
                gravity_values = f"grax: Nan; gray: Nan; graz: Nan; "
            self.log_values_array.append(timestamp + gps_values + accelerometer_values + gravity_values)


    def save_data(self):
        context = mActivity.getApplicationContext()
        result = context.getExternalFilesDir(None)
        if result:
            storage_path = str(result.toString())
        file_name = "logfile.txt"
        file_path = storage_path + "/" + file_name
        try:
            with open(file_path, "w") as f:
                for log in self.log_values_array:
                    f.write(f"{log}\n")
        except Exception as e:
            print(f"The exception is: {e}")

class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lat = 0
        self.lon = 0

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


    def build(self):
        self.title = "Kitesurf logger"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"

        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
        except NotImplementedError:
            import traceback
            traceback.print_exc()

        if platform == "android":
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()

        Builder.load_file("layout.kv")
        return PlyerWindow()

    @mainthread
    def on_location(self, **kwargs):
        #self.gps_location = '\n'.join(['{}={}'.format(k, v) for k, v in kwargs.items()])
        self.lat = kwargs.get('lat')
        self.lon = kwargs.get('lon')

    @mainthread
    def on_status(self, stype, status):
        pass

    def start_gps(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop_gps(self):
        gps.stop()

if __name__ == "__main__":
    try:
        app = MainApp()
        app.run()
    except:
        pass