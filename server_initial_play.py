from ast import literal_eval
from time import sleep
import json
import re
import requests


def play_htl(game_server_url: str, netid: str, player_key: str):
    # start a fresh session with blank cookies:
    session = requests.Session()
    session.headers = {"Connection": "close"}  # Disables HTTP Keep-Alive

    # query the available game_types to find the Hold That Line(HTL) id:
    game_search = session.get(url=game_server_url + "game-types",
                              json={"netid": netid,
                                    "player_key": player_key})

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
    request_match = session.post(url=game_server_url + "game-type/{}/request-match".format(game_id),
                                 json={"netid": netid,
                                       "player_key": player_key})

    match_id = request_match.json()['result']['match_id']

    while True:
        # wait for my turn:
        while True:
            print('\n\nrequesting await-turn now.')
            await_turn = session.get(url=game_server_url + "match/{}/await-turn".format(match_id))
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

                    # TODO - write logic to fetch the move made by the other user
                    prev_move = result['history']['move']
                    try:
                        start, end = (literal_eval(x) for x in re.match(r'^((?:[^,]*,){%d}[^,]*),(.*)' % 1, prev_move).groups())
                    except SyntaxError:
                        # TODO - write logic to dispute the move
                        return

                    # TODO - write logic to update the game state with this move

                    break  # exit the while loop.
                if "Timed out" in turn_status:
                    print('PZ-server said it timed out while waiting for my turn to come up...')
                print('waiting for my turn...')
                sleep(3)
                continue
            elif result["match_status"] in ["game over", "scored, final"]:
                print('Game over?  Who won?')
                return
            elif result["match_status"] == "awaiting more player(s)":
                print('match has not started yet. sleeping a bit...')
                sleep(5)
            else:
                raise ValueError('Unexpected match_status: ' + result["match_status"])

        # Ok, now it's my turn...

        # submit my move:
        # TODO - write logic to generate a move and play here
        # TODO - if no more moves possible - call the /end-match endpoint to finish the game
        move_instruction = ''
        print("\nSending my choice of", move_instruction)

        # TODO - write the logic here to update local game state with the move

        submit_move = session.post(url=game_server_url + "match/{}/move".format(match_id),
                                   json={"move": move_instruction})
        move_result = submit_move.json()["result"]
        print(move_result)
        if move_result["match_status"] in ['']:
            print('Game over?  Who won?')
            break

        """Insert a small delay to reduce the chance of cPanel server throttling 
        this client, and to simulate the "thinking time" of a more challenging game."""
        sleep(3)

    return


if __name__ == '__main__':
    netid = 'adarsha2'
    player_key = '4dbf0de4cd09'
    game_server_url = 'https://jweible.web.illinois.edu/pz-server/games/'

    play_htl(game_server_url, netid, player_key)
