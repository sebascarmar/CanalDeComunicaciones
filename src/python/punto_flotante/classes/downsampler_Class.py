import numpy as np

class downsampler:
    
    def __init__(self, OS):
        self.fifo  = np.zeros(OS)
        
    def insert_symbol(self, symb_in):
        self.fifo = np.roll(self.fifo, 1)
        self.fifo[0] = symb_in
        
    def get_symbol(self, phase):
        return self.fifo[phase]