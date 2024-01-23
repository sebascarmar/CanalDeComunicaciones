import numpy as np
import cmath
import random

class phase_off:

    def __init__(self):
        step             = np.pi/8
        array_aux        = [float(x) for x in range(int(-np.pi/step), int(np.pi/step) + 1)]
        
        self.titas       = [x * step for x in array_aux]
        self.i           = 0
        self.num_of_symb = 0


    def get_phase_off(self):
        i        = random.randint(0,len(self.titas))
        ejO      = cmath.exp(1j*self.titas[i])
        symb_IjQ = self.symbI + self.symbQ*1j
        
        symb_IjQ_with_off = symb_IjQ*ejO
        
        return (symb_IjQ_with_off.real, symb_IjQ_with_off.imag)

