import numpy as np
import cmath
import random

class phase_off:

    def __init__(self, fs, Delta_f):
        self.step        = Delta_f/fs

        array_aux        = [float(x) for x in range(0, int(2*np.pi/self.step) + 1)]
        self.titas       = [x * self.step for x in array_aux]

        self.i           = -1
        self.num_of_symb = 0


    def get_phase_off(self, RRC_tx_I_symb_out, RRC_tx_Q_symb_out):
        self.symbI = RRC_tx_I_symb_out
        self.symbQ = RRC_tx_Q_symb_out
        
        # Incrementa en 1 el index i cada 4 símbolos recibidos.
        if(self.num_of_symb%4 == 0):
            self.num_of_symb = 0
            if( self.i < len(self.titas)-1 ):
                self.i += 1
            else:
                self.i  = 0
        
        self.num_of_symb += 1
        
        # Creación del factor e^(jwt) o, en ptras palabras, e^(jTita).
        ejO = cmath.exp(1j*self.titas[self.i])
        
        # Símbolo proveniente del filtro en su forma rectangular.
        symb_IjQ = self.symbI + self.symbQ*1j
        
        # Generación del desfasaje del símbolo.
        symb_IjQ_with_off = symb_IjQ * ejO
        
        return (symb_IjQ_with_off.real, symb_IjQ_with_off.imag)

