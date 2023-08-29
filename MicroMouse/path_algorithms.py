from calibrations import *

class turn_right_algorithm():

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.go_straight = False
        self.go_right = False
        self.go_left = False
        self.right_counter = -10
        self.left_counter = 0

    def determine_next_move(self, sensor_front, sensor_right, sensor_left, sensor_back):
        self.go_straight = False
        self.go_right = False
        self.go_left = False
        if sensor_front <= 15:
            if sensor_right <= 15:
                self.go_left = True
                self.left_counter = 0
            else:
                self.go_right = True
                self.right_counter = -((MAZE_BLOCK_SIZE/2)-WALL_THICKNESS+2)
        else:
            if sensor_right >= 50:
                self.right_counter += 1
                if self.right_counter >= ((MAZE_BLOCK_SIZE/2)-WALL_THICKNESS):
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