from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
from functions import *
from calibrations import *
from path_algorithms import *

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1

# Calibrations
DEBUG_MODE = False

# Set window to screen size
Window.maximize()

# MicroMouse class
class MicroMouse(Widget):

    def __init__(self, start_pos_x, start_pos_y, **kwargs):
        self.pos_x = start_pos_x
        self.pos_y = start_pos_y
        # Orientation
        # Facing up: 0
        # Facing right: 3
        # Facing down: 6
        # Facing left: 9
        self.orientation = 0
        self.mouse_widgets = []
        super().__init__(**kwargs)
        Color(0,0,1)
        self.ellipse = Ellipse(pos=(self.pos_x-MOUSE_SIZE_X/2,self.pos_y-MOUSE_SIZE_Y/2), size=(MOUSE_SIZE_X, MOUSE_SIZE_Y))

    # Update the ellipse on the canvas
    def update_pos(self):
        Color(0,0,1)
        self.ellipse = Ellipse(pos=(self.pos_x - MOUSE_SIZE_X / 2, self.pos_y - MOUSE_SIZE_Y / 2), size=(MOUSE_SIZE_X, MOUSE_SIZE_Y))

    # Function to move mouse
    def move(self):
        if self.orientation == C_MOUSE_ORIEN_UP:
            self.pos_y = self.pos_y + 1
        elif self.orientation == C_MOUSE_ORIEN_RIGHT:
            self.pos_x = self.pos_x + 1
        elif self.orientation == C_MOUSE_ORIEN_DOWN:
            self.pos_y = self.pos_y - 1
        elif self.orientation == C_MOUSE_ORIEN_LEFT:
            self.pos_x = self.pos_x - 1
        else:
            pass

    def stop(self):
        pass

    # Function to turn right
    def go_right(self):
        self.orientation = self.orientation + 3
        if self.orientation == 12:
            self.orientation = C_MOUSE_ORIEN_UP

    # Function to turn left
    def go_left(self):
        self.orientation = self.orientation - 3
        if self.orientation == -3:
            self.orientation = C_MOUSE_ORIEN_LEFT


class MainWindow(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 1 / 60)
        # Generate the maze
        self.maze, self.finish = generate_maze(MAZE_BLOCKS_X, MAZE_BLOCKS_Y)
        self.maze_widgets = []
        # Selection of algorithm
        self.algorithm = maze_solve_algorithm(turning_preference="left")
        self.finished = False
        # Create the maze
        with self.canvas:
            self.mouse = MicroMouse(START_POS_X_MOUSE, START_POS_Y_MOUSE)
            Color(1, 1, 0)  #Yellow
            for j in range(MAZE_BLOCKS_Y):
                for i in range(MAZE_BLOCKS_X):
                    # Set finish of the maze
                    if self.maze[j][i] & C_CELL_FINISH == C_CELL_FINISH:
                        Color(0, 1, 0)
                        self.maze_widgets.append(Rectangle(pos=[MAZE_REF_X + i*MAZE_BLOCK_SIZE,MAZE_REF_Y - MAZE_BLOCK_SIZE - j*MAZE_BLOCK_SIZE], size=[MAZE_BLOCK_SIZE, MAZE_BLOCK_SIZE]))
                        Color(1, 1, 0)
                    # Set start of the maze
                    if i == 0 and j == MAZE_BLOCKS_Y - 1:
                        Color(1,0,0)
                        self.maze_widgets.append(Rectangle(pos=[MAZE_REF_X + i*MAZE_BLOCK_SIZE,MAZE_REF_Y - MAZE_BLOCK_SIZE - j*MAZE_BLOCK_SIZE], size=[MAZE_BLOCK_SIZE, MAZE_BLOCK_SIZE]))
                        Color(1, 1, 0)
                    if self.maze[j][i] & C_CELL_BOTTOM == C_CELL_BOTTOM:
                        self.maze_widgets.append(Rectangle(pos=[MAZE_REF_X + i*MAZE_BLOCK_SIZE, MAZE_REF_Y - MAZE_BLOCK_SIZE - j*MAZE_BLOCK_SIZE], size=[MAZE_BLOCK_SIZE,WALL_THICKNESS]))
                    if self.maze[j][i] & C_CELL_RIGHT == C_CELL_RIGHT:
                        self.maze_widgets.append(Rectangle(pos=[MAZE_REF_X + MAZE_BLOCK_SIZE-WALL_THICKNESS + i * MAZE_BLOCK_SIZE, MAZE_REF_Y -MAZE_BLOCK_SIZE - j * MAZE_BLOCK_SIZE],size=[WALL_THICKNESS, MAZE_BLOCK_SIZE]))
                    if self.maze[j][i] & C_CELL_LEFT == C_CELL_LEFT:
                        self.maze_widgets.append(Rectangle(pos=[MAZE_REF_X + i * MAZE_BLOCK_SIZE, MAZE_REF_Y - MAZE_BLOCK_SIZE - j * MAZE_BLOCK_SIZE],size=[WALL_THICKNESS, MAZE_BLOCK_SIZE]))
                    if self.maze[j][i] & C_CELL_TOP == C_CELL_TOP:
                        self.maze_widgets.append(Rectangle(pos=[MAZE_REF_X + i * MAZE_BLOCK_SIZE, MAZE_REF_Y - WALL_THICKNESS - j * MAZE_BLOCK_SIZE],size=[MAZE_BLOCK_SIZE, WALL_THICKNESS]))

    # Update
    def update(self, dt):
        if not(self.finished):
            sensor_front, sensor_right, sensor_left, sensor_back = get_distance_sensor_values([self.mouse.pos_x, self.mouse.pos_y],self.mouse.orientation, self.maze)
            self.algorithm.determine_next_move(sensor_front, sensor_right, sensor_left, sensor_back)
            self.canvas.remove(self.mouse.ellipse)
            with self.canvas:
                if self.algorithm.go_straight:
                    self.mouse.move()
                elif self.algorithm.go_right:
                    self.mouse.go_right()
                elif self.algorithm.go_left:
                    self.mouse.go_left()
                else:
                    pass
                self.mouse.update_pos()
            # Determine if the mouse finished!
            self.finished = determine_if_mouse_reached_finish(self.finish, self.mouse)
            if self.finished:
                print("Mouse found the finish")


class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.title = "Micromouse"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        Builder.load_file("layout.kv")
        return MainWindow()


# Main loop
if __name__ == "__main__":
    app = MainApp()
    app.run()
    app.stop()