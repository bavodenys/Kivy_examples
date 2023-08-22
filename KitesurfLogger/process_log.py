import json
import polyline
import folium
from functions import *
import matplotlib.pyplot as plt

window_size = 10

# Open the JSON file
with open('logfile_2023-08-22-22-02-58.json') as json_file:
    data = json.load(json_file)

x = []
y = []
z = []
timestamp = []
lon = []
lat = []
for entry in data:
    lon.append(entry['lon'])
    lat.append(entry['lat'])
    timestamp.append(entry['timestamp'])
    x.append(entry['x'])
    y.append(entry['y'])
    z.append(entry['z'])

x = moving_average(x[1:], window_size)
y = moving_average(y[1:], window_size)
z = moving_average(z[1:], window_size)



plt.plot(timestamp[window_size:], x, label='X')
plt.plot(timestamp[window_size:], y, label='Y')
plt.plot(timestamp[window_size:], z, label='Z')
plt.xlabel('Timestamp')
plt.ylabel('Gyroscope Data')
plt.title('Gyroscope Data Over Time')
plt.legend()  # Add legend based on labels
plt.show()


lat_average = moving_average(lat,50)
lon_average = moving_average(lon,50)

gps_data = []
for i in range(len(lat_average)):
    gps_data.append([lat_average[i],lon_average[i]])



#encoded_polyline = polyline.encode(gps_data)

latitude_start = 51.8436
longitude_start = 4.3674

# Create map with folium
m = folium.Map(location=[latitude_start, longitude_start], zoom_start=10)
folium.PolyLine(gps_data, color='red').add_to(m)
html_string = m.get_root().render()
file_path = 'output.html'

# Open the file in write mode and write the HTML string
with open(file_path, 'w') as file:
    file.write(html_string)

print("HTML content saved to", file_path)
print('stop')