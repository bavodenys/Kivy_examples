import random
from calibrations import *

def generate_maze(rows, cols):
    maze = [[C_CELL_ALL_WALLS for _ in range(cols)] for _ in range(rows)]

    start_row = random.randint(0, rows - 1)
    start_col = random.randint(0, cols - 1)

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

    return maze