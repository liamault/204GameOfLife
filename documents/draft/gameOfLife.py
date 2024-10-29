import numpy as np
import time
import os

class GameOfLife:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.status = 'UNSTABLE'
        self.oldGrids = []
        
        #initialize with random alive and dead
        self.grid = np.random.randint(2, size=(rows, cols))

    def display(self):
        #clear the command line
        os.system('cls')
        
        #print top row border
        print("_"*(self.cols+2))

        #add rows
        for row in self.grid:
            rowStr = "".join(['O' if cell else ' ' for cell in row])
            
            # add left and right borders
            print('|' + rowStr + '|')

        #print bottom row border
        print("_"*(self.cols+2))

        #print status
        print(f'STATUS: {self.status}')

    def countNeighbors(self, x, y):
        
        #count the alive neighbors of a cell at position (x, y)
        total = np.sum(self.grid[max(0, x-1):min(self.rows, x+2), max(0, y-1):min(self.cols, y+2)])
        return total - self.grid[x, y]

    def step(self):
        newGrid = np.copy(self.grid)
        
        #loop through grid
        for i in range(self.rows):
            for j in range(self.cols):
                aliveNeighbors = self.countNeighbors(i, j)
                if self.grid[i, j] == 1:
                    #underpop vs overpop
                    if aliveNeighbors < 2 or aliveNeighbors > 3:
                        newGrid[i, j] = 0
                else:
                    #reproduction
                    if aliveNeighbors == 3:
                        newGrid[i, j] = 1
        
        #status logic
        if self.status == 'UNSTABLE':
            self.oldGrids.append(self.grid)
        
        #update grid
        self.grid = newGrid
        
        #more status logic
        if self.status == 'UNSTABLE':
            gridIndex = -1
            for i in range(len(self.oldGrids)-1, -1, -1):
                if np.array_equal(self.oldGrids[i], self.grid):
                    gridIndex = i
                    break
            if gridIndex != -1:
                loopLength = len(self.oldGrids) - gridIndex

                if loopLength == 1:
                    self.status = 'STATIC'
                else:
                    self.status = f'LOOP WITH LENGTH {loopLength}'

    def run(self, delay):
        while True:
            self.display()
            self.step()
            time.sleep(delay)
        

#initialize
game = GameOfLife(rows=20, cols=40)
game.run(delay=0.2)
