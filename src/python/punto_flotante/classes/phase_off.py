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


    def get_phase_off(self, RRC_tx_I_symb_out, RRC_tx_Q_symb_out):
        self.symbI = RRC_tx_I_symb_out
        self.symbQ = RRC_tx_Q_symb_out
        
        # Realiza una selección aleatoria del index i cada 4 símbolos recibidos.
        if(self.num_of_symb%4 == 0):
            self.num_of_symb = 0
            self.i           = random.randint(0,len(self.titas))
        
        self.num_of_symb += 1
        print(self.num_of_symb, self.i, self.titas[self.i])
        
        # Creación del factor e^(jwt) o, en ptras palabras, e^(jTita).
        ejO = cmath.exp(1j*self.titas[self.i])
        
        # Símbolo proveniente del filtro en su forma rectangular.
        symb_IjQ = self.symbI + self.symbQ*1j
        
        # Generación del desfasaje del símbolo.
        symb_IjQ_with_off = symb_IjQ * ejO
        
        return (symb_IjQ_with_off.real, symb_IjQ_with_off.imag)

