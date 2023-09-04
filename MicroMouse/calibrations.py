
# Calibrations
MAZE_REF_X = 100
MAZE_REF_Y = 1900
MAZE_BLOCKS_X = 16
MAZE_BLOCKS_Y = 16
MAZE_BLOCK_SIZE = 90
MAZE_REF_X_OFFS = MAZE_BLOCKS_X * MAZE_BLOCK_SIZE + 100
WALL_THICKNESS = 5
MOUSE_SIZE_X = 50
MOUSE_SIZE_Y = 50
START_POS_X_MOUSE = MAZE_REF_X + MAZE_BLOCK_SIZE/2
START_POS_Y_MOUSE = MAZE_REF_Y - (MAZE_BLOCKS_Y-1)*MAZE_BLOCK_SIZE - MAZE_BLOCK_SIZE/2

# Cell properties
C_CELL_BOTTOM = 1
C_CELL_RIGHT = 2
C_CELL_LEFT = 4
C_CELL_TOP = 8
C_CELL_ALL_WALLS = 15
C_CELL_START = 16
C_CELL_FINISH = 32
C_CELL_VISITED = 64

# Mouse orientations
C_MOUSE_ORIEN_UP = 0
C_MOUSE_ORIEN_RIGHT = 3
C_MOUSE_ORIEN_DOWN = 6
C_MOUSE_ORIEN_LEFT = 9






