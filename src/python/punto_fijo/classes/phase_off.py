import matplotlib.pyplot as plt
from tool._fixedInt import *
import numpy as np
import cmath
import random


class phase_off:

    def __init__(self, NBTot, NBFrac):
        self.NBTot  = NBTot
        self.NBFrac = NBFrac
        
        ### Variables aux. para obtener 1025 muestras del 1/4 de seno
        stepRad  = (np.pi/2)/1024
        wt       = np.arange(0., np.pi/2 + stepRad, stepRad)
        sin      = np.sin(wt)
        
        ### Valores de 1/4 de seno con 1025 valores cuantizados
        self.sin = arrayFixedInt(NBTot, NBFrac, sin, 'S', 'trunc', 'saturate')
        ### Escritura de valores del seno en un archivo
        with open('cuartoDeSeno.txt', 'w') as archivo:
            for i in range(len(self.sin)):
                archivo.write(str(int(self.sin[i].fValue*(2**NBFrac))) + '\n')
        
        ### Punteros y contador para armado del seno y coseno
        self.i       = 0
        self.j       = 1024
        self.semicycle_counter = 1
        
        ### Registro para recibir los símbolos de entrada (simula carga de dato)
        reg_in_I = np.zeros(2)
        reg_in_Q = np.zeros(2)
        self.symbI = arrayFixedInt(NBTot, NBFrac, reg_in_I, 'S', 'trunc', 'saturate')
        self.symbQ = arrayFixedInt(NBTot, NBFrac, reg_in_Q, 'S', 'trunc', 'saturate')
        
        ### Productos y sumas con su respectiva resolución
        self.prodParcial_I_a = DeFixedInt(2*NBTot, 2*NBFrac, 'S', 'trunc', 'saturate') 
        self.prodParcial_I_b = DeFixedInt(2*NBTot, 2*NBFrac, 'S', 'trunc', 'saturate') 
        
        self.prodParcial_Q_a = DeFixedInt(2*NBTot, 2*NBFrac, 'S', 'trunc', 'saturate') 
        self.prodParcial_Q_b = DeFixedInt(2*NBTot, 2*NBFrac, 'S', 'trunc', 'saturate') 
        
        self.sumaPReal = DeFixedInt(2*NBTot+1, 2*NBFrac, 'S', 'trunc', 'saturate') 
        self.sumaPImag = DeFixedInt(2*NBTot+1, 2*NBFrac, 'S', 'trunc', 'saturate') 
        
        ### Variables de salida
        self.sym_I_con_off = DeFixedInt(NBTot, NBFrac, 'S', 'trunc', 'saturate') 
        self.sym_Q_con_off = DeFixedInt(NBTot, NBFrac, 'S', 'trunc', 'saturate') 

