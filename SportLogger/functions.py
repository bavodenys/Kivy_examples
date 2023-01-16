import polyline

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