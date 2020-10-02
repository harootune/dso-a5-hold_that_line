# local
import argparse
import gamestate
import line


class Opponent:

    def receive_move(self, move: line.Line):
        raise NotImplementedError()

    def return_move(self, game: gamestate.HoldThatLine):
        raise NotImplementedError()


class HumanOpponent(Opponent):

    def receive_move(self, move: line.Line):
        if move is None:
            print('Computer has won.')
        else:
            print(f'Computer last move: {(move.start, move.end)}')

    def return_move(self, game: gamestate.HoldThatLine):
        legal_moves = game.generate_moves()
        if not legal_moves:
            print('You have won.')
            return None

        print(f'Current lines: {[(l.start, l.end) for l in game.lines]}')
        print(f'Current endpoints: {game.endpoints}')
        print(f'Possible moves: {[(l.start, l.end) for l in legal_moves] if game.endpoints else "Any"}')

        while True:
            # input start
            while True:
                try:
                    start = input('Enter move start point (comma-separated - height,width): ').strip().split(',')
                    i = int(start[0])
                    j = int(start[1])
                    start = i, j
                    if game.endpoints is not None:
                        if start not in game.endpoints:
                            print('Start coordinate must be a current endpoint. Please input again.')
                            continue
                except ValueError:
                    print('Invalid start coordinate. Please input again.')
                    continue
                break

            # input end
            while True:
                try:
                    end = input('Enter move end point (comma-separated - height,width): ').strip().split(',')
                    i = int(end[0])
                    j = int(end[1])
                    end = i, j
                    if end == start:
                        print('End coordinate cannot be same as start coordinate. Please input again.')
                        continue
                except ValueError:
                    print('Invalid end coordinate. Please input again.')
                    continue
                break

            try:
                move = line.Line(start, end)
            except ValueError:
                print('Input could not be evaluated as a line. Please input again.')
                continue

            return move


def main(mode='human'):
    opponent = None
    if mode == 'human':
        print('Human input selected.')
        opponent = HumanOpponent()

        while True:
            try:
                h, w = tuple(int(x.strip()) for x in input('Enter Board Dimensions (comma-separated - height,width): ').split(','))
                if w <= 0 or h <= 0:
                    print('Invalid Board Dimensions')
                    continue
            except ValueError:
                print('Invalid Board Dimensions')
                continue
            break

        while True:
            try:
                first = input('Would you like to move first? (y, yes, n, no): ')
                first = first.lower().strip()
                if first in ['y', 'yes']:
                    comp_turn = False
                elif first in ['n', 'no']:
                    comp_turn = True
                else:
                    print('Invalid input.')
                    continue
            except ValueError:
                print('Invalid input.')
                continue
            break

    elif mode == 'network':
        print('Network behavior not yet implemented.')
        exit()
    else:
        raise ValueError(f'Invalid mode "{mode}"')

    game = gamestate.HoldThatLine(h, w)
    in_play = True
    while in_play:
        if comp_turn:
            move = game.pick_move()
            if move is None:
                in_play = False
            else:
                game.make_move(move)
                opponent.receive_move(move)
        else:
            valid = False
            while not valid:
                move = opponent.return_move(game)
                if move is not None:
                    valid = game.check_move(move) or move is None
                else:
                    valid = True

                if not valid:
                    print('Invalid move. Prompting opponent for correction.')  # TODO: Figure out what happens if the network gives us a bad move

            if move is None:
                in_play = False
            else:
                game.make_move(move)

        if in_play:
            comp_turn = not comp_turn

    print(f'{"Computer" if comp_turn else "Opponent"} wins.')


if __name__ == '__main__':
    desc = 'Simulate a game of Hold-That-Line, either over the network or with human input'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('mode', type=str, choices=['human', 'network'],
                        help='Whether to play with human or network input')
    args = parser.parse_args()
    main(mode=args.mode)


    # # Fetching user input for board width, height and game mode
    # while True:
    #     try:
    #         h, w = tuple(int(x.strip()) for x in input('Enter Board Dimensions (comma-separated - height,width): ').split(','))
    #         if w <= 0 or h <= 0:
    #             print('Invalid Board Dimensions')
    #             continue
    #     except ValueError:
    #         print('Invalid Board Dimensions')
    #         continue
    #     break
    #
    # while True:
    #     mode = input('Enter game mode (c - computer/s - server): ').lower()
    #     if mode not in ['c', 's']:
    #         print('Invalid Game Mode')
    #         continue
    #     break
    #
    # print(h, w, mode)
    # winner = play_game(mode=mode)
    # print(f'Game Winner is {winner}')