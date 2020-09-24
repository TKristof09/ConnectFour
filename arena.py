class Arena():
    def __init__(self, player1, player2, game):
        self.player1 = player1
        self.player2 = player2
        self.game = game

    def play_game(self):
        board = self.game.get_initial_board()
        current_player = 1
        players = [self.player1, None, self.player2]
        while self.game.is_over(board, current_player):
            action = players[current_player + 1](board, current_player)
            valids = self.game.get_valid_moves(board)

            assert valids[action] > 0

            state, current_player = self.game.get_next_state(board, action, current_player)
            board = (state[0] == 1) + ((state[1] == 1) * -1)
        
        return self.game.is_over(board, 1)
    
    def play_games(self, num):
        """
        Play num games where player 1 starts half of the time and player 2 half of the time
        Return:
            games won by 1
            games won by 2
            games draw
        """
        num = int(num / 2)
        onewon = 0
        twowon = 0
        draw = 0

        for _ in range(num):
            result = self.play_game()
            if result == 1:
                onewon += 1
            elif result == -1:
                twowon += 1
            else:
                draw +=1
        
        self.player1, self.player2 = self.player2, self.player1

        for _ in range(num):
            result = self.play_game()
            if result == -1:
                onewon += 1
            elif result == 1:
                twowon += 1
            else:
                draw +=1
        
        return onewon, twowon, draw