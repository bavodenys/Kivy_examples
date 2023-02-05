
def calculate_acceleration(acceleration_force, braking_force, veh_spd):
    drag_force = (AIR_DENSITY*DRAG_COEFF*FRONTAL_AREA*veh_spd*veh_spd)/2
    acceleration = (acceleration_force-braking_force-drag_force)/(VEHICLE_MASS + DRIVER_MASS)
    return acceleration
