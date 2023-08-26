import random
from calibrations import *
import math

def generate_maze(rows, cols):
    maze = [[C_CELL_ALL_WALLS for _ in range(cols)] for _ in range(rows)]

    start_row = random.randint(0, rows - 1)
    start_col = random.randint(0, cols - 1)

    # Save the start_row, start_col as finish
    finish = [start_row, start_col]

    # Mark the starting cell as visited
    maze[start_row][start_col] = maze[start_row][start_col] | C_CELL_VISITED
    # Mark the starting cell also as finish
    maze[start_row][start_col] = maze[start_row][start_col] | C_CELL_FINISH

    # Create a stack and push the starting cell
    stack = [(start_row, start_col)]

    while stack:
        current_row, current_col = stack[-1]
        unvisited_neighbors = []

        # Check neighboring cells
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            next_row, next_col = current_row + dr, current_col + dc
            if 0 <= next_row < rows and 0 <= next_col < cols and maze[next_row][next_col] & C_CELL_VISITED == 0:
                unvisited_neighbors.append((next_row, next_col))

        if unvisited_neighbors:
            next_row, next_col = random.choice(unvisited_neighbors)
            maze[next_row][next_col] = maze[next_row][next_col] | C_CELL_VISITED
            if next_row == current_row:
                if next_col > current_col:
                    # Go RIGHT
                    maze[current_row][current_col] = maze[current_row][current_col] - C_CELL_RIGHT
                    maze[next_row][next_col] = maze[next_row][next_col] - C_CELL_LEFT
                if next_col < current_col:
                    # Go LEFT
                    maze[current_row][current_col] = maze[current_row][current_col] - C_CELL_LEFT
                    maze[next_row][next_col] = maze[next_row][next_col] - C_CELL_RIGHT
            if next_col == current_col:
                if next_row > current_row:
                    # Go DOWN
                    maze[current_row][current_col] = maze[current_row][current_col] - C_CELL_BOTTOM
                    maze[next_row][next_col] = maze[next_row][next_col] - C_CELL_TOP
                if next_row < current_row:
                    # Go UP
                    maze[current_row][current_col] = maze[current_row][current_col] - C_CELL_TOP
                    maze[next_row][next_col] = maze[next_row][next_col] - C_CELL_BOTTOM

            stack.append((next_row, next_col))
        else:
            stack.pop()

    return maze, finish

# Function to return distance sensor values: up, left, right, down
def get_distance_sensor_values(mouse_pos_abs, maze):
    # Determine the position in the maze with as reference the upper left corner
    mouse_pos_rel_x = mouse_pos_abs[0] - MAZE_REF_X
    mouse_pos_rel_y = MAZE_REF_Y - mouse_pos_abs[1]
    # Determine the cell the mouse is in
    index_x = math.floor(mouse_pos_rel_x / MAZE_BLOCK_SIZE)
    index_y = math.floor(mouse_pos_rel_y / MAZE_BLOCK_SIZE)
    # Determine the relative position in a cell
    remain_x = mouse_pos_rel_x % MAZE_BLOCK_SIZE
    remain_y = mouse_pos_rel_y % MAZE_BLOCK_SIZE
    # Determine distance up
    distance_up = remain_y - MOUSE_SIZE_Y/2 - WALL_THICKNESS
    i = 0
    while (not(maze[index_y-i][index_x] & C_CELL_TOP == C_CELL_TOP)):
        distance_up = distance_up + MAZE_BLOCK_SIZE
        i += 1
    # Determine distance down
    distance_down = (MAZE_BLOCK_SIZE - remain_y) - MOUSE_SIZE_Y/2 - WALL_THICKNESS
    i = 0
    while (not(maze[index_y+i][index_x] & C_CELL_BOTTOM == C_CELL_BOTTOM)):
        distance_down = distance_down + MAZE_BLOCK_SIZE
        i += 1
    # Determine distance right
    distance_right = (MAZE_BLOCK_SIZE - remain_x) - MOUSE_SIZE_X/2 - WALL_THICKNESS
    i = 0
    while (not(maze[index_y][index_x+i] & C_CELL_RIGHT == C_CELL_RIGHT)):
        distance_right = distance_right + MAZE_BLOCK_SIZE
        i += 1
    # Determine distance left
    distance_left = remain_x - MOUSE_SIZE_X/2 - WALL_THICKNESS
    i = 0
    while (not(maze[index_y][index_x-i] & C_CELL_LEFT == C_CELL_LEFT)):
        distance_left = distance_left + MAZE_BLOCK_SIZE
        i += 1
    # Return distances
    return distance_up, distance_down, distance_right, distance_left