from copy import copy, deepcopy
import numpy as np
from sympy.combinatorics.permutations import Permutation
from permutations import get_inverted_permutation
from puzzle_dictionary import puzzle_moves


class State:
    def __init__(self, state):
        self.state = state
        print("New state create!")

    def translate(self, pos, nested: bool):
        """ convert state to string"""
        if nested:
            return "".join((self.get_nested_substate(pos)))
        return "".join((self.get_substate(pos)))

    def apply_permutation(self, puzzle_type: str, move_name: str):
        """ Apply the given permutation to the initial state and return the final state"""
        permutation_table = puzzle_moves.loc[move_name, "permutation"]
        initial_state = copy(self.state)
        self.state = [initial_state[i] for i in permutation_table]

    def get_state_dim(self):
        return int(np.sqrt(len(self.state) / 6))

    def get_rectangle_substate(self, nested_pos):
        return [[self.state[p] for p in pos] for pos in nested_pos]

    def get_substate(self, pos):
        return [self.state[p] for p in pos]

    def get_nested_substate(self, nested_pos):
        elements = sorted(self.get_rectangle_substate(nested_pos))
        return [e for el in elements for e in el]

    def get_orientation(self, positions):
        pos = [p for po in positions for p in po]
        elements_rec = self.get_rectangle_substate(pos)
        ids = sorted(range(len(elements_rec)), key=lambda i: elements_rec[i])
        return Permutation(ids).parity()

    def get_relative_vertex_permutations(self, pos_1, pos_2):
        """
        return relative permutation between the first and second quadruple of vertices at stage 3
        """
        elements_rec1 = self.get_rectangle_substate(pos_1)
        elements_rec2 = self.get_rectangle_substate(pos_2)
        length = len(elements_rec1)
        ids_1 = sorted(range(length), key=lambda i: elements_rec1[i])
        ids_2 = sorted(range(length), key=lambda i: elements_rec2[i])

        return get_inverted_permutation(ids_1, length)[ids_2]

    def __eq__(self, other):
        return self.state == other.state

    def copy(self):
        cls = self.__class__
        new_state = cls.__new__(cls)
        new_state.state = deepcopy(self.state)
        return new_state
