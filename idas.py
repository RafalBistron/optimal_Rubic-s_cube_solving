import numpy as np
from utils import get_idas_withdraw_num, get_moves_to_consider, get_current_allowed_moves, get_cube_invariant_positions, get_inverse_move
from build_distances_dict import build_distances_dict
from permutations import get_permutation_representation


def get_heuristic_distance(state, positions, dicts, stage):
    """
    Using dictionaries {value of subgroup invariants: how far from solution they first appear
    gives lower bound for how far the state is from solution_state coset for now only for cubes
    """
    dist = 0
    for i in range(len(positions)):
        pos = positions[i]
        dic = dicts[i]

        elements = ""
        if (4 > stage > 0) and i > 0:
            elements = state.translate(pos, nested=True)
        else:
            elements = state.translate(pos, nested=False)

        if elements in dic.keys():
            tmp_dist = dic[elements]
        else:
            tmp_dist = dic[""]  # default argument, case not save
        if tmp_dist > dist:
            dist = tmp_dist

    if stage == 3:
        key = state.get_orientation(positions[4:6])

        if key in dicts[6].keys():
            tmp_dist = dicts[6][key]
        else:
            tmp_dist = dicts[6][2]  # default argument, case not save
        if tmp_dist > dist:
            dist = tmp_dist

        key_tuple = get_permutation_representation(state, positions[4], positions[5], original_perm=dicts[7][0])
        if key_tuple in dicts[7].keys():
            tmp_dist = dicts[7][key_tuple]
        else:
            tmp_dist = dicts[7][tuple()]  # default argument, case not save
        if tmp_dist > dist:
            dist = tmp_dist

    return dist


def is_found(state, solution_state, stage, positions, dicts):
    """"
    return true if state and solution_state are in the same coset
    """
    if stage == 4:
        return state == solution_state

    elif stage == 3:
        if not state.get_substate(positions[0]) == solution_state.get_substate(positions[0]):
            return False
        for i in range(1, 6):
            if not state.get_nested_substate(positions[i]) == solution_state.get_nested_substate(positions[i]):
                return False
        if not state.get_orientation(positions[4:6]) == solution_state.get_orientation(positions[4:6]):
            return False
        perm1 = get_permutation_representation(state, positions[4], positions[5], original_perm=dicts[7][0])
        perm2 = get_permutation_representation(solution_state, positions[4], positions[5], original_perm=dicts[7][0])
        if not perm1 == perm2:
            return False
        return True

    elif 3 > stage > 0:
        for i in range(len(positions)):
            if i == 0:
                if not state.get_substate(positions[i]) == solution_state.get_substate(positions[i]):
                    return False
            elif not state.get_nested_substate(positions[i]) == solution_state.get_nested_substate(positions[i]):
                return False
        return True

    elif stage == 0:
        return state.get_substate(positions[0]) == solution_state.get_substate(positions[0])


