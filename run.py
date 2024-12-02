
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

INITIAL_TILES = [];
GRID = [];
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

def generate_locations(rows, cols):
    global GRID, INITIAL_TILES
    assert rows < 9 # No more then 8 rows 
    assert cols < 9 # No more then 8 columns 
    
    for i in range(0, rows - 1):
        for j in range(0, cols - 1):
            GRID.append((i,j))
            
    for tile in example1['tiles']:
        INITIAL_TILES.append(tile)



# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class TileStatus(object):
    def __init__(self, cords, state) -> None:
        assert cords in COORDINATES
        self.x_coor = x_coor
        self.y_coor = y_coor
        self.state = state

    def _prop_name(self):
        return f"({self.x_coor}, {self.y_coor}: {self.state})"

@proposition(E)
class GridStatus(object):
    def __init__(self, iteration, grid) -> None:
        assert grid in
        self.iteration = iteration
        self.grid = grid

    def _prop_name(self):
        return f"({self.iteration}: {self.grid})"

@proposition(E)
class Stability(object):
    def __init__(self, grid1, grid2) -> None:
        assert grid1 in
        assert grid2 in
        self.grid1 = grid1
        self.grid2 = grid2

    def _prop_name(self):
        return f"({self.grid1} = {self.grid2})"

@proposition(E)
class Repeating(object):
    def __init__(self, i, j) -> None:
        assert grid[i] in 
        assert grid[j] in
        self.i = grid[i]
        self.j = grid[j]

    def _prop_name(self):
        return f"({self.i} = {self.i})"


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
