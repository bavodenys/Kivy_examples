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
import random

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
        self.mouse_widgets = []
        super().__init__(**kwargs)
        Color(0,0,1)
        self.ellipse = Ellipse(pos=(self.pos_x-MOUSE_SIZE_X/2,self.pos_y-MOUSE_SIZE_Y/2), size=(MOUSE_SIZE_X, MOUSE_SIZE_Y))

    # Update the ellipse on the canvas
    def update_pos(self):
        Color(0,0,1)
        self.ellipse = Ellipse(pos=(self.pos_x - MOUSE_SIZE_X / 2, self.pos_y - MOUSE_SIZE_Y / 2), size=(MOUSE_SIZE_X, MOUSE_SIZE_Y))



class MainWindow(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 1 / 60)
        # Generate the maze
        self.maze, finish = generate_maze(MAZE_BLOCKS_X, MAZE_BLOCKS_Y)
        #for i in range(MAZE_BLOCKS_X):
        #    for j in range(MAZE_BLOCKS_Y):
        #        self.maze[i][j] = self.maze[i][j] - 64

        self.maze_widgets = []
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
        distance_up, distance_down, distance_right, distance_left = get_distance_sensor_values([self.mouse.pos_x, self.mouse.pos_y], self.maze)
        print(f" UP:{distance_up}, DOWN: {distance_down}, RIGHT: {distance_right}, LEFT: {distance_left}")
        self.canvas.remove(self.mouse.ellipse)
        with self.canvas:
            self.mouse.update_pos()


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