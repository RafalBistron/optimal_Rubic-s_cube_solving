import numpy as np


def get_inverse_move(move):
    """
    Returns move inverse to the given move
    """
    if list(move)[0] == "-":
        return ''.join(list(move[1:]))
    return "-" + move


def get_idas_withdraw_num(withdraw_table, depth):
    """
    Returns the number of moves to withdraw in depth first like IDA^* search
    """
    new_table = withdraw_table[:depth+1][::-1]
    counter = 1
    while counter < depth+1 and  new_table[counter] == 1:
        counter +=1
    return counter


def get_current_allowed_moves(allowed_moves, move_sequence, depth, max_r, stage):
    """
    Returns a list of moves allowed at the given situation
    """
    curr_allowed_moves = allowed_moves.copy()

    if depth <= 0:
        return curr_allowed_moves

    inverse_move = get_inverse_move(move_sequence[depth - 1])
    if inverse_move in curr_allowed_moves:
        curr_allowed_moves.remove(inverse_move)

    prev_move = move_sequence[depth - 1]

    if '2' in prev_move and (depth != max_r - 1 or stage < 3):
        prev_move_type = list(prev_move)[-2]
        curr_allowed_moves = [m for m in curr_allowed_moves if not ((prev_move_type in m) and ('0' in m))]

    if ((depth > 1 and prev_move == move_sequence[depth - 2]) or (
            "-" in prev_move)) and prev_move in curr_allowed_moves:
        curr_allowed_moves.remove(prev_move)
    elif stage > 1:
        if ('f' in prev_move) or (stage == 3 and ('r' in prev_move)) or stage == 4:
            return [prev_move]

    if stage == 2 and depth == max_r - 1:
        curr_allowed_moves = [move for move in curr_allowed_moves if not ('f' in move)]
    elif stage == 3 and depth == max_r - 1:
        curr_allowed_moves = [move for move in curr_allowed_moves if ('d' in move)]
    elif stage == 4 and depth == max_r - 1:
        curr_allowed_moves = []

    return curr_allowed_moves


def get_moves_to_consider(move_sequence, depth, stage):
    """
    Tells whether move_sequence consists only of combinations of moves allowed at given stage
    """
    if stage == 2 and depth > -1:
        curr_move = move_sequence[depth]
        if depth == 0 and ('f' in curr_move):
            return False
        prev_move = move_sequence[depth - 1]
        if ('f' in curr_move) and prev_move != curr_move:
            return False

    if stage == 3 and depth > -1:
        curr_move = move_sequence[depth]
        if depth == 0 and (('f' in curr_move) or ('r' in curr_move)):
            return False
        prev_move = move_sequence[depth - 1]
        if (('f' in curr_move) or ('r' in curr_move)) and prev_move != curr_move:
            return False

    if stage == 4 and depth > -1:
        curr_move = move_sequence[depth]
        if depth == 0:
            return False
        prev_move = move_sequence[depth - 1]
        if prev_move != curr_move:
            return False

    return True


def get_cube_invariant_positions(state, stage):
    dim = state.get_state_dim()

    center_pos = []
    for i in range(6):
        for j in range(dim):
            for k in range(dim):
                if (0 < j < dim - 1) and (0 < k < dim - 1):
                    center_pos.append(i * (dim ** 2) + j * dim + k)

    if stage == 0:
        return [center_pos]

    elif stage == 1:
        # designed for cubes 3x3x3
        edges_pos = np.array([[12, 41], [14, 21], [30, 23], [32, 39],
                              [3, 37], [1, 28], [5, 19], [7, 10],
                              [48, 43], [52, 34], [50, 25], [46, 16]], dtype=int)
        return [center_pos, edges_pos]

    elif stage == 2:
        # designed for cubes 3x3x3
        chosen_edges_pos = np.array([[12, 41], [14, 21], [30, 23], [32, 39]], dtype=int)
        other_edges_pos = np.array([[7, 10], [5, 19], [1, 28], [3, 37], [46, 16], [50, 25], [52, 34], [48, 43]],
                                   dtype=int)
        corners_pos = np.array([[15, 45, 44],
                                [24, 47, 17],
                                [11, 8, 18],
                                [38, 6, 9],
                                [33, 53, 26],
                                [42, 51, 35],
                                [20, 2, 27],
                                [29, 0, 36]], dtype=int)

        return [center_pos, chosen_edges_pos, other_edges_pos, corners_pos]

    elif stage == 3:
        # designed for cubes 3x3x3
        chosen_edges1_pos = np.array([[12, 41], [14, 21], [30, 23], [32, 39]], dtype=int)
        chosen_edges2_pos = np.array([[7, 10], [1, 28], [46, 16], [52, 34]], dtype=int)
        chosen_edges3_pos = np.array([[3, 37], [5, 19], [48, 43], [50, 25]], dtype=int)

        corners1_pos = np.array([[15, 45, 44],
                                 [11, 8, 18],
                                 [33, 53, 26],
                                 [29, 0, 36]], dtype=int)

        corners2_pos = np.array([[38, 6, 9],
                                 [24, 47, 17],
                                 [20, 2, 27],
                                 [42, 51, 35]], dtype=int)

        return [center_pos, chosen_edges1_pos, chosen_edges2_pos, chosen_edges3_pos, corners1_pos, corners2_pos]

    elif stage == 4:

        # return the positions of vertices, edges and centers
        corners_pos = []
        edges_pos = []

        for i in range(6):
            for j in range(dim):
                for k in range(dim):
                    if (j == 0 or j == dim - 1) and (k == 0 or k == dim - 1):
                        corners_pos.append(i * (dim ** 2) + j * dim + k)
                    elif (j == 0 or j == dim - 1) or (k == 0 or k == dim - 1):
                        edges_pos.append(i * (dim ** 2) + j * dim + k)

    return [center_pos, edges_pos, corners_pos]


def get_dicts(positions, moves, stage, solution_state):
    """
    "Initialize" the dictionary {value subgroup invariants: how far from solution they first appear}
    """
    dicts = [{"": moves} for _ in positions]

    if stage == 3:
        dicts.append({2: moves})
        key_perm = solution_state.get_relative_vertex_permutations(positions[4], positions[5])
        dicts.append({tuple(): moves, 0: key_perm})

    return dicts
