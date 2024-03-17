# optimal_Rubic-s_cube_solving
Solving 3x3x3 Rubic cubes by Thistlethwaite's algorithm using subgroup cosets. One of the programs used in Kaggle challenge https://www.kaggle.com/competitions/santa-2023
([Original description of Thistlethwaite's algorithm](https://www.jaapsch.net/puzzles/thistle.htm), [wikipedia page](https://en.wikipedia.org/wiki/Optimal_solutions_for_the_Rubik%27s_Cube#Thistlethwaite's_algorithm)).


The search in each coset is performed by [Iterative Deepening $A^*$ algorythm](https://en.wikipedia.org/wiki/Iterative_deepening_A*) with heuristical distance calculated using values of subgroups invariants for configurations of cube close to solution state.
