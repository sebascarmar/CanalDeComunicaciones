import numpy as np

class fir_filter:

    def __init__(self,filter_coeff):
        self.filter_coeff = filter_coeff
        self.filter_order = len(filter_coeff)
        self.z_buffer = np.zeros(self.filter_order)

    def get_coef(self):
        return self.filter_coeff

    def filter_symb(self, symb_input):
        self.z_buffer[0] = symb_input
        filtered_output = 0
        for i in range(self.filter_order):
            filtered_output += self.z_buffer[i] * self.filter_coeff[i]
        for j in range(self.filter_order-1,0,-1):
            self.z_buffer[j] = self.z_buffer[j - 1]
        return filtered_output