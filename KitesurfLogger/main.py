from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from plyer import accelerometer, gps, gyroscope, gravity
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.clock import mainthread
from android import mActivity

# Window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 1600

# - buildozer android debug deploy run

class PlyerWindow(MDBoxLayout):
    accelerometer_values = StringProperty('')
    accelerometer_active = BooleanProperty(False)
    gyroscope_values = StringProperty('')
    gyroscope_active = BooleanProperty(False)
    gravity_values = StringProperty('')
    gravity_active = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #Window.size = (dp(WINDOW_WIDTH), dp(WINDOW_HEIGHT))
        # Activate the accelerometer
        self.accelerometer_active = False
        self.gravity_active = False
        self.gyroscope_active = False
        self.accelerometer_values = f"x: {0} \ny: {0}\nz: {0}"
        self.gravity_values = f"x: {0} \ny: {0}\nz: {0}"
        Clock.schedule_interval(self.update, 1 / 20)

    # Accelerometer button
    def accelerometer_button(self):
        try:
            if self.accelerometer_active:
                self.accelerometer_active = False
                accelerometer.disable()
            else:
                self.accelerometer_active = True
                accelerometer.enable()
        except NotImplementedError:
            self.accelerometer_values = "ERROR"


    def gyroscope_button(self):
        try:
            if self.gyroscope_active:
                self.gyroscope_active = False
                gyroscope.disable()
            else:
                self.gyroscope_active = True
                gyroscope.enable()
        except NotImplementedError:
            self.gyroscope_values = "ERROR"

    def gravity_button(self):
        try:
            if self.gravity_active:
                self.gravity_active = False
                gravity.disable()
            else:
                self.gravity_active = True
                gravity.enable()
        except NotImplementedError:
            self.gravity_values = "ERROR"


    def update(self, dt):
        if self.accelerometer_active:
            val = accelerometer.acceleration[:3]
            if not val == (None, None, None):
                self.accelerometer_values = f"x: {(val[0])}\ny: {(val[1])}\nz: {(val[2])}"

        if self.gyroscope_active:
            val = gyroscope.rotation[:3]
            if not val == (None, None, None):
                self.gyroscope_values = f"x: {(val[0])}\ny: {(val[1])}\nz: {(val[2])}"

        if self.gravity_active:
            val = gravity.gravity
            if not val == (None, None, None):
                self.gravity_values = f"x: {val[0]} \ny: {val[1]}\nz: {val[2]}"


class MainApp(MDApp):
    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')

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
        self.title = "Plyer window"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        self.gps_data = []

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

        Builder.load_file("layout.kv")
        return PlyerWindow()

    @mainthread
    def on_location(self, **kwargs):
        self.gps_location = '\n'.join(['{}={}'.format(k, v) for k, v in kwargs.items()])
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        self.gps_data.append((lat, lon))

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()
        self.save_gps_data_to_text()

    def save_gps_data_to_text(self):
        if self.gps_data:
            context = mActivity.getApplicationContext()
            result = context.getExternalFilesDir(None)
            if result:
                storage_path = str(result.toString())
            file_name = "logfile.txt"
            file_path = storage_path + "/" + file_name
            try:
                with open(file_path, "w") as f:
                    for lat, lon in self.gps_data:
                        print(f"lat: {lat}, lon: {lon} \n")
                        f.write(f"Latitude: {lat}, Longitude: {lon}\n")
            except Exception as e:
                print(f"The exception is: {e}")
            self.gps_data = []
            print("GPS data saved to text file!")

if __name__ == "__main__":
    try:
        app = MainApp()
        app.run()
    except:
        pass