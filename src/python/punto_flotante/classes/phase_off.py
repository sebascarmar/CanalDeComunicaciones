import numpy as np
import cmath
import random

# Teniendo como frecuencia de trabajo 100 MHz:
#           2^(N-1)*[(1024*4*T)^(-1)]
#   -para step=1   =>  f_offset = 24.3 kHz
#   -para step=2   =>  f_offset = 48.7 kHz
#   -para step=4   =>  f_offset = 97.5 kHz
#   -para step=8   =>  f_offset = 195.1 kHz
#   -para step=10  =>  f_offset = 390.2 kHz

class phase_off:

    def __init__(self):
        stepRad      = (np.pi/2)/1024
        wt           = np.arange(0., np.pi/2 + stepRad, stepRad)
        self.sin     = np.sin(wt)
        
        self.i       = 0
        self.j       = 1024
        self.semicycle_counter = 1
#        print(wt)
#        print(self.sin)
#        print(len(self.sin))


    def __cose(self, j):
        if(self.semicycle_counter == 1 or self.semicycle_counter == 4):
            return self.sin[j]
        else:
            return -1.0*self.sin[j]


    def __seno(self, i):
        if(self.semicycle_counter == 1 or self.semicycle_counter == 2):
            return self.sin[i]
        else:
            return -1.0*self.sin[i]


    def __ptr_refresh(self):
        if(self.semicycle_counter == 1 or self.semicycle_counter == 3):
            if( self.i < len(self.sin)-1 ):
                self.i += self.stepN
                self.j -= self.stepN
            else:
                self.semicycle_counter = 2 if(self.semicycle_counter==1) else 4
                self.i = 1024-self.stepN
                self.j = self.stepN
        elif(self.semicycle_counter == 2 or self.semicycle_counter == 4):
            if( self.i > 0 ):
                self.i -= self.stepN
                self.j += self.stepN
            else:
                self.semicycle_counter = 3 if(self.semicycle_counter==2) else 1
                self.i = self.stepN
                self.j = 1024-self.stepN
        else:
            print("Error con contador de ciclos")            


    def get_phase_off(self, RRC_tx_I_symb_out, RRC_tx_Q_symb_out, step):
        self.stepN = 2**(int(step)-1) if(step>0 and step<5) else 1
        self.symbI = RRC_tx_I_symb_out
        self.symbQ = RRC_tx_Q_symb_out
        
        pReal_symb_w_offset = self.symbI*self.__cose(self.j) - self.symbQ*self.__seno(self.i)
        pImag_symb_w_offset = self.symbI*self.__seno(self.i) + self.symbQ*self.__cose(self.j)
        # print(self.__cose(self.j), self.j) #Debug
       
        self.__ptr_refresh()
        
        
        return (pReal_symb_w_offset, pImag_symb_w_offset)

