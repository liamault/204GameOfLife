
from bauhaus import Encoding, proposition, constraint, And, Or
from bauhaus.utils import count_solutions, likelihood
from itertools import combinations
import time
import re
import numpy as np

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

#number of iterations
MAX_ITERATIONS = 10

#size of grid
GRID_SIZE = 8

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class TileStatus(object):
    def __init__(self, x, y, iteration) -> None:
        self.x = x
        self.y = y
        self.iteration = iteration

    def _prop_name(self):
        return f"(At iteration {self.iteration}, the tile at {self.x}, {self.y} is alive)"
    
@proposition(E)
class Has2Neighbors(object):
    def __init__(self, x, y, iteration) -> None:
        self.x = x
        self.y = y
        self.iteration = iteration

    def _prop_name(self):
        return f"(At iteration {self.iteration}, the tile at {self.x}, {self.y} has 2 neighbors)"
    
@proposition(E)
class Has3Neighbors(object):
    def __init__(self, x, y, iteration) -> None:
        self.x = x
        self.y = y
        self.iteration = iteration

    def _prop_name(self):
        return f"(At iteration {self.iteration}, the tile at {self.x}, {self.y} has 3 neighbors)"

@proposition(E)
class GridStatus(object):
    def __init__(self, iteration) -> None:
        self.iteration = iteration

    def _prop_name(self):
        return f"(The grid is alive at iteration {self.iteration})"

@proposition(E)
class Stability(object):
    def __init__(self, iteration) -> None:
        self.iteration = iteration

    def _prop_name(self):
        return f"(Itertation {self.iteration} will not change next iteration (Stable))"

@proposition(E)
class Repeating(object):
    def __init__(self, iteration) -> None:
        self.iteration = iteration

    def _prop_name(self):
        return f"(Iteration {self.iteration} will repeat in one of the next iterations (Repeating))"

@proposition(E)
class Glider(object):
    def __init__(self, iteration) -> None:
        self.iteration = iteration

    def _prop_name(self):
        return f"(Iteration {self.iteration} is a glider)"
    
@proposition(E)
class Oscillating(object):
    def __init__(self, iteration) -> None:
        self.iteration = iteration

    def _prop_name(self):
        return f"(Iteration {self.iteration} is oscillating)"

#blinker test
def blinkerTest():
    blinker = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if blinker[x][y] == 1:
                E.add_constraint(TileStatus(x,y,0))
            else:
                E.add_constraint(~TileStatus(x,y,0))

