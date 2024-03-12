import numpy as np
from tool._fixedInt import *

class fir_filter:

    def __init__(self,filter_coeff,NBTot,NBFrac):
        self.NBTot = NBTot
        self.NBFrac = NBFrac
        self.filter_coeff = filter_coeff
        self.filter_coeff_fixed = arrayFixedInt(NBTot, NBFrac,filter_coeff,'S', 'trunc', 'saturate')
        self.filter_order = len(filter_coeff)
        self.z_buffer = arrayFixedInt(NBTot, NBFrac,np.zeros(self.filter_order),'S', 'trunc', 'saturate')

        
    def get_coef(self):
        return self.filter_coeff
    
    def get_fixed_coeff(self):
        return self.filter_coeff_fixed

    def filter_symb(self, symb_input):
        self.z_buffer[0].value = float(symb_input)
        filtered_output = DeFixedInt(self.NBTot,self.NBFrac,'S', 'trunc', 'saturate')
        filtered_output.value = 0.0
        for i in range(self.filter_order):
            filtered_output.assign((self.z_buffer[i] * self.filter_coeff_fixed[i]) + filtered_output )  
        for j in range(self.filter_order-1,0,-1):
            self.z_buffer[j].assign(self.z_buffer[j - 1])  
        return filtered_output.fValue
