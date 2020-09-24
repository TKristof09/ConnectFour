#import plaidml.keras
#plaidml.keras.install_backend()

from agent import Agent
from Connect4Game import Connect4
from ai import Connect4Zero
from config import Config

config = Config()
g = Connect4(7, 6)
nnet = Connect4Zero(7, 6, g, config)

agent = Agent(nnet, g, 1000, 100, 40, 0.6)
agent.learn()