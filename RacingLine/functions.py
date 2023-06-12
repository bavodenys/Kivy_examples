from calibrations import *
from math import sin, cos, radians, sqrt, pow

# Function to calculate the acceleration
def calculate_acceleration(acceleration_force, braking_force, veh_spd):
    # Drag force
    drag_force = (AIR_DENSITY*DRAG_COEFF*FRONTAL_AREA*veh_spd*veh_spd)/2
    # Rolling resistance

    # Calculate acceleration
    acceleration = (acceleration_force-braking_force-drag_force)/(VEHICLE_MASS + DRIVER_MASS)
    return acceleration

# Function to calculate the vehicle speed
def calculate_speed(vehicle_speed_old, vehicle_acceleration, delta_t):
    vehicle_speed_new = vehicle_speed_old + (vehicle_acceleration*delta_t)
    if vehicle_speed_new < 0:
        vehicle_speed_new = 0
    else:
        pass
    return vehicle_speed_new

# Calculate the vehicle position
def calculate_position(vehicle_pos_x, vehicle_pos_y, vehicle_speed, steering_angle, orientation_angle, delta_t):
    resulting_angle = orientation_angle - steering_angle
    vehicle_pos_y_new = vehicle_pos_y + (vehicle_speed*delta_t)*sin(radians(resulting_angle))*MAP_SCALING
    vehicle_pos_x_new = vehicle_pos_x + (vehicle_speed*delta_t)*cos(radians(resulting_angle))*MAP_SCALING
    distance = calculate_distance(vehicle_pos_x, vehicle_pos_x_new, vehicle_pos_y, vehicle_pos_y_new)
    return vehicle_pos_x_new, vehicle_pos_y_new, resulting_angle, distance

def calculate_distance(x1, x2, y1, y2):
    distance = sqrt(pow(x2-x1,2) + pow(y2-y1,2))
    return distance

def determine_in_rectangle(veh_pos_x, veh_pos_y, or_ang, x0, y0, width, height):
    x_pos = {}
    y_pos = {}
    in_rectangle = VEH_ALL_COR
    x_pos['front_left_x'] = veh_pos_x - (VEHICLE_WIDTH/2)*cos(or_ang-START_ORIENTATION_ANGLE)-(VEHICLE_LENGTH/2)*sin(or_ang-START_ORIENTATION_ANGLE)
    x_pos['front_right_x'] = veh_pos_x + (VEHICLE_WIDTH/2)*cos(or_ang-START_ORIENTATION_ANGLE)-(VEHICLE_LENGTH/2)*sin(or_ang-START_ORIENTATION_ANGLE)
    x_pos['rear_left_x'] = veh_pos_x - (VEHICLE_WIDTH/2)*cos(or_ang-START_ORIENTATION_ANGLE)+(VEHICLE_LENGTH/2)*sin(or_ang-START_ORIENTATION_ANGLE)
    x_pos['rear_right_x'] = veh_pos_x + (VEHICLE_WIDTH/2)*cos(or_ang-START_ORIENTATION_ANGLE)+(VEHICLE_LENGTH/2)*sin(or_ang-START_ORIENTATION_ANGLE)
    y_pos['front_left_y'] = veh_pos_y + (VEHICLE_LENGTH/2)*cos(or_ang-START_ORIENTATION_ANGLE) - (VEHICLE_WIDTH/2)*sin(or_ang-START_ORIENTATION_ANGLE)
    y_pos['front_right_y'] = veh_pos_y + (VEHICLE_LENGTH/2)*cos(or_ang-START_ORIENTATION_ANGLE) + (VEHICLE_WIDTH/2)*sin(or_ang-START_ORIENTATION_ANGLE)
    y_pos['rear_left_y'] = veh_pos_y - (VEHICLE_LENGTH/2)*cos(or_ang-START_ORIENTATION_ANGLE) - (VEHICLE_WIDTH/2)*sin(or_ang-START_ORIENTATION_ANGLE)
    y_pos['rear_right_y'] = veh_pos_y - (VEHICLE_LENGTH/2)*cos(or_ang-START_ORIENTATION_ANGLE) + (VEHICLE_WIDTH/2)*sin(or_ang-START_ORIENTATION_ANGLE)

    for x in x_pos:
        if x_pos[x]<x0 or x_pos[x]>x0+width:
            if x == 'front_left_x':
                in_rectangle = in_rectangle & ~FRONT_LEFT
            if x == 'front_right_x':
                in_rectangle = in_rectangle & ~FRONT_RIGHT
            if x == 'rear_left_x':
                in_rectangle = in_rectangle & ~REAR_LEFT
            if x == 'rear_right_x':
                in_rectangle = in_rectangle & ~REAR_RIGHT
    for y in y_pos:
        if y_pos[y]<y0 or y_pos[y]>y0+height:
            if y == 'front_left_y':
                in_rectangle = in_rectangle & ~FRONT_LEFT
            if y == 'front_right_y':
                in_rectangle = in_rectangle & ~FRONT_RIGHT
            if y == 'rear_left_y':
                in_rectangle = in_rectangle & ~REAR_LEFT
            if y == 'rear_right_y':
                in_rectangle = in_rectangle & ~REAR_RIGHT
    return in_rectangle


def determine_on_track(veh_pos_x, veh_pos_y, or_ang, track):
    on_track = 0
    for seg in track:
        result = determine_in_rectangle(veh_pos_x, veh_pos_y, or_ang, track[seg]['TRACK_POS_X'], track[seg]['TRACK_POS_Y'], track[seg]['TRACK_SIZE_X'], track[seg]['TRACK_SIZE_Y'])
        on_track = on_track | result
    if on_track == VEH_ALL_COR:
        return True
    else:
        return False

