# stdlib
import random
from typing import Tuple, List

# local
from line import Line


def generate_moves(endpoints: List[Tuple[int, int]], lines: List[Line]) -> List[Line]:
    """
    Generate all moves possible on the current board

    :param endpoints: Current endpoints of the line on the board
    :param lines: The line segments currently on the board
    :return: A list of Line objects representing possible moves
    """
    moves = []
    # iterate through each endpoint and every legal destination on the board
    for endpoint in endpoints:
        for i in range(4):
            for j in range(4):
                coord = (i, j)
                if coord != endpoint:  # no zero-dimensional "lines"
                    temp_line = Line(endpoint, coord)
                    if check_move(temp_line, lines):  # check if move is legal
                        moves.append(temp_line)  # if so, save it
    return moves


def check_move(move: Line, lines: List[Line]) -> bool:
    """
    Checks if a potential move is possible given the board state

    :param move: The Line object being checked
    :param lines: The Lines already on the board
    :return: True if the move does not intersect with any lines, else False
    """
    # iterate through every line
    for line in lines:
        intersect = move.check_intersection(line)  # does our move intersect with the line?
        if intersect:
            return False  # if so, return False
    return True  # if not, return True


def predict_wins_and_losses(moves: List[Line], endpoints: List[Tuple[int, int]], lines: List[Line],
                           wins: List[Line], losses: List[Line]) -> None:
    """
    This function evaluates a list of potential moves, given a current board state, and roughly predicts any 1-move wins
    or 2-move losses. This allows us to guard against obviously dumb or suicidal play, though the computer will
    still often make random moves, and some apparent wins or losses are false positives.

    :param moves:  The list of moves (Lines) to evaluate
    :param endpoints: The current endpoints of the board
    :param lines:  The current Lines on the board
    :param wins:  A list to output known wins to
    :param losses: A list to output known losses to
    :return: None
    """
    # Iterate through every move
    for move in moves:
        # For each move, we simulate a temporary board state in which the move has been made
        temp_lines = lines.copy()
        temp_endpoints = endpoints.copy()
        temp_lines.append(move)
        for i in range(2):
            if temp_endpoints[i] == move.start:
                temp_endpoints[i] = move.end

        # Figure out the number of moves left in the game
        seen = set()
        look_ahead = generate_moves(temp_endpoints, temp_lines)
        look_ahead_clean = []
        for temp_move in look_ahead:
            # We are concerned with the number of spaces left to move to, so filter duplicates
            if temp_move.end not in seen:
                seen.add(temp_move.end)
                look_ahead_clean.append(temp_move)
        num_look_ahead = len(look_ahead_clean)

        # if our potential move leaves only one space to move to afterward, its likely a win
        if num_look_ahead == 1:
            wins.append(move)
        # if there are no or only two moves left to make, it may be a loss and should be avoided if possible
        elif num_look_ahead in [0, 2]:
            losses.append(move)


def pick_move(endpoints: List[Tuple[int, int]], lines: List[Line]) -> Line:
    """
    Randomly chooses a legal move, filtering where possible to avoid guaranteed losses and take guaranteed wins

    :param endpoints: The current endpoints of the board
    :param lines: The current lines on the board
    :return: The chosen move
    """
    moves = generate_moves(endpoints, lines)  # generate all possible, legal moves

    # predict wins and losses
    wins = []
    losses = []
    predict_wins_and_losses(moves, endpoints, lines, wins, losses)

    # If there is a guaranteed win, take it every time
    if wins:
        return random.choice(wins)  # there may be more than one, in which case the choice is random
    else:
        # if there are losses and not all next moves are losses, filter out the losses
        # if all next moves are losses, no filtering occurs
        if losses:
            if len(losses) != len(moves):
                loss_set = set(losses)
                move_set = set(moves)
                moves = list(move_set - loss_set)
        # make a random choice after loss filtering
        # early in a game, this is effectively random play
        return random.choice(moves)


if __name__ == '__main__':
    # 5 losses and 1 win scenario
    # endpoints = [(0, 2), (1, 1)]
    # lines = [Line((0, 3), (3, 0)), Line((3, 0), (2, 0)), Line((2, 0), (1, 1)), Line((0, 3), (0, 2))]
    # moves = generate_moves(endpoints, lines)
    # for move in moves:
    #     print()
    #     print(move.start)
    #     print(move.end)
    # move = pick_move(endpoints, lines)
    # print()
    # print(move.start, move.end)

    # 1 loss scenario
    endpoints = [(0, 2), (1, 3)]
    lines = [Line((1, 2), (0, 2)), Line((1, 2), (1, 1)), Line((1, 1), (2, 1)), Line((2, 1), (2, 2)),
             Line((2, 2), (3, 2)), Line((3, 2), (3, 3)), Line((3, 3), (1, 3))]
    moves = generate_moves(endpoints, lines)
    for move in moves:
        print()
        print(move.start)
        print(move.end)
    move = pick_move(endpoints, lines)
    print()
    print(move.start, move.end)






