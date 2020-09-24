
class Game():
    def __init__(self, name):
        self.name = name
        
    def get_initial_board(self):
        """
        Return:
            initial board
        """
        pass
    
    def is_over(self, board, player):
        """
        Return:
            0 if not over
            -1 if player lost
            1 if player won
            small value for draw
        """
        pass
    
    def get_action_size(self):
        """
        Return:
            number of possible actions for the game type
        """
        pass

    def get_valid_moves(self, board):
        pass
    
    def get_state(self, board, player):
        pass

    def get_next_state(self, board, action, player):
        """
        Doesn't modify current board
        Return:
            next_board: array of
                board for player 1
                board for player -1
                board indicating which players turn it is
            next_player
        """
        pass