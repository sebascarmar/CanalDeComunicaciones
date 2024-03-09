import matplotlib.pyplot as plt
import numpy as np

class adaptive_filter:
    def __init__(self, FFE_taps = 51, LMS_step = 1e-3):
        self.taps       = FFE_taps
        self.step       = LMS_step
        self.delay_LMS  = 0
        self.taps_LMS   = self.taps + self.delay_LMS
        self.alpha_leak = 0                                 # Correccion tap leakeage

        self.Coef_FFE = np.zeros(self.taps)                  # Coeficientes del Ecualizador
        self.Coef_FFE[1+int((self.taps-1)/2)] = 1.0          # Inicializacion impulso

        self.FIFO_FFE = np.zeros(self.taps)                  # FIFO del FFE
        self.FIFO_LMS = np.zeros(self.taps_LMS)             # FIFO del LMS

        self.eq_o       = 0                                  # Salida del filtro
        self.slicer_o   = 0                                  # Salida del Slicer
        self.error      = 0                                  # Diferencia entre slicer y filtro
        self.symcounter = False

    def Input_Shift(self, new_symbol):
        self.FIFO_FFE    = np.roll(self.FIFO_FFE, 1)          # Shiteo a la derecha
        self.FIFO_FFE[0] = new_symbol                        # Agrega un nuevo elemento
        self.FIFO_LMS    = np.roll(self.FIFO_LMS, 1)          # Shiteo a la derecha
        self.FIFO_LMS[0] = new_symbol                        # Agrega un nuevo elemento
        return
    
    def FFE_Filter(self):
        eq_o = np.dot(self.FIFO_FFE, self.Coef_FFE)      # Multiplica la FIFO por los coeficientes y suma los productos
        return eq_o
    
    def Slicer(self,eq_o):
        if(eq_o >= 0):                                       # Mapea el símbolo segun un umbral
            return 1
        else:
            return -1
        
    def calculate_error(self,slicer_o,eq_o):
        return slicer_o - eq_o                               # Diferencia entre valor recibido y simbolo estimado
    
    def LMS(self, error):
        # Gradient Estimate
        LMS_Delayed = self.FIFO_LMS[self.delay_LMS:self.taps_LMS]
        grad = error * LMS_Delayed
        # Coeficient Update
        self.Coef_FFE = self.Coef_FFE*(1-self.step*self.alpha_leak) + self.step*grad
        return
    
#    def loop_adaptive_filter(self,new_symbol):
#        # Shifteo
#        self.FFE_Shift(new_symbol)
#        # Filtrado
#        eq_o = self.FFE_Filter()
#
#        self.symcounter = ~self.symcounter
#        error = 0
#        slicer_o = 0
#
#        # Downsample by 2 
#        if(self.symcounter):
#            # Slicer
#            slicer_o = self.Slicer(eq_o)
#        
#            # Calculo error
#            error = self.calculate_error(slicer_o,eq_o)            
#
#        # LMS
#        self.LMS(error)
#
#        self.eq_o = eq_o
#        self.slicer_o = slicer_o
#        self.error = error
#
#        return slicer_o

    def get_eq_o(self):
        return self.eq_o
    
    def get_slicer_o(self):
        return self.slicer_o
    
    def get_error(self):
        return self.error
    
    def get_Coef_FFE(self):
        return self.Coef_FFE
    
    def FCR_conn_I(self, symbI, symbQ, phi):
        aux = symbI * np.cos(phi) - symbQ * np.sin(phi)
        return aux
    
    def FCR_conn_Q(self,symbI,symbQ,phi):
        aux = symbI * np.sin(phi) + symbQ * np.cos(phi)
        return aux
    