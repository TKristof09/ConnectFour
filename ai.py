from keras.engine.topology import Input
from keras.engine.training import Model
from keras.layers import Conv2D, Activation, Add, BatchNormalization, Flatten, Dense
from keras.regularizers import l2
from keras.optimizers import Adam
from keras.models import load_model
import numpy as np
import os
import json
from config import Config

# https://applied-data.science/static/main/res/alpha_go_zero_cheat_sheet.png
class Connect4Zero():
    def __init__(self, inputx, inputy, game, config:Config):
        self.model = None
        self.inputx = inputx
        self.inputy = inputy
        self.config = config
        self.game = game
        self.build()
    
    def predict(self, state):
        state = np.expand_dims(state, axis=0)
        return self.model.predict(state)
    
    def train(self, targets):
        input_states, target_p, target_v = list(zip(*targets))
        self.model.fit(x=input_states, y=[target_p, target_v])

    def build(self):
        config = self.config
        in_x = x = Input((3, self.inputx, self.inputy)) # [[own 7x6], enemy[7x6], which player's turn] if board is of size 7x6

        x = Conv2D(config.filter_num, config.filter_size, data_format="channels_first", kernel_regularizer=l2(config.l2_reg))(x)
        # maybe batch normalization
        x = Activation("relu")(x)

        for _ in range(config.residual_num):
            x = self.build_residual_blocks(x)

        x_common = x

        # policy head
        x = Conv2D(2, 1, data_format="channels_first", kernel_regularizer=l2(config.l2_reg))(x_common)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Flatten()(x)
        policy = Dense(self.game.get_action_size(), activation="softmax", name="policy_head")(x)

        # value head
        x = Conv2D(1, 1, data_format="channels_first", kernel_regularizer=l2(config.l2_reg))(x_common)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Flatten()(x)
        x = Dense(256, activation="relu")(x)
        value = Dense(1, activation="tanh", name="value_head")(x)

        self.model = Model(in_x, [policy, value], name="connect4zero_model")
        self.model.compile(loss=["categorical_crossentropy", "mean_squared_error"], optimizer=Adam(self.config.lr))

    def build_residual_blocks(self, x):
        config = self.config
        in_x = x
        x = Conv2D(config.filter_num, config.filter_size,  padding="same", data_format="channels_first", kernel_regularizer=l2(config.l2_reg))(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        
        x = Conv2D(config.filter_num, config.filter_size,  padding="same", data_format="channels_first", kernel_regularizer=l2(config.l2_reg))(x)
        x = BatchNormalization(axis=1)(x)
        
        # Residual layer add
        x = Add()([in_x, x])
        x = Activation("relu")(x)
        return x
    
    def load_model(self, folder="checkpoint", filename="chechkpoint.h5"):
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            self.model = load_model(path)
            print(f"Loaded model from: {path}")
            return True
        else:
            print(f"Model file doesn't exist: {path}")
            return False

    def save_model(self, folder="checkpoint", filename="chechkpoint.h5"):
        path = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.mkdir(folder)
        self.model.save(path)
        print(f"Saved model to {path}")
