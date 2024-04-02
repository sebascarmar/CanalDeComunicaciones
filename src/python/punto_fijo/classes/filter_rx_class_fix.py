import matplotlib.pyplot as plt
import numpy as np
from classes.tool._fixedInt import *

from classes.FSE_LMS_fixed      import FSE_LMS_fixed
from classes.slicer_fixed       import slicer_fixed
# from classes.PLL_Class              import PLL_Class

class filter_rx:
    def __init__(self, FFE_taps = 51,  LMS_FIFO_delay = 0 ,LMS_step = 1e-3, 
                 Kp = 0.02, Ki = 0.00002, Lat = 0, fcr_on=0,
                 NB_SYMB_IN = 8,NBF_SYMB_IN = 6,
                 NB_FSE_O = 8,NBF_FSE_O = 6,
                 NB_SL_O = 8, NBF_SL_O = 6, 
                 NB_ERR = 8, NBF_ERR = 6, 
                 NB_LMS_STEP = 11,NBF_LMS_STEP = 10,
                 NB_FCR = 8, NBF_FCR = 6):
        
        # Asignación valores
        self.taps = FFE_taps
        self.delay_LMS = LMS_FIFO_delay
        self.taps_LMS = self.taps + self.delay_LMS

        # Fixed Point Variables
        # Simbolos de entrada - FIFO FSE - FIFO LMS - Coeficientes: S(NB_IN , NBF_IN)
        # Salida del FSE - Entrada del Slicer: S(NB_FSE_O,NBF_FSE_O)
        # Salida del Slicer: S(NB_SL_O,NBF_SL_O)
        # Error: S(NB_ERR,NBF_ERR)
        # Step LMS: S(NB_LMS_STEP,NBF_LMS_STEP) -> S(11,10) para llegar a 1e-3 aprox
        self.eq_o_I   = DeFixedInt   (NB_FSE_O   ,NBF_FSE_O   ,signedMode = 'S', roundMode='trunc', saturateMode='saturate')
        self.eq_o_Q   = DeFixedInt   (NB_FSE_O   ,NBF_FSE_O   ,signedMode = 'S', roundMode='trunc', saturateMode='saturate')
        
        self.slicer_o_I = DeFixedInt   (NB_SL_O    ,NBF_SL_O    ,signedMode = 'S', roundMode='trunc', saturateMode='saturate')
        self.slicer_o_Q = DeFixedInt   (NB_SL_O    ,NBF_SL_O    ,signedMode = 'S', roundMode='trunc', saturateMode='saturate')
        
        self.error_I    = DeFixedInt   (NB_ERR     ,NBF_ERR     ,signedMode = 'S', roundMode='trunc', saturateMode='saturate')
        self.error_Q    = DeFixedInt   (NB_ERR     ,NBF_ERR     ,signedMode = 'S', roundMode='trunc', saturateMode='saturate')
        
        # Inicialización Variables
        self.symcounter = 0
        self.phi = 0
        self.phi_conj = 0

        # Objetos --------------------------------------------------------
        # Instanciación Filtros Adaptivos
        self.u_FSE_LMS_I = FSE_LMS_fixed(FFE_taps, LMS_FIFO_delay, LMS_step,NB_SYMB_IN, NBF_SYMB_IN,NB_FSE_O, NBF_FSE_O,NB_ERR, NBF_ERR,NB_LMS_STEP, NBF_LMS_STEP)
        self.u_FSE_LMS_Q = FSE_LMS_fixed(FFE_taps, LMS_FIFO_delay, LMS_step,NB_SYMB_IN, NBF_SYMB_IN,NB_FSE_O, NBF_FSE_O,NB_ERR, NBF_ERR,NB_LMS_STEP, NBF_LMS_STEP)
        # Instanciación Slicers
        self.u_slicer_I  = slicer_fixed (NB_FSE_O, NBF_FSE_O, NB_SL_O, NBF_SL_O, NB_ERR, NBF_ERR)
        self.u_slicer_Q  = slicer_fixed (NB_FSE_O, NBF_FSE_O, NB_SL_O, NBF_SL_O, NB_ERR, NBF_ERR)
        # Instanciación FCR
        # 
        # 


    # symbI y symbQ se pasan como valor numerico y no como objeto
    def loop_rx_filter(self,symbI,symbQ):
        ## FSE --------------------------------------------
        # Shifteo
        self.u_FSE_LMS_I.Input_Shift(symbI)
        self.u_FSE_LMS_Q.Input_Shift(symbQ)

        # Filtrado
        self.eq_o_I._setValue(self.u_FSE_LMS_I.FFE_Filter())
        self.eq_o_Q._setValue(self.u_FSE_LMS_Q.FFE_Filter())

        # Downsample by 2 
        if(self.symcounter%2 == 0):
            # Compensancion salida FSE
            self.eq_fcr_I = self.FCR_conn_I(self.eq_o_I.fValue,self.eq_o_Q.fValue,self.phi)
            self.eq_fcr_Q = self.FCR_conn_Q(self.eq_o_I.fValue,self.eq_o_Q.fValue,self.phi)

            ## Slicer -----------------------------------------
            self.slicer_o_I.value = self.u_slicer_I.slicer_PAM2(self.eq_fcr_I)
            self.slicer_o_Q.value = self.u_slicer_Q.slicer_PAM2(self.eq_fcr_Q)
            
            # Calculo error
            self.error_I._setValue(self.u_slicer_I.calculate_error())
            self.error_Q._setValue(self.u_slicer_Q.calculate_error())

            ## FCR ----------------------------------------------
            # if self.symcounter > (self.fcr_on*2):
            #     self.phi = self.fcr.PLL_process(eq_fcr_I, slicer_o_I, eq_fcr_Q, slicer_o_Q)
            #     self.phi_conj = -1*self.phi

            # Compensancion error
            error_fcr_I = self.FCR_conn_I(self.error_I.fValue,self.error_Q.fValue,self.phi_conj)# El angulo va conjugado
            error_fcr_Q = self.FCR_conn_Q(self.error_I.fValue,self.error_Q.fValue,self.phi_conj)
                
            ## LMS -----------------------------------------------
            self.u_FSE_LMS_I.LMS(error_fcr_I)
            self.u_FSE_LMS_Q.LMS(error_fcr_Q)

        self.symcounter += 1

        return self.slicer_o_I.fValue, self.slicer_o_Q.fValue
     
    
    def FCR_conn_I(self,symbI,symbQ,phi):
        aux = symbI * np.cos(phi) - symbQ * np.sin(phi)
        return aux
    
    def FCR_conn_Q(self,symbI,symbQ,phi):
        aux = symbI * np.sin(phi) + symbQ * np.cos(phi)
        return aux
    

    # def get_Coef_FFE_I(self):
    #     return self.u_FSE_LMS_I.get_Coef_FFE()
    
    # def get_Coef_FFE_Q(self):
    #     return self.u_FSE_LMS_Q.get_Coef_FFE() 

    def print_COEF(self):
        self.u_FSE_LMS_I.print_Coef_FFE()
        self.u_FSE_LMS_Q.print_Coef_FFE()
        return

    def get_eq_o_I(self):
        return self.eq_o_I.fValue
    
    def get_eq_o_Q(self):
        return self.eq_o_Q.fValue
    
    
    def get_eq_fcr_I(self):
        return self.eq_fcr_I
    
    def get_eq_fcr_Q(self):
        return self.eq_fcr_Q
    

    def get_slicer_I(self):
        return self.slicer_o_I.fValue

    def get_slicer_Q(self):
        return self.slicer_o_Q.fValue
    
    
    def get_error_I(self):
        return self.error_I.fValue
    
    def get_error_Q(self):
        return self.error_Q.fValue
    
    
    # def get_error_fcr_I(self):
    #     return self.error_fcr_I
    
    # def get_error_fcr_Q(self):
    #     return self.error_fcr_Q
    
    def get_phi(self):
        return self.phi
    

    