#        #### Gráficas del cuarto de seno
#        aux = []
#        for i in range(len(self.sin)):
#            aux.append(self.sin[i].fValue)
#
#        plt.figure(figsize=[6,6])
#        plt.plot(wt,aux,'bo-',linewidth=0.4,label=r'$cuantizado$')
#        plt.legend()
#        plt.grid(True)
#        plt.xlabel('Muestras Cuantizadas')
#        plt.ylabel('Magnitud')
#
#        plt.figure(figsize=[6,6])
#        plt.plot(wt,sin,'ro-',linewidth=0.4,label=r'$full res.$')
#        plt.legend()
#        plt.grid(True)
#        plt.xlabel('Muestras')
#        plt.ylabel('Magnitud')
#
#        plt.show()



    def __cose(self, j):
        if(self.semicycle_counter == 1 or self.semicycle_counter == 4):
            return self.sin[j]
        else:
            menos = DeFixedInt(2, 1, 'S', 'trunc', 'saturate')
            menos.value = -1.0

            complemento = DeFixedInt(self.NBTot, self.NBFrac, 'S', 'trunc', 'saturate')
            complemento.assign( menos*self.sin[j] )
            return complemento


    def __seno(self, i):
        if(self.semicycle_counter == 1 or self.semicycle_counter == 2):
            return self.sin[i]
        else:
            menos = DeFixedInt(2, 1, 'S', 'trunc', 'saturate')
            menos.value = -1.0
            
            complemento = DeFixedInt(self.NBTot, self.NBFrac, 'S', 'trunc', 'saturate')
            complemento.assign( menos*self.sin[i] )
            
            return complemento


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


    # Teniendo como frecuencia de trabajo 100 MHz:
    #     f = 2^(N-1)*[(1024*4*T)^(-1)]
    #     f =   step *[(1024*4*T)^(-1)] (4 por los 4 cuartos del seno)
    #   -para step=1   =>  f_offset = 24.3 kHz
    #   -para step=2   =>  f_offset = 48.7 kHz
    #   -para step=4   =>  f_offset = 97.5 kHz
    #   -para step=8   =>  f_offset = 195.1 kHz
    #   -para step=10  =>  f_offset = 390.2 kHz

    def get_phase_off(self, RRC_tx_I_symb_out, RRC_tx_Q_symb_out, N):
        # Puede recorrer de a 1, 2 , 4 u 8 muestras
        self.stepN = 2**(int(N)-1) if(N>0 and N<5) else 1
        
        ### Desplaza y carga el símb. para la comp. en el siguiente clock
        ### El símb. en i=1 asemeja a la carga del reg. con el dato del clock anterior
        self.symbI          = np.roll(self.symbI, 1)
        self.symbI[0].value = RRC_tx_I_symb_out # Si lo que recibo es float64
        #self.symbI[0].assign( RRC_tx_I_symb_out) # Si lo que recibo es FixedInt
        
        ### Desplaza y carga el símb. para la comp. en el siguiente clock
        ### El símb. en i=1 asemeja a la carga del reg. con el dato del clock anterior
        self.symbQ          = np.roll(self.symbQ, 1)
        self.symbQ[0].value = RRC_tx_Q_symb_out  # Si lo que recibo es float64
        #self.symbQ[0].assign( RRC_tx_Q_symb_out) # Si lo que recibo es FixedInt
        #print("symI:",self.symbI, "\t symQ:", self.symbQ) #Debug
        
        ### Las operaciones a realizar son:
        ### symbI_des = I*cos[wt]-Q*sen[wt]
        ### symbQ_des = I*sen[wt]+Q*cos[wt]
        
        ### Productos parciales
        self.prodParcial_I_a.assign(self.symbI[1]*self.__cose(self.j))
        self.prodParcial_I_b.assign(self.symbQ[1]*self.__seno(self.i))
        #print("prodI_a:",self.prodParcial_I_a, "\t prodI_b:", self.prodParcial_I_b) #Debug
        
        self.prodParcial_Q_a.assign(self.symbI[1]*self.__seno(self.i))
        self.prodParcial_Q_b.assign(self.symbQ[1]*self.__cose(self.j))
        #print("prodQ_a:",self.prodParcial_Q_a, "\t prodQ_b:", self.prodParcial_Q_b) #Debug
        
        ### Sumas
        self.sumaPReal.assign(self.prodParcial_I_a - self.prodParcial_I_b)
        
        self.sumaPImag.assign(self.prodParcial_Q_a + self.prodParcial_Q_b)
        #print("sumaFinI:",self.sumaPReal, "\t sumaFinQ:", self.sumaPImag) #Debug
        
        ### Saturación y trucnado final
        self.sym_I_con_off.assign(self.sumaPReal)
        
        self.sym_Q_con_off.assign(self.sumaPImag)
        #print("symIdes:",self.sym_I_con_off, "\t symQdes:", self.sym_Q_con_off) #Debug
       
        ### Actualiza punteros hacia la tabla del seno
        self.__ptr_refresh()
        
        
        return (self.sym_I_con_off.fValue, self.sym_Q_con_off.fValue)
        #return (sym_I_con_off, sym_Q_con_off) # Si lo que retorna es fixedPoint

