# local
import argparse
import gamestate
import json
import line
import re
import requests

from time import sleep
from ast import literal_eval


class Opponent:

    def receive_move(self, move: line.Line):
        raise NotImplementedError()


    def return_move(self, game: gamestate.HoldThatLine):
        raise NotImplementedError()


    def dispute_move(self, move: line.Line):
        raise NotImplementedError()


class NetworkOpponent:

    def __init__(self, game_server_url, netid, player_key):
        self.request_session = requests.Session()
        self.request_session.headers = {"Connection": "close"}
        self.game_server_url = game_server_url
        self.netid = netid
        self.player_key = player_key
        self.match_id = -1
        self.turn = 1


    def receive_move(self, move: line.Line):
        this_pc_move_str = f"{str(move.start)},{str(move.end)}"
        self.request_session.post(url=self.game_server_url + f"match/{self.match_id}/move", json={'move': this_pc_move_str})
        self.turn += 1


    def return_move(self, game: gamestate.HoldThatLine):
        # wait for my turn:
        while True:
            print('\n\nrequesting await-turn now.')
            await_turn = self.request_session.get(url=self.game_server_url + f"match/{self.match_id}/await-turn")
            print(await_turn.text)
            try:
                result = await_turn.json()["result"]
            except json.decoder.JSONDecodeError:
                print('Unexpected Server Response. Not valid JSON.')
                sleep(15)
                continue  # try again after a wait.  Is this a temporary server problem or a client bug?

            print('Update on previous move(s): ' + json.dumps(result))
            if result["match_status"] == "in play":
                turn_status = result["turn_status"]
                if turn_status == "your turn":
                    # Yea! There was much rejoicing.

                    # Fetching move made by other user
                    prev_move = result['history'][0]
                    start, end = (literal_eval(x) for x in re.match(r'^((?:[^,]*,){%d}[^,]*),(.*)' % 1, prev_move).groups())
                    move = line.Line(start, end)
                    print(f'Opponent Last Move : {(start, end)}')
                    return move

                if "Timed out" in turn_status:
                    print('PZ-server said it timed out while waiting for my turn to come up...')
                print('waiting for my turn...')
                sleep(3)
                continue
            elif result["match_status"] in ["game over", "scored, final"]:
                players = self.fetch_game_players()
                winner = next(player for player in players if player['win_lose_draw'] == 'W')['netid']
                print(f'Game Over! Winner is : {winner}')
                return
            elif result["match_status"] == "awaiting more player(s)":
                print('match has not started yet. sleeping a bit...')
                sleep(5)
            elif result['match_status'] == 'under review':
                # TODO - /resolve-disputed-turn logic
                print('move is in review!')
                sleep(5)
            else:
                raise ValueError('Unexpected match_status: ' + result["match_status"])


    def fetch_game_history(self):
        try:
            return self.request_session.get(url=self.game_server_url + f"match/{self.match_id}/history").json()['result']['history']
        except Exception:
            return []


    def fetch_game_players(self):
        return self.request_session.get(url=self.game_server_url + f"match/{self.match_id}/history").json()['result']['players']


    def setup(self):
        # query the available game_types to find the Hold That Line(HTL) id:
        game_search = self.request_session.get(url=self.game_server_url + "game-types",
                                               json={"netid": self.netid,
                                                     "player_key": self.player_key})

        try:
            result = game_search.json()['result']
        except Exception as e:
            print('unexpected response:')
            print(game_search.content)
            print('\nfollowed by exception:' + str(e))
            return

        # Fetching Game ID
        game_id = False
        for g in result:
            if (g['category'] == 'hold_that_line' or 'line' in g['fullname'].lower()) and g['num_players'] == 2:
                game_id = g['id']

        if game_id:
            print('Found matching game-type: ', game_id)
        else:
            print('Game not available now.')
            exit()

        # Now request a single match of that game type:
        request_match = self.request_session.post(url=self.game_server_url + "game-type/{}/request-match"
                                                  .format(game_id),
                                                  json={"netid": self.netid,
                                                        "player_key": self.player_key})

        self.match_id = request_match.json()['result']['match_id']


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

        return self.make_this_pc_move(game)


    @staticmethod
    def make_this_pc_move(game: gamestate.HoldThatLine):  # This should be in human opponent
        while True:

            # Input Move
            while True:
                try:
                    move_input = input('Enter move points (comma-separated - (x1,y1),(x2,y2)): ')
                    start, end = (literal_eval(x) for x in re.match(r'^((?:[^,]*,){%d}[^,]*),(.*)' % 1, move_input).groups())
                    if isinstance(start, tuple) and isinstance(end, tuple):  # isinstance
                        if game.endpoints is not None:
                            if start not in game.endpoints:
                                print('Start coordinate must be a current endpoint. Please input again.')
                                continue
                        elif end == start:
                            print('End coordinate cannot be same as start coordinate. Please input again.')
                            continue
                    else:
                        print('Invalid Input Type - Please use tuples!')
                except SyntaxError:
                    print('Invalid Move Input')
                    continue
                break

            try:
                move = line.Line(start, end)
            except ValueError:
                print('Input could not be evaluated as a line. Please input again.')
                continue

            return move


    def dispute_move(self, move: line.Line):
        print('Move disputed.')


def main(mode='human'):
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

        game = gamestate.HoldThatLine(h, w)

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
        netid = 'adarsha2'
        player_key = 'b8587ad6ce78'
        game_server_url = 'https://jweible.web.illinois.edu/pz-server/games/'
        opponent = NetworkOpponent(game_server_url, netid, player_key)
        opponent.setup()
        h = w = 4

        game = gamestate.HoldThatLine(h, w)

        game_history = opponent.fetch_game_history()
        if game_history:
            for move in sorted(game_history, key=lambda x: x['turn']):
                start, end = (literal_eval(x) for x in
                              re.match(r'^((?:[^,]*,){%d}[^,]*),(.*)' % 1, move['move']).groups())
                move = line.Line(start, end)
                game.make_move(move)
                opponent.turn += 1

        players = opponent.fetch_game_players()
        for player in players:
            if player['netid'] == netid:
                order = player['player_order']
                break

        is_odd = order % 2  # TODO: Pass on logic
        if opponent.turn % 2:
            comp_turn = is_odd
        else:
            comp_turn = not is_odd

    else:
        print('no')
        exit()

    # TODO: Determine in-play based on board state
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
                    opponent.dispute_move(move)

            if move is None:
                in_play = False
            else:
                game.make_move(move)

        if in_play:
            comp_turn = not comp_turn

    print(f'{"Computer" if comp_turn else "Opponent"} wins.')


if __name__ == '__main__':
    desc = 'Simulate a game of Hold-That-Line, either over the network or with human input'
    # parser = argparse.ArgumentParser(description=desc)
    # parser.add_argument('mode', type=str, choices=['human', 'network'],help='Whether to play with human or network input')
    # args = parser.parse_args()
    # main(mode=args.mode)
    main(mode='network')
