import numpy as np

from classes.adaptive_filter        import adaptive_filter
from classes.PLL_Class              import PLL_Class

class filter_rx:
    def __init__(self, FFE_taps = 51, LMS_step = 1e-3, Kp = 0.02, Ki = 0.00002, Lat = 0, fcr_on=0):
        # Instanciación Filtros Adaptivos
        self.ad_fil_I       = adaptive_filter(FFE_taps, LMS_step)
        self.ad_fil_Q       = adaptive_filter(FFE_taps, LMS_step)
        # Instanciación FCR
        self.fcr            = PLL_Class(Kp,Ki,Lat)

        self.phi            = 0
        self.phi_conj       = 0
        self.eq_o_I         = 0
        self.eq_o_Q         = 0
        self.eq_fcr_I       = 0
        self.eq_fcr_Q       = 0
        self.slicer_I       = 0
        self.slicer_Q       = 0
        self.error_I        = 0
        self.error_Q        = 0
        self.error_fcr_I    = 0
        self.error_fcr_Q    = 0
        self.symcounter     = 0
        self.fcr_on         = fcr_on


    def loop_rx_filter(self, symbI, symbQ):
        ## FSE --------------------------------------------
        # Shifteo
        self.ad_fil_I.Input_Shift(symbI)
        self.ad_fil_Q.Input_Shift(symbQ)

        # Filtrado
        eq_o_I = self.ad_fil_I.FFE_Filter()
        eq_o_Q = self.ad_fil_Q.FFE_Filter()
        
        eq_fcr_I    = 0
        eq_fcr_Q    = 0
        slicer_o_I  = 0
        slicer_o_Q  = 0
        error_I     = 0
        error_Q     = 0
        error_fcr_I = 0
        error_fcr_Q = 0

        # Downsample by 2 
        if(self.symcounter%2 == 0):
            # Compensancion salida FSE
            self.phi = 0 #FORCED
            eq_fcr_I = self.FCR_conn_I(eq_o_I, eq_o_Q, self.phi)
            eq_fcr_Q = self.FCR_conn_Q(eq_o_I, eq_o_Q, self.phi)

            ## Slicer -----------------------------------------
            slicer_o_I = self.ad_fil_I.Slicer(eq_fcr_I)
            slicer_o_Q = self.ad_fil_Q.Slicer(eq_fcr_Q)
        
            # Calculo error
            error_I = self.ad_fil_I.calculate_error(slicer_o_I, eq_fcr_I)
            error_Q = self.ad_fil_Q.calculate_error(slicer_o_Q, eq_fcr_Q)

            ## FCR ----------------------------------------------
            #if self.symcounter > (self.fcr_on*2):
            #    self.phi = self.fcr.PLL_process(eq_fcr_I, slicer_o_I, eq_fcr_Q, slicer_o_Q)
            #    self.phi_conj = -1*self.phi

            # Compensancion error
            error_fcr_I = self.FCR_conn_I(error_I, error_Q, self.phi_conj)# El angulo va conjugado
            error_fcr_Q = self.FCR_conn_Q(error_I, error_Q, self.phi_conj)
                
            ## LMS -----------------------------------------------
            self.ad_fil_I.LMS(error_fcr_I)
            self.ad_fil_Q.LMS(error_fcr_Q)

        ## Retencion de valores
        self.eq_o_I      = eq_o_I
        self.eq_o_Q      = eq_o_Q
        self.eq_fcr_I    = eq_fcr_I
        self.eq_fcr_Q    = eq_fcr_Q
        self.slicer_I    = slicer_o_I
        self.slicer_Q    = slicer_o_Q
        self.error_I     = error_I
        self.error_Q     = error_Q
        self.error_fcr_I = error_fcr_I
        self.error_fcr_Q = error_fcr_Q

        self.symcounter += 1

        return slicer_o_I, slicer_o_Q
     
    
    def FCR_conn_I(self,symbI, symbQ, phi):
        aux = symbI * np.cos(phi) - symbQ * np.sin(phi)
        return aux
    
    def FCR_conn_Q(self,symbI,symbQ,phi):
        aux = symbI * np.sin(phi) + symbQ * np.cos(phi)
        return aux
    

    def get_Coef_FFE_I(self):
        return self.ad_fil_I.get_Coef_FFE()
    
    def get_Coef_FFE_Q(self):
        return self.ad_fil_Q.get_Coef_FFE() 
    

    def get_eq_o_I(self):
        return self.eq_o_I
    
    def get_eq_o_Q(self):
        return self.eq_o_Q
    
    
    def get_eq_fcr_I(self):
        return self.eq_fcr_I
    
    def get_eq_fcr_Q(self):
        return self.eq_fcr_Q
    

    def get_slicer_I(self):
        return self.slicer_I

    def get_slicer_Q(self):
        return self.slicer_Q
    
    
    def get_error_I(self):
        return self.error_I
    
    def get_error_Q(self):
        return self.error_Q
    
    
    def get_error_fcr_I(self):
        return self.error_fcr_I
    
    def get_error_fcr_Q(self):
        return self.error_fcr_Q
    
    def get_phi(self):
        return self.phi
    

    