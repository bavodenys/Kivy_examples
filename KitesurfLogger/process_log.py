import json
import polyline
import folium

# Open the JSON file
with open('logfile_2023-08-21-21-06-17.json') as json_file:
    data = json.load(json_file)

gps_data = []
for entry in data:
    gps_data.append([entry['lat'],entry['lon']])

#encoded_polyline = polyline.encode(gps_data)

latitude_start = 50.8436
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