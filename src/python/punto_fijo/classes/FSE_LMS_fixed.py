import matplotlib.pyplot as plt
import numpy as np
from classes.tool._fixedInt import *

class FSE_LMS_fixed:
    def __init__(self,FFE_taps, LMS_FIFO_delay, LMS_step,
                 NB_SYMB_IN, NBF_SYMB_IN,
                 NB_FSE_O, NBF_FSE_O,
                 NB_ERR, NBF_ERR,
                 NB_LMS_STEP, NBF_LMS_STEP):
        
        # Asignación valores
        self.taps = int(FFE_taps)
        self.delay_LMS = int(LMS_FIFO_delay)
        self.taps_LMS = int(FFE_taps + LMS_FIFO_delay)

        # Fixed Point Variables
        # Simbolos de entrada - FIFO FSE - FIFO LMS - Coeficientes: S(NB_IN , NBF_IN)
        # Salida del FSE - Entrada del Slicer: S(NB_FSE_O,NBF_FSE_O)
        # Error: S(NB_ERR,NBF_ERR)
        # Step LMS: S(NB_LMS_STEP,NBF_LMS_STEP) -> S(11,10) para llegar a 1e-3 aprox
        self.Coef_FFE = arrayFixedInt(NB_SYMB_IN ,NBF_SYMB_IN ,np.zeros(self.taps)    ,signedMode='S', roundMode='trunc', saturateMode= 'saturate')  # Coeficientes del Ecualizador
        self.FIFO_FFE = arrayFixedInt(NB_SYMB_IN ,NBF_SYMB_IN ,np.zeros(self.taps)    ,signedMode='S', roundMode='trunc', saturateMode= 'saturate')  # FIFO del FFE
        self.FIFO_LMS = arrayFixedInt(NB_SYMB_IN ,NBF_SYMB_IN ,np.zeros(self.taps_LMS),signedMode='S', roundMode='trunc', saturateMode= 'saturate')  # FIFO del LMS
        self.LMS_Delayed =arrayFixedInt(NB_ERR +NB_LMS_STEP+ NB_SYMB_IN ,NBF_ERR +NBF_LMS_STEP+ NBF_SYMB_IN  ,np.zeros(self.taps)    ,signedMode='S', roundMode='trunc', saturateMode= 'saturate')  # FIFO del LMS retrasada
        self.correction_term = arrayFixedInt(NB_SYMB_IN ,NBF_SYMB_IN ,np.zeros(self.taps),signedMode='S', roundMode='trunc', saturateMode= 'saturate')  # Coef Correction
        self.eq_o     = DeFixedInt   (NB_FSE_O   ,NBF_FSE_O   ,signedMode = 'S', roundMode='trunc', saturateMode='saturate')
        self.eq_aux   = DeFixedInt   (NB_SYMB_IN + NB_SYMB_IN + self.taps , NBF_SYMB_IN + NBF_SYMB_IN   ,signedMode = 'S', roundMode='trunc', saturateMode='saturate')
        self.error    = DeFixedInt   (NB_ERR     ,NBF_ERR     ,signedMode = 'S', roundMode='trunc', saturateMode='saturate')
        self.step     = DeFixedInt   (NB_LMS_STEP,NBF_LMS_STEP,signedMode = 'S', roundMode='trunc', saturateMode='saturate')
        self.errorxstep = DeFixedInt   (NB_LMS_STEP+NB_ERR ,NBF_LMS_STEP+NBF_ERR ,signedMode = 'S', roundMode='trunc', saturateMode='saturate')

        # Inicialización Variables
        self.Coef_FFE[1+int((self.taps-1)/2)]._setValue(1.0)  # Inicializacion impulso
        self.eq_o._setValue(float(0))                       # Salida del filtro
        self.eq_aux._setValue(float(0))
        self.error._setValue(float(0))                             # Diferencia entre slicer y filtro
        self.step._setValue(LMS_step) 

    def Input_Shift(self,new_symbol):

        for i in range(self.taps-1):    # Shift
            self.FIFO_FFE[self.taps-i-1].value = self.FIFO_FFE[self.taps-i-2].value
        self.FIFO_FFE[0].value = new_symbol  # Agrega un nuevo elemento

        for i in range(self.taps_LMS-1):    # Shift
            self.FIFO_LMS[self.taps-i-1].value = self.FIFO_LMS[self.taps-i-2].value
        self.FIFO_LMS[0].value = new_symbol  # Agrega un nuevo elemento

        return
    
    def FFE_Filter(self):
        self.eq_aux._setValue(float(0))  

        for i in range(self.taps):
            self.eq_aux  += self.FIFO_FFE[i] * self.Coef_FFE[i]    # Multiplica la FIFO por los coeficientes y suma los productos

        self.eq_o.value = self.eq_aux.fValue
        
        # eq_o_float = 0
        # for i in range(self.taps):
        #     eq_o_float  += self.FIFO_FFE[i].fValue * self.Coef_FFE[i].fValue

        return self.eq_o.fValue
    
    def LMS(self,error):
        self.error._setValue(float(error)) 
        # Gradient Estimate
        for i in range(self.taps):
            self.LMS_Delayed[i] = self.FIFO_LMS[i+self.delay_LMS]
        
        errorxstep = self.error.fValue * self.step.fValue

        # Coeficient Update
        for i in range(self.taps):
            self.correction_term[i].value = self.LMS_Delayed[i].fValue * errorxstep
            coef_aux = self.Coef_FFE[i] + self.correction_term[i]
            self.Coef_FFE[i].value = coef_aux.fValue
        
        return
    
    def print_Coef_FFE(self):
        aux_coef = np.zeros(self.taps)
        plt.figure(figsize=[10,6])
        for i in range(self.taps):
            aux_coef[i] = self.Coef_FFE[i].fValue
        plt.plot(aux_coef)
        plt.grid(True)
        plt.title('Coeficientes LMS I')
        return self.Coef_FFE