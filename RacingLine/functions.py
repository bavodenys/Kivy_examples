from calibrations import *
from math import sin, cos, radians

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
    return vehicle_speed_new

# Calculate the vehicle position
def calculate_position(vehicle_pos_x, vehicle_pos_y, vehicle_speed, steering_angle, orientation_angle, delta_t):

    resulting_angle = orientation_angle - steering_angle
    vehicle_pos_y_new = vehicle_pos_y + (vehicle_speed*delta_t)*sin(radians(resulting_angle))*MAP_SCALING
    vehicle_pos_x_new = vehicle_pos_x + (vehicle_speed*delta_t)*cos(radians(resulting_angle))*MAP_SCALING
    return vehicle_pos_x_new, vehicle_pos_y_new, resulting_angle
