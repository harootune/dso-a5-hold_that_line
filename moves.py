# stdlib
import random
from typing import Tuple, List

# local
from line import Line


COORD_TUPLE = Tuple[int, int]  #


def generate_moves(endpoints: Tuple[COORD_TUPLE], board: List[List[str]], lines: List[Line]) -> List[Line]:
    moves = []
    for endpoint in endpoints:
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == '-':
                    coord = (i, j)
                    temp_line = Line(endpoint, coord)
                    if check_move(temp_line, lines):
                        moves.append(temp_line)
    return moves


def check_move(move, lines):
    for line in lines:
        intersect = move.check_intersection(line)
        if intersect:
            return False
    return True


def detect_wins_and_losses(moves, board, lines, endpoints, wins, losses):

    for move in moves:
        # prep
        temp_board = board.copy()
        temp_lines = lines.copy()
        temp_endpoints = endpoints.copy()
        temp_board[move.end[0]][move.end[1]] = 'X'
        temp_lines.append(move)
        for i in range(2):
            if temp_endpoints[i] == move.end:
                temp_endpoints[i] = move

        look_ahead = generate_moves(temp_endpoints, temp_board, temp_lines)
        num_look_ahead = len(look_ahead)
        if num_look_ahead == 1:
            wins.append(move)
        elif num_look_ahead == 2:
            losses.append(move)


def pick_move(endpoints, board, lines):
    moves = generate_moves(endpoints, board, lines)
    wins = []
    losses = []
    detect_wins_and_losses(moves, board, lines, endpoints, wins, losses)

    if wins:
        return random.choice(wins)
    else:
        if losses:
            if len(losses) != len(moves):
                loss_set = set(losses)
                move_set = set(moves)
                moves = list(move_set - loss_set)
        return random.choice(moves)


if __name__ == '__main__':
    test_board = [
        ['-', '-', 'X', 'X'],
        ['-', 'X', '-', '-'],
        ['X', '-', '-', '-'],
        ['X', '-', '-', '-']
    ]
    endpoints = [(0, 2), (1, 1)]
    lines = [Line((0, 3), (3, 0)), Line((3, 0), (2, 0)), Line((2,0), (1,1)), Line((0,3), (0,2))]
    moves = generate_moves(endpoints, test_board, lines)

    for move in moves:
        print()
        print(move.start)
        print(move.end)

    # move = pick_move(endpoints, test_board, lines)
    # print(move.start, move.end)





