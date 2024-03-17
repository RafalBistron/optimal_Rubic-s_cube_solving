from utils import get_cube_invariant_positions, get_dicts, get_moves_to_consider, get_idas_withdraw_num
from idas import IDAs, is_found


def __pop_cube_moves_stage_0(moves, dim):  # moves to consider for stage 0
    return [move for move in moves if not (chr(48) in move or chr(48 + dim - 1) in move)]


def __pop_cube_moves_stage_1(moves, dim):  # moves to consider for stage 1
    return [move for move in moves if (chr(48) in move or chr(48 + dim - 1) in move)]


def __pop_cube_moves_stage_2(moves, dim):  # moves to consider for stage 2
    moves1 = [move for move in moves if (chr(48) in move or chr(48 + dim - 1) in move)]
    return [move for move in moves1 if not (('-' in move) and ('f' in move))]


def __pop_cube_moves_stage_3(moves, dim):  # moves to consider for stage 3
    moves1 = [move for move in moves if (chr(48) in move or chr(48 + dim - 1) in move)]
    return [move for move in moves1 if not (('-' in move) and (('f' in move) or ('r' in move)))]


def __pop_cube_moves_stage_4(moves, dim):  # moves to consider for stage 4
    moves1 = [move for move in moves if (chr(48) in move or chr(48 + dim - 1) in move)]
    return [move for move in moves1 if not ('-' in move)]


def layer_solving_IDAs(puzzle_type, initial_state, solution_state, moves,
                       max_r0, n_final_moves0, final_max_r0,
                       max_r1, n_final_moves1, final_max_r1,
                       max_r2, n_final_moves2, final_max_r2,
                       max_r3, n_final_moves3, final_max_r3,
                       max_r4, n_final_moves4, final_max_r4,
                       verbouse1=False, verbouse2=False):

    dim = initial_state.get_state_dim()
    allowed_moves = __pop_cube_moves_stage_0(moves, dim)

    if verbouse2:
        print("moves = ", moves)
        print("\n **** solving centers of the cube\n **** \n")
        print("allowed_moves = ", allowed_moves)

    puzzle_info = (puzzle_type, initial_state, solution_state, allowed_moves)
    moves_0, mid_states0 = IDAs(puzzle_info, max_r0, n_final_moves0, final_max_r0, stage=0, verbose=verbouse1)

    if verbouse2:
        print("0 moves = ", moves_0[-1])
        positions = get_cube_invariant_positions(solution_state, stage=0)
        dicts = get_dicts(positions, n_final_moves0 + 1, 0, solution_state)
        print("is 0 stage ok? : ", is_found(mid_states0[-1], solution_state, 0, positions, dicts))
        print("\n **** solving edges orientation\n **** \n")

    allowed_moves = __pop_cube_moves_stage_1(moves, dim)

    if verbouse2:
        print("allowed_moves = ", allowed_moves)

    puzzle_info = (puzzle_type, mid_states0[-1], solution_state, allowed_moves)
    moves_1, mid_states1 = IDAs(puzzle_info, max_r1, n_final_moves1, final_max_r1, stage=1, verbose=verbouse1)

    if verbouse2:
        print("1 moves = ", moves_1[-1])
        positions = get_cube_invariant_positions(solution_state, stage=1)
        dicts = get_dicts(positions, n_final_moves1 + 1, 1, solution_state)
        print("is 1 stage ok? : ", is_found(mid_states1[-1], solution_state, 1, positions, dicts))
        print("\n **** solving corners orientation\n **** \n")

    allowed_moves = __pop_cube_moves_stage_2(moves, dim)

    if verbouse2:
        print("allowed_moves = ", allowed_moves)

    puzzle_info = (puzzle_type, mid_states1[-1], solution_state, allowed_moves)
    moves_2, mid_states2 = IDAs(puzzle_info, max_r2, n_final_moves2, final_max_r2, stage=2, verbose=verbouse1)

    if verbouse2:
        print("2 moves = ", moves_2[-1])
        positions = get_cube_invariant_positions(solution_state, stage=2)
        dicts = get_dicts(positions, n_final_moves2 + 1, 2, solution_state)
        print("is 2 stage ok? : ", is_found(mid_states2[-1], solution_state, 2, positions, dicts))
        print("\n **** solving intermediate cube\n **** \n")

    allowed_moves = __pop_cube_moves_stage_3(moves, dim)

    if verbouse2:
        print("allowed_moves = ", allowed_moves)

    puzzle_info = (puzzle_type, mid_states2[-1], solution_state, allowed_moves)
    moves_3, mid_states3 = IDAs(puzzle_info, max_r3, n_final_moves3, final_max_r3, stage=3,
                                verbose=verbouse1)
    if verbouse2:
        print("3 moves = ", moves_3[-1])
        positions = get_cube_invariant_positions(solution_state, stage=3)
        dicts = get_dicts(positions, n_final_moves3 + 1, 3, solution_state)
        print("is 3 stage ok? : ", is_found(mid_states3[-1], solution_state, 3, positions, dicts))
        print("\n **** solving rest of the cube\n **** \n")

    allowed_moves = __pop_cube_moves_stage_4(moves, dim)

    if verbouse2:
        print("allowed_moves = ", allowed_moves)

    puzzle_info = (puzzle_type, mid_states3[-1], solution_state, allowed_moves)
    moves_4, solution_states = IDAs(puzzle_info, max_r4, n_final_moves4, final_max_r4, stage=4, verbose=verbouse1)
    if verbouse2:
        print("4 moves = ", moves_4[-1])
        print("is state ok? ", solution_states[-1] == solution_state)

    state = initial_state.copy()
    solution = moves_0[-1] + moves_1[-1] + moves_2[-1] + moves_3[-1] + moves_4[-1]
    if verbouse2:
        print("length of solution = ", len(solution))
        for move in solution:
            state.apply_permutation(puzzle_type, move)
        if state != solution_state:
            print("ERROR")
        else:
            print("moves are also ok")

    return solution
