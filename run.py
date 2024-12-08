
from bauhaus import Encoding, proposition, constraint, And, Or
from bauhaus.utils import count_solutions, likelihood
from itertools import combinations
import time

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
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if glider[x][y] == 1:
                E.add_constraint(TileStatus(x,y,0))
            else:
                E.add_constraint(~TileStatus(x,y,0))

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
                    for nx in range(x-1, x+2)
                    for ny in range(y-1, y+2)
                    if (nx, ny) != (x, y) and 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE
                ]

                #define whether or not tile has 2 neighbors or not
                has_2_neighbors = Or(*[
                    And(*comb) for comb in combinations(neighbors, 2)
                ])
                E.add_constraint(has_2_neighbors >> Has2Neighbors(x, y, i))
                E.add_constraint(~has_2_neighbors >> ~Has2Neighbors(x, y, i))

                #define whether or not tile has 3 neighbors or not
                has_3_neighbors = Or(*[
                    And(*comb) for comb in combinations(neighbors, 3)
                ])
                E.add_constraint(has_3_neighbors >> Has3Neighbors(x, y, i))
                E.add_constraint(~has_3_neighbors >> ~Has3Neighbors(x, y, i))

                #if dead and three alive neighbors, become alive
                E.add_constraint(
                    (~TileStatus(x, y, i) & (Has3Neighbors(x, y, i))) >> TileStatus(x, y, i+1)
                )

                #if dead and dont have three alive neighbors, stay dead
                E.add_constraint(
                    (~TileStatus(x, y, i) & (~Has3Neighbors(x, y, i))) >> ~TileStatus(x, y, i+1)
                )

                #if alive with less than 2 or more than 3 alive neighbors, die
                E.add_constraint(
                    (TileStatus(x, y, i) & (~Has2Neighbors(x, y, i) & ~Has3Neighbors(x, y, i))) >> ~TileStatus(x, y, i+1)
                )

                #if alive with with 2 or 3 neighbors, stay alive
                E.add_constraint(
                    (TileStatus(x, y, i) & (Has2Neighbors(x, y, i) | Has2Neighbors(x, y, i))) >> TileStatus(x, y, i+1)
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

        equivalences = [
            (TileStatus(x, y, i) >> TileStatus(x, y, j)) & 
            (TileStatus(x, y, j) >> TileStatus(x, y, i))
            for j in range(i + 1, MAX_ITERATIONS)
            for x in range(GRID_SIZE)
            for y in range(GRID_SIZE)
        ]

        E.add_constraint(Repeating(i) >> And(*equivalences))
        
#glider constraint, does shape move in a diagonal after 4 turns?
def add_glider_constraints():
    for i in range(MAX_ITERATIONS - 4):
        equivalences = []

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                #up left
                if x > 0 and y > 0:
                    equivalences.append(
                        (TileStatus(x, y, i) >> TileStatus(x-1, y-1, i+4)) &
                        (TileStatus(x-1, y-1, i+4) >> TileStatus(x, y, i))
                    )

                #up right
                if x > 0 and y < GRID_SIZE - 1:
                    equivalences.append(
                        (TileStatus(x, y, i) >> TileStatus(x-1, y+1, i+4)) &
                        (TileStatus(x-1, y+1, i+4) >> TileStatus(x, y, i))
                    )

                #down left
                if x < GRID_SIZE - 1 and y > 0:
                    equivalences.append(
                        (TileStatus(x, y, i) >> TileStatus(x+1, y-1, i+4)) &
                        (TileStatus(x+1, y-1, i+4) >> TileStatus(x, y, i))
                    )

                #down right
                if x < GRID_SIZE - 1 and y < GRID_SIZE - 1:
                    equivalences.append(
                        (TileStatus(x, y, i) >> TileStatus(x+1, y+1, i+4)) &
                        (TileStatus(x+1, y+1, i+4) >> TileStatus(x, y, i))
                    )

        E.add_constraint(Repeating(i) >> And(*equivalences))

        

#S → R and ¬(R → S)
def add_repeating_stability_relationship_constraints():
    for i in range(MAX_ITERATIONS):
        
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
    for i in range(MAX_ITERATIONS):
        E.add_constraint(
            ~GridStatus(i) >> (Stability(i) & Repeating(i))
        )



def example_theory():

    add_tile_constraints()
    add_grid_status_constraints()
    add_stable_constraints()
    add_repitition_constraints()
    add_glider_constraints

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

    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())  

    end_time = time.time()

    print(f"\nExecution Time: {end_time - start_time:.2f} seconds")
    # print("\nVariable likelihoods:")
    # for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
    #     # Ensure that you only send these functions NNF formulas
    #     # Literals are compiled to NNF here
    #     print(" %s: %.2f" % (vn, likelihood(T, v)))
    # print()
