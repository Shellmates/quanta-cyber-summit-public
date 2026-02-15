import numpy as np

def validate_sudoku(grid):
    grid = np.array(grid)
    
    if grid.shape != (9, 9):
        return False
    
    if not np.all((grid >= 1) & (grid <= 9)):
        return False
    
    for row in grid:
        if len(set(row)) != 9:
            return False
    
    for col in grid.T:
        if len(set(col)) != 9:
            return False
    
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            box = grid[box_row:box_row+3, box_col:box_col+3].flatten()
            if len(set(box)) != 9:
                return False
    
    return True