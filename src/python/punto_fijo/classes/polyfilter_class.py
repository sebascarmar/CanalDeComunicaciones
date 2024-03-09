from tool._fixedInt import *
import numpy as np

class poly_filter:
    
    def __init__(self, Nbauds, OS, filter_coefs, NB_INPUT, NBF_INPUT, NB_COEF, NBF_COEF, NB_OUTPUT, NBF_OUTPUT):
        self.Nbauds             = Nbauds
        self.OS                 = OS
        self.fifo               = arrayFixedInt(NB_INPUT, NBF_INPUT, np.zeros(Nbauds)       , signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        self.inter_products     = arrayFixedInt(NB_INPUT, NBF_INPUT, np.zeros(Nbauds)       , signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        self.filter_coef        = arrayFixedInt(NB_COEF , NBF_COEF , np.zeros(filter_coefs) , signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        
        self.fir_ph0_coef       = arrayFixedInt(8, 7, list_rc_ph0      , signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        self.fir_ph1_coef       = arrayFixedInt(8, 7, list_rc_ph1      , signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        self.fir_ph2_coef       = arrayFixedInt(8, 7, list_rc_ph2      , signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        self.fir_ph3_coef       = arrayFixedInt(8, 7, list_rc_ph3      , signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        
        self.sum                = DeFixedInt(  NB_INPUT+Nbauds-1, NBF_INPUT,    signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        self.symb_out           = DeFixedInt(  NB_OUTPUT,         NBF_OUTPUT,   signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        self.next_symb_in       = DeFixedInt(  NB_INPUT,          NBF_INPUT,    signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        self.symb_in            = DeFixedInt(  NB_INPUT,          NBF_INPUT,    signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        
        self.sum.value          = 0
        self.symb_in.value      = 0
        self.next_symb_in.value = 1
        self.symb_out.value     = 0        
        
        
    def run(self, reset, enable, control, symb_in):
        if reset:
            for i in range(self.Nbauds):
                self.fifo[i].value              = 0
                self.inter_products[i].value    = 0
            self.sum.value                      = 0
            self.symb_in.value                  = 1
            self.next_symb_in.value             = 1
            self.symb_out.value                 = 0
                     
        elif enable:
            if control == 0:                                                                # Valid
                self.symb_in.value = self.next_symb_in.value
                self.next_symb_in.value = symb_in
                
                for i in range(self.Nbauds):
                    if self.Nbauds-i == 1:
                        self.fifo[0].value = self.symb_in.value
                    else:
                        self.fifo[self.Nbauds-i-1].value = self.fifo[self.Nbauds-i-2].value
            
            for i in range(self.Nbauds):
                if control == 0:
                    if self.fifo[i].value < 0:
                        self.inter_products[i].value = -self.fir_ph0_coef[i].value
                    else:
                        self.inter_products[i].value = self.fir_ph0_coef[i].value
                elif control == 1:
                    if self.fifo[i].value < 0:
                        self.inter_products[i].value = -self.fir_ph1_coef[i].value
                    else:
                        self.inter_products[i].value = self.fir_ph1_coef[i].value
                elif control == 2:
                    if self.fifo[i].value < 0:
                        self.inter_products[i].value = -self.fir_ph2_coef[i].value
                    else:
                        self.inter_products[i].value = self.fir_ph2_coef[i].value
                elif control == 3:
                    if self.fifo[i].value < 0:
                        self.inter_products[i].value = -self.fir_ph3_coef[i].value
                    else:
                        self.inter_products[i].value = self.fir_ph3_coef[i].value
            
        self.sum.value  = 0
        
        for i in range(self.Nbauds):
            self.sum.value += self.inter_products[i].value
        
        if reset:
            self.sum.value = 0      
        
        if self.sum.value < 32:
            self.symb_out.value = self.sum.value
        
        elif self.sum.value > -32:
            self.symb_out.value = self.sum.value
        else:
            if self.sum.value > 0:
                self.symb_out.value = 32
            else:
                self.symb_out.value = -32
              