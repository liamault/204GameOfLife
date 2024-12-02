
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

#used for simplicity
import numpy as np

# Encoding that will store all of your constraints
E = Encoding()

#blinker setup
INITIAL_TILES = [(3,3),(3,4),(3,5)];
GRIDS = [];
NEIGHBOURS = {};

# moving in the grid i.e. finding neighbors 
move = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
    "across_right_up": (-1, 1),
    "across_left_up": (-1, -1),
    "across_right_down": (1, 1),
    "across_left_down": (1, -1)
}

# getting neighbors for a cell
def get_neighbors(row, col, grid):
    global NEIGHBORS
    for direction in move.values():
        # neighbor coordinates
        new_row, new_col = row + direction[0], col + direction[1]
        
        # check if  within bounds
        if 0 <= new_row < len(grid) and 0 <= new_col < len(grid[0]):
            NEIGHBORS.append((new_row, new_col))
    return NEIGHBORS

def initialize_neighbors(grid):
    #loop through both and x and y
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            NEIGHBORS[(row, col)] = get_neighbors(row, col, grid)

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class TileStatus(object):
    def __init__(self, cords, state, iteration) -> None:
        assert cords in COORDINATES
        self.x_coor = x_coor
        self.y_coor = y_coor
        self.iteration = iteration

    def _prop_name(self):
        return f"(At iteration {self.iteration}, the tile at {self.x_coor}, {self.y_coor} is alive)"

@proposition(E)
class GridStatus(object):
    def __init__(self, iteration) -> None:
        self.iteration = iteration

    def _prop_name(self):
        return f"(The grid is alive at iteration {self.iteration})"

@proposition(E)
class Stability(object):
    def __init__(self, iteration1, iteration2) -> None:
        self.iteration = iteration

    def _prop_name(self):
        return f"(Itertation {iteration} is the same as the previous iteration (Stable))"

@proposition(E)
class Repeating(object):
    def __init__(self, i) -> None:
        self.iteration

    def _prop_name(self):
        return f"(Iteration {iteration} is the same as one of the previous iterations (Repeating))"

@proposition(E)
class Glider(object):
    def __init__(self, i) -> None:
        self.iteration

    def _prop_name(self):
        return f"(Iteration {iteration} is a glider)"

#create initial grid, and add Tile Status constraint to each tile
def initialize_grid(rows=8, cols=8, initialAlive=[]):
    for x in range(rows):
        for y in range(cols):
            if (x, y) in initialAlive
                E.add_constraint(TileStatus(x, y, 0))
            else:
                E.add_constraint(~TileStatus(x, y, 0))

# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
@constraint.at_least_one(E)
@proposition(E)
class FancyPropositions:

    def __init__(self, data):
        self.data = data

    def _prop_name(self):
        return f"A.{self.data}"

# Call your variables whatever you want
a = BasicPropositions("a")
b = BasicPropositions("b")   
c = BasicPropositions("c")
d = BasicPropositions("d")
e = BasicPropositions("e")
# At least one of these will be true
x = FancyPropositions("x")
y = FancyPropositions("y")
z = FancyPropositions("z")


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():

    # A tile is placed for every space on the grid either alive or dead
    for tile in GRID:
        x_coor = tile[0]
        y_coor = tile[1]
        
        if tile in INITIAL_TILES:
            tile_propositions = TileStatus(x_coor, y_coor, 1)
        else:
            tile_propositions = TileStatus(x_coor, y_coor, 0)

        constraint.add_exactly_one(E, tile_propositions)

    # TODO: need to create function get_alive_neighbours which returns the number of neighbours of a given tile
    # Alive tile remains alive with 2 or 3 neighbors
    for tile in GRID:
            E.add_constraint((tile.state.implies((get_alive_neighbors(tile) == 2) | (get_alive_neighbors(tile) == 3))))
    
    # Alive tile dies otherwise
    for tile in GRID:
            E.add_constraint((tile.state.implies(~((get_alive_neighbors(tile) < 2) | (get_alive_neighbors(tile) > 3)))))
    
    # Dead tile becomes alive with exactly 3 neighbors
    for tile in GRID:
            E.add_constraint((~tile.state).implies(get_alive_neighbors(tile) == 3))

    # Add custom constraints by creating formulas with the variables you created. 
    E.add_constraint((a | b) & ~x)
    # Implication
    E.add_constraint(y >> z)
    # Negate a formula
    E.add_constraint(~(x & y))
    # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    constraint.add_exactly_one(E, a, b, c)

    return E


if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()
