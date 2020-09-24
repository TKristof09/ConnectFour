class Config():
    def __init__(self):
        self.filter_num = 128
        self.filter_size = 3
        self.residual_num = 2
        self.l2_reg = 1e-4
        self.lr = 1e-4
        self.num_iterations = 1000