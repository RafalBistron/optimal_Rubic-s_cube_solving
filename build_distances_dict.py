import numpy as np
from utils import get_cube_invariant_positions, get_current_allowed_moves, get_moves_to_consider, get_idas_withdraw_num, get_inverse_move, get_dicts
from permutations import get_permutation_representation


def update_dicts(positions, dicts, state, n_moves, stage):
    """
    Update the dictionary for {value subgroup invariants: how far from solution they first appear}
    {state: n_new} - new pair to add to consider
    """

    for i in range(len(positions)):
        pos = positions[i]
        dic = dicts[i]

        if (4 > stage > 0) and i > 0:
            elements = state.translate(pos, nested=True)
        else:
            elements = state.translate(pos, nested=False)

        if elements in dic.keys():
            old_el_len = dic[elements]
            if old_el_len > n_moves:
                dic.update({elements: n_moves})
        else:
            dic.update({elements: n_moves})

    if stage == 3:
        key = state.get_orientation(positions[4:6])
        try:
            old_key_len = dicts[6][key]
            if old_key_len > n_moves:
                dicts[6].update({key: n_moves})
        except KeyError:
            dicts[6].update({key: n_moves})

        key_tuple = get_permutation_representation(state, positions[4], positions[5], original_perm=dicts[7][0])
        try:
            old_key_tuple_len = dicts[7][key_tuple]
            if old_key_tuple_len > n_moves:
                dicts[7].update({key_tuple: n_moves})
        except KeyError:
            dicts[7].update({key_tuple: n_moves})

    return dicts


def build_distances_dict(puzzle_info, n_final_moves, stage, verbose=False):
    """
    For each inviariant relevant at given stage build a dictionary:
    {value of subgroup invariants: how far from solution they first appear}
    For now only for cubes
    """

    puzzle_type, _, solution_state, allowed_moves = puzzle_info

    max_r = n_final_moves
    positions = get_cube_invariant_positions(solution_state, stage)
    dicts = get_dicts(positions, n_final_moves + 1, stage, solution_state)

    move_table = np.zeros(n_final_moves).astype(int) - 1
    withdraw_table = np.zeros(n_final_moves).astype(int)
    depth = -1
    move_sequence = []

    curr_allowed_moves = get_current_allowed_moves(allowed_moves, move_sequence, depth, max_r, stage)
    current_state = solution_state.copy()

    if verbose:
        print("****\n building dict \n ****")

    while True:
        n_moves = len(move_sequence)

        if get_moves_to_consider(move_sequence, depth, stage):
            dicts = update_dicts(positions, dicts, current_state, n_moves, stage)

        if depth <= 0 and verbose:
            print("move[0] = ", move_table[0])

        # increment last generator
        if depth == max_r - 1 and move_table[depth] < len(curr_allowed_moves) - 1:

            current_state.apply_permutation(puzzle_type, get_inverse_move(move_sequence[-1]))

            move_table[depth] += 1
            move_sequence[depth] = curr_allowed_moves[move_table[depth]]
            current_state.apply_permutation(puzzle_type, move_sequence[-1])

            if move_table[depth] == len(curr_allowed_moves) - 1:
                withdraw_table[depth] = 1
            else:
                withdraw_table[depth] = 0

                # withdraw and increment previous generator
        elif depth == max_r - 1:
            withdraw_num = get_idas_withdraw_num(withdraw_table, depth)
            if withdraw_num == max_r:
                break
            else:
                # withdraw
                depth = depth - withdraw_num
                move_table[depth + 1:] = -1
                withdraw_table[depth:] = 0
                for i in range(withdraw_num):
                    current_state.apply_permutation(puzzle_type, get_inverse_move(move_sequence[-1]))
                    move_sequence.pop()

                # increment generator
                current_state.apply_permutation(puzzle_type, get_inverse_move(move_sequence[-1]))
                move_table[depth] += 1
                curr_allowed_moves = get_current_allowed_moves(allowed_moves, move_sequence, depth, max_r, stage)
                if move_table[depth] == len(curr_allowed_moves) - 1:
                    withdraw_table[depth] = 1
                move_sequence[depth] = curr_allowed_moves[move_table[depth]]
                current_state.apply_permutation(puzzle_type, move_sequence[-1])

        # add new generator
        else:
            depth += 1
            move_table[depth] = 0
            curr_allowed_moves = get_current_allowed_moves(allowed_moves, move_sequence, depth, max_r, stage)
            if len(curr_allowed_moves) > 1:
                withdraw_table[depth] = 0
            else:
                withdraw_table[depth] = 1
            move_sequence.append(curr_allowed_moves[move_table[depth]])
            current_state.apply_permutation(puzzle_type, move_sequence[-1])

    return dicts
