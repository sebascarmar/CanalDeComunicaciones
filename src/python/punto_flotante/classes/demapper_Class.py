import numpy as np

class demapper:
    
    def __init__(self, M):
        self.M = M
        
    def get_bit(self, symbol):
        if self.M == 4:
            if symbol >= 0:
                return 1
            else:
                return 0