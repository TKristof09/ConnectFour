import numpy as np
from tqdm import trange
import time

class Node():
    # state is the same as in the ai.py: [[own 7x6], enemy[7x6], which players turn] if board is of size 7x6
    def __init__(self, state, player):
        self.edges = []
        self.state = state
        self.current_player = player

    def is_leaf(self):
        return len(self.edges) == 0


class Edge():
    def __init__(self, in_node, out_node, prior, action):
        self.in_node = in_node
        self.out_node = out_node
        self.action = action
        self.stats = {
            "N": 0,
            "W": 0,
            "Q": 0,
            "P": prior
        }

class MCTS():
    # TODO make better constructor
    def __init__(self, game, c, ai, num_sims):
        self.root = Node(game.get_initial_board(), 1)
        self.game = game
        self.tree = []
        self.c = c
        self.ai = ai
        self.num_sims = num_sims


    def get_probs(self, temp=1):
        for _ in trange(self.num_sims):
            self.simulate()

        counts = [edge.stats["N"] for action, edge in self.root.edges]

        assert(len(counts)==7)
        if temp == 0:
            best = np.argmax(counts)
            probs = [0] * len(counts)
            probs[best] = 1
            return probs

        counts = [x ** (1.0/temp) for x in counts]
        probs = [x / float(sum(counts)) for x in counts]
        return probs
    
    def simulate(self):
        leaf, trace = self.move_to_leaf()
        self.evaluate_leaf(leaf, trace)
    

    def new_root(self, node):
        #self.tree = self.tree[node]
        self.root = node

    def add_node(self, node, parent):
        self.tree.append(node)

    def move_to_leaf(self):
        current_node = self.root
        trace = []
        while not current_node.is_leaf():
            maxQU = -9999
            board = (current_node.state[0] == 1) + ((current_node.state[1] == -1) * -1)
            nb_explor = 0
            for _, edge in current_node.edges:
                nb_explor += edge.stats['N']

            for action, edge in current_node.edges:
                U = self.c * edge.stats['P'] * np.sqrt(nb_explor) / (1 + edge.stats['N'])
                Q = edge.stats['Q']

                if Q + U > maxQU and self.game.get_valid_moves(board)[action]:
                    maxQU = Q + U
                    sim_edge = edge

            current_node = sim_edge.out_node
            trace.append(sim_edge)
        
        return (current_node, trace)
    
    def update_edges(self, leaf, value, trace):
        for edge in trace:
            edge.stats["N"] += 1
            edge.stats["W"] += value
            edge.stats["Q"] = edge.stats["W"] / edge.stats["N"]

    def evaluate_leaf(self, leaf, trace):
        probs, value = self.ai.predict(leaf.state)
        probs = probs[0]
        value = value[0][0]
        self.update_edges(leaf, value, trace)
        board = (leaf.state[0] == 1) + ((leaf.state[1] == 1) * -1)
       
        # mask invalid moves
        valids = self.game.get_valid_moves(board)
        probs = probs * valids
        sum_probs = np.sum(probs)
        if sum_probs > 0:
            probs /= sum_probs # renormalize
        else:
            print("All valid moves were masked, do workaround.")
            probs = probs + valids
            probs /= np.sum(probs)

        for action in range(self.game.get_action_size()): # only do valid actions(ones that have non 0 prob)
            if valids[action] != 0:
                b = (leaf.state[0] == 1) + ((leaf.state[1] == 1) * -1)
                new_state, next_player = self.game.get_next_state(b, action, leaf.current_player) # Probably bad
                node = Node(new_state, next_player)
                self.add_node(node, leaf)
                new_edge = Edge(leaf, node, probs[action], action)
                leaf.edges.append((action, new_edge))
            else:
                # Add a dummy edge so that the action list returned by the mcts will always have a length of action_size with 0 
                # probablilties for invalid actions
                new_edge = Edge(leaf, None, 0, action)
                new_edge.stats["Q"] = -9999
                leaf.edges.append((action, new_edge))
        
        return (value, trace)