
from bauhaus import Encoding, proposition, constraint, And, Or
from bauhaus.utils import count_solutions, likelihood
from itertools import combinations

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "auto"

# Encoding that will store all of your constraints
E = Encoding()

#number of iterations
MAX_ITERATIONS = 1

#size of grid
GRID_SIZE = 4

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
        return f"(Iteration {self.iteration} is the same as one of the previous iterations (Repeating))"

@proposition(E)
class Glider(object):
    def __init__(self, iteration) -> None:
        self.iteration = iteration

    def _prop_name(self):
        return f"(Iteration {self.iteration} is a glider)"

#TESTS ARE GONNA GO HERE
#this is where initial tile states will be made

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

            



# IGNORE THIS JUNK ---------------------------------------------------------------------------------------------------------------------

# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
# @constraint.at_least_one(E)
# @proposition(E)
# class FancyPropositions:

#     def __init__(self, data):
#         self.data = data

#     def _prop_name(self):
#         return f"A.{self.data}"

# # Call your variables whatever you want
# a = BasicProposi
# tions("a")
# b = BasicPropositions("b")   
# c = BasicPropositions("c")
# d = BasicPropositions("d")
# e = BasicPropositions("e")
# # At least one of these will be true
# x = FancyPropositions("x")
# y = FancyPropositions("y")
# z = FancyPropositions("z")

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.

#helper function for tile constrints
def exactly_n_neighbors(neighbors, n):
    return Or(
        *[
            And(*subset, *[~neighbor for neighbor in neighbors if neighbor not in subset])
            for subset in combinations(neighbors, n)
        ]
    )


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

                exactly2neighbors = exactly_n_neighbors(neighbors, 2)
                exactly3neighbors = exactly_n_neighbors(neighbors, 3)

                #if dead and three alive neighbors, become alive
                E.add_constraint(
                    (~TileStatus(x, y, i) & (exactly3neighbors)) >> TileStatus(x, y, i+1)
                )

                #if alive with less than 2 or more than 3 alive neighbors, die
                E.add_constraint(
                    (TileStatus(x, y, i) & (~exactly2neighbors & ~exactly3neighbors)) >> ~TileStatus(x, y, i+1)
                )

                #if alive with with 2 or 3 neighbors, stay alive
                E.add_constraint(
                    (TileStatus(x, y, i) & (exactly2neighbors | exactly3neighbors)) >> TileStatus(x, y, i+i)
                )


def add_grid_status_constraints():
    for i in range(MAX_ITERATIONS):
        
        #if any tiles are alive, grid is alive
        E.add_constraint(Or(*[TileStatus(x, y, i) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]) >> GridStatus(i))

        #if all tiles are dead, grid is dead
        E.add_constraint(And(*[~TileStatus(x, y, i) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]) >> ~GridStatus(i))

def add_stable_constraints():
    for i in range(MAX_ITERATIONS):
        
        #if all the values of the current iteration match the next iteration, it is stable
        if i != (MAX_ITERATIONS-1):
            E.add_constraint(
                And(*[TileStatus(x, y, i) == TileStatus(x, y, i+1) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]) >> Stability(i)
            )

        #backwards constraints
        if i != 0:
            E.add_constraint(
                And(*[TileStatus(x, y, i) == TileStatus(x, y, i-1) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]) >> Stability(i)
            )

def add_repitition_constraints():
    for i in range(MAX_ITERATIONS):
        
        #add constraints for repetitions
        if i != (MAX_ITERATIONS-1):
            E.add_constraint(
                Or(*[
                    And(*[TileStatus(x, y, i) == TileStatus(x, y, k) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]) for k in range(i+1, MAX_ITERATIONS)
                ]) >> Repeating(i)
            )
        
        #backwards constraints
        if i != 0:
            E.add_constraint(
                Or(*[
                    And(*[TileStatus(x, y, i) == TileStatus(x, y, k) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]) for k in range(0, i)
                ]) >> Repeating(i)
            )

def add_glider_constraints():
    for i in range(MAX_ITERATIONS):
        
        #add constraints for glider (forward)
        if i <= MAX_ITERATIONS - 5:
            #down right
            E.add_constraint(
                And(*[
                    TileStatus(x, y, i) == TileStatus(x + 1, y + 1, i + 4) for x in range(GRID_SIZE - 1) for y in range(GRID_SIZE - 1)
                ]) >> Glider(i)
            )

            #down left
            E.add_constraint(
                And(*[
                    TileStatus(x, y, i) == TileStatus(x + 1, y - 1, i + 4) for x in range(GRID_SIZE - 1) for y in range(1, GRID_SIZE)
                ]) >> Glider(i)
            )

            #up right
            E.add_constraint(
                And(*[
                    TileStatus(x, y, i) == TileStatus(x - 1, y + 1, i + 4) for x in range(1, GRID_SIZE) for y in range(GRID_SIZE - 1)
                ]) >> Glider(i)
            )

            #up left
            E.add_constraint(
                And(*[
                    TileStatus(x, y, i) == TileStatus(x - 1, y - 1, i + 4) for x in range(1, GRID_SIZE) for y in range(1, GRID_SIZE)
                ]) >> Glider(i)
            )

        #backwards constraints
        if i >= 4:
            #down right
            E.add_constraint(
                And(*[
                    TileStatus(x + 1, y + 1, i) == TileStatus(x, y, i - 4) for x in range(GRID_SIZE - 1) for y in range(GRID_SIZE - 1)
                ]) >> Glider(i)
            )

            #down left
            E.add_constraint(
                And(*[
                    TileStatus(x + 1, y - 1, i) == TileStatus(x, y, i - 4) for x in range(GRID_SIZE - 1) for y in range(1, GRID_SIZE)
                ]) >> Glider(i)
            )

            #up right
            E.add_constraint(
                And(*[
                    TileStatus(x - 1, y + 1, i) == TileStatus(x, y, i - 4) for x in range(1, GRID_SIZE) for y in range(GRID_SIZE - 1)
                ]) >> Glider(i)
            )

            #up left
            E.add_constraint(
                And(*[
                    TileStatus(x - 1, y - 1, i) == TileStatus(x, y, i - 4) for x in range(1, GRID_SIZE) for y in range(1, GRID_SIZE)
                ]) >> Glider(i)
            )

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
    # add_grid_status_constraints()

    return E


if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    
    print('STARTED COMPILING ...')
    T = T.compile()
    print('FINISHED COMPILING')
    print('TEST1')

    # After compilation (and only after), you can check some of the properties
    # of your model:
    # print("\nSatisfiable: %s" % T.satisfiable())
    # print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())  

    # print("\nVariable likelihoods:")
    # for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
    #     # Ensure that you only send these functions NNF formulas
    #     # Literals are compiled to NNF here
    #     print(" %s: %.2f" % (vn, likelihood(T, v)))
    # print()
