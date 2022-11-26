from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import StringProperty
from plyer import gps

# Set to True to just test the GUI (not the GPS functionality)
DEBUG = True

# Calibrations window
WINDOW_WIDTH = dp(500)
WINDOW_HEIGHT = dp(800)

class WindowManager(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = NoTransition()
        Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)

class MainWindow(Screen):
    pass

class RecordWindow(Screen):
    pass

class MainApp(MDApp):
    activity_type = StringProperty('Run')

    data = {
        'Run': 'run',
        'Ride': 'bike'
    }

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
        self.theme_cls.primary_palette = "Orange"

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

    def callback(self, instance):
        if instance.icon == 'bike':
            self.root.current = self.root.screens[1].name
            self.activity_type = "Ride"

        if instance.icon == 'run':
            self.root.current = self.root.screens[1].name
            self.activity_type = "Run"

if __name__ == "__main__":
    try:
        app = MainApp()
        app.run()
    except:
        pass