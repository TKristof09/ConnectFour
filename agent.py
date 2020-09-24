from MCTS import MCTS
from game import Game
from arena import Arena
import numpy as np
from random import shuffle
from tqdm import trange

class Agent():
    def __init__(self, nnet, game, num_iter, num_episodes, arena_games_num, acception_threshold):
        self.nnet = nnet
        self.pnet = self.nnet.__class__(nnet.inputx, nnet.inputy, nnet.game, nnet.config)
        self.game = game
        self.mcts = MCTS(game, 1, self.nnet, 1600)
        self.train_data = []
        self.num_iter = num_iter
        self.num_ep = num_episodes
        self.arena_games_num = arena_games_num
        self.acception_threshold = acception_threshold
    
    def play_episode(self):
        train_data = []
        board = self.game.get_initial_board()
        board = (board[0] == 1) + ((board[1] == -1) * -1)
        self.current_player = 1

        while True:
            input_board = self.game.get_state(board, self.current_player)
            probs = self.mcts.get_probs()
            train_data.append([input_board, probs, self.current_player])

            action = np.random.choice(len(probs), p=probs)
            state, self.current_player = self.game.get_next_state(board, action, self.current_player)
            board = (state[0] == 1) + ((state[1] == 1) * -1)
            self.mcts.new_root(self.mcts.root.edges[action][1].out_node)
            result = self.game.is_over(board, self.current_player)
            if result != 0:
                return [(x[0], x[1], result*((-1)**(x[2] != self.current_player))) for x in train_data]
    
    def learn(self):
        iters = trange(self.num_iter)
        iters.set_description("Iterations")
        for i in iters:
            iter_train_exemples = []
            eps = trange(self.num_ep)
            eps.set_description("Episodes")
            for _ in eps:
                self.mcts = MCTS(self.game, 1, self.nnet, 1600)
                iter_train_exemples += self.play_episode()
            self.train_data.append(iter_train_exemples)

            train_data = []
            for ep in self.train_data:
                train_data.extend(ep)
            shuffle(train_data)
            
            # train new neural net and keep copy of the old one
            self.nnet.save_model(folder=self.game.name, filename="temp.h5")
            self.pnet.load_model(folder=self.game.name, filename="temp.h5")
            pmcts = MCTS(self.game.init(), 1, self.pnet, 1600)
            self.nnet.train(train_data)
            nmcts = MCTS(self.game.init(), 1, self.nnet, 1600)

            # Make the two nnets play vs each other and choose new one if it won > threshold
            arena = Arena(lambda x: np.argmax(pmcts.get_probs(x, temp=0)),
                          lambda x: np.argmax(nmcts.get_probs(x, temp=0)), self.game)
            pwins, nwins, draws = arena.play_games(self.arena_games_num)
            
            accepted = float(nwins) / (pwins + nwins + draws) > self.acception_threshold
            if accepted:
                self.nnet.save_model(folder=self.game.name, filename="checkpoint_" + i + ".h5")
                self.nnet.save_model(folder=self.game.name, filename="best.h5")
            else:
                self.nnet.load_model(folder=self.game.name, filename="temp.h5")