import requests

def play_rps(game_server_url: str, netid: str, player_key: str):

    # start a fresh session with blank cookies:
    session = requests.Session()
    session.headers = {"Connection": "close"}  # Disables HTTP Keep-Alive

    # query the available game_types to find the Hold That Line(HTL) id:
    game_search = session.get(url=game_server_url + "game-types",
                               json={"netid": netid,
                                     "player_key": player_key})

    # TODO: there's not sufficient error checking here...
    try:
        result = game_search.json()['result']
    except Exception as e:
        print('unexpected response:')
        print(game_search.content)
        print('\nfollowed by exception:' + str(e))
        return

    #TODO: Confirm name of the game again on the server
    # search for a multi-round, 2-player "Hole that line":
    game_id = False
    for g in result:
        if (g['category'] == 'HTL' or 'line' in g['fullname'].lower()) \
                and 'rounds' in g['fullname'] and g['num_players'] == 2:
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

    print(request_match.text)
    match_id = request_match.json()['result']['match_id']
