import polyline

# Function to determine
# - lat/lon of center point of activity
# - lat/lon list of the activity
# - zoom level of the MapView
def determine_lat_lon_from_polyline(activity_polyline):
    lat_lon_list = polyline.decode(activity_polyline)
    max_lat = max(lat_lon_list, key=lambda item: item[1])[0]
    min_lat = min(lat_lon_list, key=lambda item: item[1])[0]
    max_lon = max(lat_lon_list, key=lambda item: item[1])[1]
    min_lon = min(lat_lon_list, key=lambda item: item[1])[1]
    if (max_lon-min_lon) <= 0.02:
        activity_zoom = 14
    elif (max_lon-min_lon) <= 0.04:
        activity_zoom = 13
    else:
        activity_zoom = 12
    return (max_lat+min_lat)/2, (max_lon+min_lon)/2, lat_lon_list, activity_zoom

# Function to convert s to a time indication x h x min x s
def convert_duration(duration_s):
    hour = int(duration_s)/3600
    remain_m_s = int(duration_s)%3600
    min = int(remain_m_s/60)
    remain_s = int(remain_m_s%60)
    if hour >= 1:
        duration_str = f"{hour:02} h {min:02} min {remain_s:02} s"
    elif min >= 1:
        duration_str = f"{min:02} min {remain_s:02} s"
    else:
        duration_str = f"{remain_s:02} s"
    return duration_str