#glider test
def gliderTest():
    glider = [
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if glider[x][y] == 1:
                E.add_constraint(TileStatus(x, y, 0))
            else:
                E.add_constraint(~TileStatus(x, y, 0))


#box test
def boxTest():
    box = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if box[x][y] == 1:
                E.add_constraint(TileStatus(x,y,0))
            else:
                E.add_constraint(~TileStatus(x,y,0))

#dead test
def deadTest():
    dead = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if dead[x][y] == 1:
                E.add_constraint(TileStatus(x,y,0))
            else:
                E.add_constraint(~TileStatus(x,y,0))

#create tile constraints
def add_tile_constraints():
    
    for i in range(MAX_ITERATIONS - 1):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                
                #this gets neighbors
                neighbors = [
                    TileStatus(nx, ny, i)
                    for nx in range(x - 1, x + 2)
                    for ny in range(y - 1, y + 2)
                    if (nx, ny) != (x, y) and 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE
                ]

                # Define whether the tile has exactly 2 neighbors
                has_exactly_2_neighbors = And(
                    Or(*[And(*comb) for comb in combinations(neighbors, 2)]),
                    ~Or(*[And(*comb) for comb in combinations(neighbors, 3)])
                )
                E.add_constraint(has_exactly_2_neighbors >> Has2Neighbors(x, y, i))
                E.add_constraint(~has_exactly_2_neighbors >> ~Has2Neighbors(x, y, i))

                # Define whether the tile has exactly 3 neighbors
                has_exactly_3_neighbors = And(
                    Or(*[And(*comb) for comb in combinations(neighbors, 3)]),
                    ~Or(*[And(*comb) for comb in combinations(neighbors, 4)])
                )
                E.add_constraint(has_exactly_3_neighbors >> Has3Neighbors(x, y, i))
                E.add_constraint(~has_exactly_3_neighbors >> ~Has3Neighbors(x, y, i))

                # Conway's rules
                # 1. Dead cell with exactly 3 alive neighbors becomes alive
                E.add_constraint(
                    (~TileStatus(x, y, i) & Has3Neighbors(x, y, i)) >> TileStatus(x, y, i + 1)
                )

                # 2. Alive cell with fewer than 2 or more than 3 neighbors dies
                E.add_constraint(
                    (TileStatus(x, y, i) & (~Has2Neighbors(x, y, i) & ~Has3Neighbors(x, y, i))) >> ~TileStatus(x, y, i + 1)
                )

                # 3. Alive cell with exactly 2 or 3 neighbors stays alive
                E.add_constraint(
                    (TileStatus(x, y, i) & (Has2Neighbors(x, y, i) | Has3Neighbors(x, y, i))) >> TileStatus(x, y, i + 1)
                )

                # 4. Dead cell without exactly 3 neighbors stays dead
                E.add_constraint(
                    (~TileStatus(x, y, i) & ~Has3Neighbors(x, y, i)) >> ~TileStatus(x, y, i + 1)
                )

def add_grid_status_constraints():
    for i in range(MAX_ITERATIONS):
        
        #if any tiles are alive, grid is alive
        E.add_constraint(Or(*[TileStatus(x, y, i) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]) >> GridStatus(i))

        #if all tiles are dead, grid is dead
        E.add_constraint(And(*[~TileStatus(x, y, i) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]) >> ~GridStatus(i))

#is the next iteration eqivalent
def add_stable_constraints():
    for i in range(MAX_ITERATIONS - 1):

        equivalences = [
            (TileStatus(x, y, i) >> TileStatus(x, y, i+1)) &
            (TileStatus(x, y, i+1) >> TileStatus(x, y, i))
            for x in range(GRID_SIZE)
            for y in range(GRID_SIZE)
        ]

        E.add_constraint(Stability(i) >> And(*equivalences))

#repitition constraint, does iteration repeat in the future
def add_repitition_constraints():
    for i in range(MAX_ITERATIONS - 1):

        equivalences = Or(*[
            And(*[
                (TileStatus(x, y, i) >> TileStatus(x, y, j)) & 
                (TileStatus(x, y, j) >> TileStatus(x, y, i))
                for x in range(GRID_SIZE)
                for y in range(GRID_SIZE)
            ])
            for j in range(i + 1, MAX_ITERATIONS)
        ])

        E.add_constraint(Repeating(i) >> equivalences)
        
#glider constraint, does shape move in a diagonal (left-down) after 4 turns?
def add_glider_constraints():
    for i in range(MAX_ITERATIONS - 4):
        equivalences = []

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if x < GRID_SIZE - 1 and y < GRID_SIZE - 1:
                    equivalences.append(
                        (TileStatus(x, y, i) >> TileStatus(x+1, y+1, i+4)) &
                        (TileStatus(x+1, y+1, i+4) >> TileStatus(x, y, i))
                    )

        if equivalences:
            E.add_constraint(Glider(i) >> And(*equivalences))




# def add_oscillating_constraint():
#     for i         

#S → R and ¬(R → S)
def add_repeating_stability_relationship_constraints():
    for i in range(MAX_ITERATIONS - 1):
        
        #S → R
        E.add_constraint(
            Stability(i) >> Repeating(i)
        )
        
        #¬(R → S)
        E.add_constraint(
            ~(Repeating(i) >> Stability(i))
        )

#¬C → (S ∧ R)
def add_dead_grid_stable_and_repeats_constraint():
    for i in range(MAX_ITERATIONS - 1):
        E.add_constraint(
            ~GridStatus(i) >> (Stability(i) & Repeating(i))
        )



def example_theory():
    add_tile_constraints()
    add_grid_status_constraints()
    add_stable_constraints()
    add_repitition_constraints()
    add_glider_constraints()

    return E


if __name__ == "__main__":
    print("\nSelect a test to run:")
    print("1. Blinker Test")
    print("2. Dead Test")
    print("3. Glider Test")
    print("4. Box Test")
        
    choice = input("Enter your choice (1-4): ")
    
    if choice == '1':
        blinkerTest()
    elif choice == '2':
        deadTest()
    elif choice == '3':
        gliderTest()
    elif choice == '4':
        boxTest()
    else:
        print("Invalid choice. Please enter a number between 1 and 4.")


    T = example_theory()
    # Don't compile until you're finished adding all your constraints!

    print('STARTED COMPILING ...')
    T = T.compile()
    print('FINISHED COMPILING') 

    
    start_time = time.time()

    solve = T.solve()

    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % solve)  

    with open("solution.txt", "w") as file:
        file.write("Solution:\n")
        for key, value in solve.items():
            file.write(f"{key}: {value}\n")

    print("Solution written to solution.txt")

    matrices = [np.zeros((GRID_SIZE, GRID_SIZE), dtype=int) for _ in range(MAX_ITERATIONS)]
    pattern = re.compile(r"\(At iteration (\d+), the tile at (\d+), (\d+) is alive\)")
    
    for key, value in solve.items():
        if value:
            match = pattern.match(str(key))
            if match:
                iteration, x, y = map(int, match.groups())
                matrices[iteration][x, y] = 1

    with open("viz.txt", "w") as file:
        for i, matrix in enumerate(matrices):
            file.write(f"Iteration {i}:\n")
            for row in matrix:
                file.write(" ".join(map(str, row)) + "\n")
            file.write("\n")

    end_time = time.time()

    print(f"\nExecution Time: {end_time - start_time:.2f} seconds")
