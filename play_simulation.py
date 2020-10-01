def play_game(mode: str) -> str:
    """
    This function will be used to play the game - Hold That Line
    :param mode:
    :return: winner of the game
    """

    if mode == 'c':
        p1 = 'user'
        p2 = 'computer'
    else:
        p1 = 'player1'
        p2 = 'player2'

    return ''


if __name__ == '__main__':

    # Fetching user input for board width, height and game mode
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
        mode = input('Enter game mode (c - computer/s - server): ').lower()
        if mode not in ['c', 's']:
            print('Invalid Game Mode')
            continue
        break

    print(h, w, mode)
    winner = play_game(mode=mode)
    print(f'Game Winner is {winner}')
