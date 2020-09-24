import numpy as np

class Column():
    def __init__(self, size, array=None):
        if array is None:
            self.column = [0 for i in range(size)]
            self.highest = 0
        else:
            if len(array) < size:
                print("Column array lenght less than size, adding zeroes to the end")
                self.column = array
                self.column += [0 for i in range(size - len(array))]
            elif len(array) > size:
                print("Column array length greater than size, removing extra")
                self.column = [array[i] for i in range(size)]
            else:
                self.column = array
            self.highest = len(self.column.nonzero()[0])
    
    def drop(self, player):
        self.column[self.highest] = player
        self.highest += 1
    
    def get_array(self):
        return self.column
    
    def check_column(self):
        arr = self.get_array()
        c = 0
        for r in range(len(arr) - 1):
            if arr[r] == arr[r + 1] and arr[r] != 0:
                c += 1
            else:
                c = 0
            if c == 3:
                print("win in column")
                return True
        return False

class Board():
    # TODO switch to numpy arrays
    def __init__(self, sizex, sizey, pieces=None, current_player=1):
        if pieces is None:
            self.board = [Column(sizey) for i in range(sizex)]
            self.sizex = sizex
            self.sizey = sizey
        else:
            self.board = [Column(len(c), array=c) for c in pieces]
            self.sizex = len(self.board)
            self.sizey = len(self.board[0].get_array())
        
        self.current_player = current_player
    
    @classmethod
    def from_array(cls, array, current_player):
        return cls(len(array), len(array[0]), pieces=array, current_player=current_player)

    def _check_diag(self, startx, starty, double=False):
        # diagonal towards the right
        arr = self.get_as_2Darray()
        count = 0
        if startx < self.sizex / 2 or double:
            r = starty
            c = startx
            while r in range(starty, self.sizey - 1) and c in range(startx, self.sizex - 1):
                if arr[c][r] == arr[c + 1][r + 1] and arr[c][r] != 0:
                    count += 1
                else:
                    count = 0
                if count == 3:
                    print("win diagonal right: {}, {}".format(startx, starty))
                    return True
                r += 1
                c += 1

        # diagonal towards the left
        elif startx >= self.sizex / 2 or double:
            r = min(startx, self.sizey)
            c = 0
            while r in range(starty, min(startx, self.sizey)) and c in range(startx):
                if arr[c][r] == arr[c + 1][r - 1] and arr[c][r] != 0:
                    count += 1
                else:
                    count = 0
                if count == 3:
                    print("win diagonal left: {}, {}".format(startx, starty))
                    return True
                r -= 1
                c += 1
        return False


    def _check_row(self, row):
        count = 0
        for c in range(self.sizex - 1):
            if self.board[c].get_array()[row] == self.board[c + 1].get_array()[row] \
                and self.board[c].get_array()[row] != 0:
                count += 1
            else:
                count = 0
            if count == 3:
                print("win in row {}".format(row + 1))
                return True
        return False

    def _check_board(self):
        for c in self.board:
            if c.check_column():
                return 1

        for r in range(self.sizey):
            if self._check_row(r):
                return 1

        # number of possible diagonals = (columns - 3 + rows - 4) * 2
        for row in range(self.sizey):
            if row >= self.sizey - 3:
                continue
            for col in range(self.sizex):
                double = False
                if self.sizex - col > 3 and col > 3:
                    double = True
                if self._check_diag(col, row, double=double):
                    return 1

        return 0


    def drop(self, column):
        assert(column < self.sizex)
        #print("Column overflows, please enter a digit between 0 and {}".format(self.sizex))
            
        self.board[column].drop(self.current_player)
        self.current_player = -self.current_player
        return self.current_player
    
    # Converts board to 2D array [column][row]
    def get_as_2Darray(self):
        return np.array([self.board[i].get_array() for i in range(len(self.board))])
    
    def is_over(self, player):
        # TODO return small number for draw
        return self._check_board() * ((-1) ** (self.current_player == player))

    def __str__(self):
        s = ""
        arr = self.get_as_2Darray()
        for r in range(self.sizey):
            s = " ".join([str(arr[i][r]) for i in range(self.sizex)]) + "\n" + s
        return s
