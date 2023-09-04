from calibrations import *

class maze_solve_algorithm_1():

    def __init__(self, turning_preference, **kwargs):
        super().__init__(**kwargs)
        self.go_straight = False
        self.go_right = False
        self.go_left = False
        self.turning_preference = turning_preference
        if turning_preference == "right":
            self.right_counter = -10
            self.left_counter = 0
        else:
            self.right_counter = 0
            self.left_counter = -10

    def determine_next_move(self, sensor_front, sensor_right, sensor_left, sensor_back):
        self.go_straight = False
        self.go_right = False
        self.go_left = False
        if sensor_front <= 15:
            if self.turning_preference == "right":
                if sensor_right <= 15:
                    self.go_left = True
                    self.left_counter = 0
                else:
                    self.go_right = True
                    self.right_counter = -((MAZE_BLOCK_SIZE/2)-WALL_THICKNESS+2)
            else:
                if sensor_left <= 15:
                    self.go_right = True
                    self.right_counter = 0
                else:
                    self.go_left = True
                    self.left_counter = -((MAZE_BLOCK_SIZE/2)-WALL_THICKNESS+2)

        else:
            if self.turning_preference == "right":
                if sensor_right >= 50:
                    self.right_counter += 1
                    if self.right_counter >= ((MAZE_BLOCK_SIZE/2)-WALL_THICKNESS+2):
                        self.go_right = True
                        self.right_counter = -((MAZE_BLOCK_SIZE/2)-WALL_THICKNESS+2)
                    else:
                        self.go_straight = True
                else:
                    if self.left_counter < 15 and sensor_front < 25:
                        self.go_left = True
                        self.left_counter = 0
                    else:
                        self.right_counter = 0
                        self.go_straight = True
                        self.left_counter += 1
            else:
                if sensor_left >= 50:
                    self.left_counter += 1
                    if self.left_counter >= ((MAZE_BLOCK_SIZE/2)-WALL_THICKNESS+2):
                        self.go_left = True
                        self.left_counter = -((MAZE_BLOCK_SIZE/2)-WALL_THICKNESS+2)
                    else:
                        self.go_straight = True
                else:
                    if self.right_counter < 15 and sensor_front < 25:
                        self.go_right = True
                        self.right_counter = 0
                    else:
                        self.left_counter = 0
                        self.go_straight = True
                        self.right_counter += 1

class maze_solve_algorithm_2():
    pass