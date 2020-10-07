# stdlib
import itertools
import random
import fractions
from typing import List, Union

# local
from line import Line


class HoldThatLine:

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.endpoints = None
        self.lines = []

    def generate_moves(self) -> List[Line]:
        """
        Generate all moves possible on the current board

        :return: A list of Line objects representing possible moves
        """
        # TODO: factorial time - should be fixed
        if self.endpoints is None:
            start = None
            end = None
            coords = itertools.product(range(self.height), range(self.width))
            possible_lines = itertools.combinations(coords, r=2)
            return [Line(l[0], l[1]) for l in possible_lines]

        moves = []
        # iterate through each endpoint and every legal destination on the board
        for endpoint in self.endpoints:
            for i in range(self.height):
                for j in range(self.width):
                    coord = (i, j)
                    if coord != endpoint:  # no zero-dimensional "lines"
                        temp_line = Line(endpoint, coord)
                        if self.check_move(temp_line):  # check if move is legal
                            moves.append(temp_line)  # if so, save it
        return moves

    def check_move(self, move: Line) -> bool:
        """
        Checks if a potential move is possible given the board state

        :param move: The Line object being checked
        :return: True if the move does not intersect with any lines, else False
        """
        # is it in the bounds of the board?
        y = move.start[0], move.end[0]
        x = move.start[1], move.end[1]
        if any([coord > self.height - 1 or coord < 0 for coord in y]) \
                or any([coord > self.width - 1 or coord < 0 for coord in x]):
            return False

        # is it from an endpoint?
        if self.endpoints is not None:
            from_endpoint = False
            for endpoint in self.endpoints:
                if endpoint == move.start:
                    from_endpoint = True
                    break
            if not from_endpoint:
                return False

        # does it intersect with any line at any point besides the endpoint its drawn from?
        for line in self.lines:
            intersect = move.check_intersection(line)  # does our move intersect with the line?
            if intersect:
                return False  # if so, return False
        return True  # if not, return True

    def predict_wins_and_losses(self, moves: List[Line], wins: List[Line], losses: List[Line]) -> None:
        """
        This function evaluates a list of potential moves and identifies probable wins and losses. This allows us to
        guard against obviously dumb or suicidal play, though the computer will still often make random moves,
        and some apparent wins or losses are false positives.

        :param moves: The list of moves (Lines) to evaluate
        :param wins:  A list to output known wins to
        :param losses: A list to output known losses to
        :return: None
        """
        # Iterate through every move
        for move in moves:
            # For each move, we simulate a temporary board state in which the move has been made
            temp_board = HoldThatLine(self.height, self.width)
            temp_lines = self.lines.copy()
            temp_endpoints = self.endpoints.copy() if self.endpoints else None
            temp_board.lines = temp_lines
            temp_board.endpoints = temp_endpoints
            temp_board.make_move(move)

            # Figure out the number of moves left in the game
            seen = set()
            look_ahead = temp_board.generate_moves()
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

    def pick_move(self) -> Union[Line, None]:
        """
        Randomly chooses a legal move, filtering where possible to avoid probable losses and take probable wins.
        If no moves can be made, return None.

        :return: The chosen move, or None if no move can be made
        """
        moves = self.generate_moves()  # generate all possible, legal moves

        # predict wins and losses
        wins = []
        losses = []
        self.predict_wins_and_losses(moves, wins, losses)

        # If there is a possible win, take it every time
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
            if moves:
                return random.choice(moves)
            # if there are no moves to make, return None
            else:
                return None

    def make_move(self, move: Line) -> bool:
        if self.check_move(move):
            if self.endpoints is None:
                midpoint = (fractions.Fraction((move.start[0] + move.end[0]) / 2),
                            fractions.Fraction((move.start[1] + move.end[1]) / 2))
                for point in move.start, move.end:
                    half_move = Line(midpoint, point)
                    self.lines.append(half_move)
                self.endpoints = [move.start, move.end]
            else:
                self.lines.append(move)
                for i in range(2):
                    if self.endpoints[i] == move.start:
                        self.endpoints[i] = move.end
            return True
        else:
            return False


if __name__ == '__main__':
    pass
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
    # endpoints = [(0, 2), (1, 3)]
    # lines = [Line((1, 2), (0, 2)), Line((1, 2), (1, 1)), Line((1, 1), (2, 1)), Line((2, 1), (2, 2)),
    #          Line((2, 2), (3, 2)), Line((3, 2), (3, 3)), Line((3, 3), (1, 3))]
    # moves = generate_moves(endpoints, lines)
    # for move in moves:
    #     print()
    #     print(move.start)
    #     print(move.end)
    # move = pick_move(endpoints, lines)
    # print()
    # print(move.start, move.end)






