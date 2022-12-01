import gpxpy
import gpxpy.gpx
import time

class gps_emulator():

    def __init__(self, gpx_filename, **kwargs):
        super().__init__(**kwargs)
        self.gpx_file = open(gpx_filename, 'r')
        self.gpx = gpxpy.parse(self.gpx_file)
        self.gps_data = self.gpx.tracks[0].segments[0].points

    def get_gps_data(self, time):
        return self.gps_data[time]


if __name__ == "__main__":
    gps_emulator = gps_emulator(gpx_filename='Run_1.gpx')
    for i in range(100):
        time.sleep(1)
        data = gps_emulator.get_gps_data(i)
