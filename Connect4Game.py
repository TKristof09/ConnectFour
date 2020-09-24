from game import Game
from Connect4Logic import Board
import numpy as np

class Connect4(Game):
    def __init__(self, sizex, sizey):
        Game.__init__(self, "Connect4")
        self.board = Board(sizex, sizey)
    
    def get_initial_board(self):
        # Game starts with player 1
        # return [np.zeros([self.board.sizex, self.board.sizey]), np.zeros([self.board.sizex, self.board.sizey]), np.ones([self.board.sizex, self.board.sizey])]
        # maybe np.zeros([2, self.board.sizex, self.board.sizey]) instead of the two zero arrays
        
        # To return it as one array: 
        return np.stack((np.zeros([self.board.sizex, self.board.sizey]), np.zeros([self.board.sizex, self.board.sizey]), np.ones([self.board.sizex, self.board.sizey])))

    def is_over(self, board, player):
        b = Board.from_array(board, player)
        return b.is_over(player)
    
    def get_action_size(self):
        return self.board.sizex

    def get_valid_moves(self, board):
        return np.array([1 if x[self.board.sizey - 1] == 0 else 0 for x in board])

    def get_state(self, board, player):
        return np.stack((np.array(board == 1, dtype=int), np.array(board == -1, dtype=int), np.ones_like(board) * player))

    def get_next_state(self, board, action, player):
        b = Board.from_array(board, player)
        b.drop(action)
        b_array = b.get_as_2Darray()
        return np.stack((np.array(b_array == 1, dtype=int), np.array(b_array == -1, dtype=int), np.ones_like(b_array) * b.current_player)), b.current_player
