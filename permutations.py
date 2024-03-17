import numpy as np


def get_inverted_permutation(permutation, length):
    inv = np.empty_like(permutation)
    inv[permutation] = np.arange(length, dtype=int)
    return inv


def get_permutation_representation(state, pos_1, pos_2, original_perm):
    """
    return one of 6 classes of relative permutation between the first and second quadruple
    of vertices at stage 3, invariant under rotation of any face by 180 degrees
    """

    perm = state.get_relative_vertex_permutations(pos_1, pos_2)
    perm_can1 = perm[get_inverted_permutation(np.array(original_perm), perm.size)]
    can_trans_tab = np.array([[0, 1, 2, 3], [1, 0, 3, 2], [2, 3, 0, 1], [3, 2, 1, 0]], dtype=int)
    ind = np.where(perm_can1 == 0)[0][0]
    return tuple(perm_can1[can_trans_tab[ind]])
