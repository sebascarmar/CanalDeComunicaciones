import numpy as np
import cmath
import random
import matplotlib.pyplot as plt

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
        self.wt      = np.arange(0., np.pi/2 + stepRad, stepRad)
        self.sin     = np.sin(self.wt)
        
        self.i       = 0
        self.j       = 1024
        self.semicycle_counter = 1
        
        self.cnt     = 0
        
#        self.list_aux = []
        
        #### Gráficas del cuarto de seno
        #aux = []
        #for i in range(len(self.sin)):
        #    aux.append(self.sin[i].fValue)

        #plt.figure(figsize=[6,6])
        #plt.plot(wt,aux,'bo-',linewidth=0.4,label=r'$cuantizado$')
        #plt.legend()
        #plt.grid(True)
        #plt.xlabel('Muestras Cuantizadas')
        #plt.ylabel('Magnitud')

#        plt.figure(figsize=[6,6])
#        plt.plot(self.wt,self.sin,'ro-',linewidth=0.4, label=r'$full res.$')
#        plt.legend()
#        plt.grid(True)
#        plt.xlabel('Muestras')
#        plt.ylabel('Magnitud')
#
#        plt.show()
#        print(self.wt)
#        print(self.sin)
#        print(len(self.sin))
#        
#        input('Press enter to finish: ')
#        plt.close()


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
        #print(self.__cose(self.j), self.j) #Debug
       
        if self.cnt%4 == 0:
            self.__ptr_refresh()
        self.cnt += 1
        #self.list_aux.append(self.__seno(self.i))
        
        return (pReal_symb_w_offset, pImag_symb_w_offset)

#    def plot_sin(self):
#        plt.figure(figsize=[6,6])
#        plt.plot(self.wt, self.list_aux,'ro-',linewidth=0.4, label=r'$full res.$')
#        plt.legend()
#        plt.grid(True)
#        plt.xlabel('Muestras')
#        plt.ylabel('Magnitud')
#
#        plt.show()
#        input('Press enter to finish: ')
#        plt.close()
    
    def get_fixed_off(self, RRC_tx_I_symb_out, RRC_tx_Q_symb_out, index):
        self.titas = [np.pi/8, np.pi/4, np.pi/2, np.pi]
        
        ejO      = cmath.exp(1j*self.titas[index])
        symb_IjQ = RRC_tx_I_symb_out + RRC_tx_Q_symb_out*1j
        
        symb_IjQ_with_fix_off = symb_IjQ*ejO
        
        return (symb_IjQ_with_fix_off.real, symb_IjQ_with_fix_off.imag)

#offset_gen =  phase_off() # Instancia objeto que genera desplazamiento de fase.
