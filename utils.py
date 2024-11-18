import random

def generate_starting_grid():
    # Create a flat list with 10 '1's (alive) and 54 '0's (dead)
    cells = [1] * 10 + [0] * 54
    
    # Shuffle the list to distribute alive cells randomly
    random.shuffle(cells)

    # Split the flat list into an 8x8 grid
    grid = [cells[i * 8:(i + 1) * 8] for i in range(8)]
    return grid