def IDAs(puzzle_info, max_r, n_final_moves, final_max_r, stage=4, verbose=False):
    """
    Finds short path (sequence of moves) form initial_state to solution_state cosets
    puzzle_info - puzzle_type, initial_state, solution_state, allowed_moves
    max_r - first guess for necessary number of moves
    n_final_moves - number of moves form solution_state coset we consider to estimate distance
    final_max_r - maximal number of moves to consider
    stage - which coset we are currently considering
    """
    puzzle_type, initial_state, solution_state, allowed_moves = puzzle_info
    solutions_tab = []
    solutions_states_tab = []

    if stage == 4:
        max_r = (max_r // 2) * 2
        n_final_moves = (n_final_moves // 2) * 2
        final_max_r = (final_max_r // 2) * 2

    move_table = np.zeros(final_max_r).astype(int) - 1
    depth = -1
    move_sequence = []
    withdraw_table = np.zeros(final_max_r).astype(int)
    curr_allowed_moves = get_current_allowed_moves(allowed_moves, move_sequence, depth, max_r, stage)

    current_state = initial_state.copy()

    new_max_r = np.infty
    falg_go_deeper = True

    dicts = build_distances_dict(puzzle_info, n_final_moves, stage, verbose=verbose)
    positions = get_cube_invariant_positions(solution_state, stage)

    if verbose:
        print("****\n solving puzzle \n ****")

    if is_found(current_state, solution_state, stage, positions, dicts):  # if the starting state is a solution
        print("moves = ", move_sequence)
        print("number of moves = ", depth + 1)

        solutions_tab.append(move_sequence.copy())
        solutions_states_tab.append(current_state.copy())
        return solutions_tab, solutions_states_tab

    while True:
        if depth <= 0 and verbose:
            print("move[0] = ", move_table[0])

        est_path_lenght = depth + get_heuristic_distance(current_state, positions, dicts, stage)

        # increment last generator
        if est_path_lenght > max_r - 1 and move_table[depth] < len(curr_allowed_moves) - 1:
            current_state.apply_permutation(puzzle_type, get_inverse_move(move_sequence[-1]))
            move_table[depth] += 1
            move_sequence[depth] = curr_allowed_moves[move_table[depth]]
            current_state.apply_permutation(puzzle_type, move_sequence[-1])
            new_max_r = min(new_max_r, est_path_lenght)
            if move_table[depth] == len(curr_allowed_moves) - 1:
                withdraw_table[depth] = 1
            else:
                withdraw_table[depth] = 0

        # withdraw and increment previous generator
        elif est_path_lenght > max_r - 1:
            new_max_r = min(new_max_r, est_path_lenght)
            withdraw_num = get_idas_withdraw_num(withdraw_table, depth)
            if withdraw_num == depth + 1:
                if new_max_r >= final_max_r or not falg_go_deeper:
                    break
                else:
                    max_r = int(new_max_r) + 1
                    if stage == 4:
                        max_r += 1
                    print("max_r = ", max_r)
                    move_table = np.zeros(final_max_r).astype(int) - 1
                    depth = -1
                    move_sequence = []
                    withdraw_table = np.zeros(final_max_r).astype(int) - 1
                    curr_allowed_moves = get_current_allowed_moves(allowed_moves, move_sequence, depth, max_r, stage)
                    current_state = initial_state.copy()
                    new_max_r = np.infty
            else:
                # withdraw
                depth = depth - withdraw_num
                move_table[depth + 1:] = -1  # ?
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

        # save solution and update minimal necessary number of generators
        if get_moves_to_consider(move_sequence, depth, stage) and is_found(current_state, solution_state, stage,
                                                                           positions, dicts):
            if verbose:
                if stage == 4:
                    print(current_state == solution_state)
                print("moves = ", move_sequence)
                print("number of moves = ", depth + 1)

            solutions_tab.append(move_sequence.copy())
            solutions_states_tab.append(current_state.copy())
            if depth == 0 or depth == -1:
                break

            # to not look for longer solutions,
            max_r = depth
            move_table = move_table[:max_r + 1]
            withdraw_table = withdraw_table[:max_r + 1]

            # withdraw, but not in the standard way
            # since the number of stapes changed, the number of allowed moves at previous stage may also change
            move_table[depth + 1:] = -1
            withdraw_table[depth:] = 0

            to_withdraw = True
            while to_withdraw:
                depth -= 1
                move_table[depth + 1] = -1
                withdraw_table[depth] = 0
                current_state.apply_permutation(puzzle_type, get_inverse_move(move_sequence[-1]))
                move_sequence.pop()
                curr_allowed_moves = get_current_allowed_moves(allowed_moves, move_sequence, depth, max_r, stage)

                if stage == 2 and depth > 0 and ('f' in move_sequence[depth]):
                    if move_sequence[depth] == move_sequence[depth - 1]:
                        to_withdraw = True

                elif stage == 3 and depth > 0 and (('f' in move_sequence[depth]) or ('r' in move_sequence[depth])):
                    if move_sequence[depth] == move_sequence[depth - 1]:
                        to_withdraw = True

                elif stage == 4 and depth > 0 and move_sequence[depth] == move_sequence[depth - 1]:
                    to_withdraw = True

                elif move_sequence[depth] in curr_allowed_moves:
                    move_table[depth] = len(curr_allowed_moves) - 1 - curr_allowed_moves[::-1].index(
                        move_sequence[depth])
                    to_withdraw = (move_table[depth] == (len(curr_allowed_moves) - 1))
                else:
                    if len(curr_allowed_moves) == 0:
                        to_withdraw = True
                    else:
                        to_withdraw = False
                        move_table[depth] = -1

            current_state.apply_permutation(puzzle_type, get_inverse_move(move_sequence[-1]))
            move_table[depth] += 1
            if move_table[depth] == len(curr_allowed_moves) - 1:
                withdraw_table[depth] = 1

            move_sequence[depth] = curr_allowed_moves[move_table[depth]]
            current_state.apply_permutation(puzzle_type, move_sequence[-1])
            falg_go_deeper = False

    return solutions_tab, solutions_states_tab
