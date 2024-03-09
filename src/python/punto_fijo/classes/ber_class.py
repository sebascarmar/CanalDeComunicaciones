from tool._fixedInt import *
import numpy as np

class ber:
    
    def __init__(self, Lfifo):
        self.Lfifo                      = Lfifo
        self.fifo                       = arrayFixedInt(1, 0, np.zeros(self.Lfifo), signedMode='U', roundMode='trunc', saturateMode='saturate')
        
        self.final_ber                  = 0
        self.flag_aligning              = 1
        self.flag_aligned               = 0
        
        self.ptr_fifo                   = 0
        self.bit_tx                     = DeFixedInt(1, 0, signedMode='U', roundMode='trunc', saturateMode= 'saturate')
        self.bit_rx                     = DeFixedInt(1, 0, signedMode='U', roundMode='trunc', saturateMode= 'saturate')
        self.symb_rx                    = DeFixedInt(8, 7, signedMode='S', roundMode='trunc', saturateMode= 'saturate')
        
        self.counter_bits_aligning      = DeFixedInt(64, 0, signedMode='U', roundMode='trunc', saturateMode= 'saturate')
        self.iterations_counter         = DeFixedInt(64, 0, signedMode='U', roundMode='trunc', saturateMode= 'saturate')
        self.actual_acum_err            = DeFixedInt(64, 0, signedMode='U', roundMode='trunc', saturateMode= 'saturate')
        
        self.min_acum_err               = DeFixedInt(64, 0, signedMode='U', roundMode='trunc', saturateMode= 'saturate')
        self.ptr_min_err                = DeFixedInt(64, 0, signedMode='U', roundMode='trunc', saturateMode= 'saturate')
        
        self.acum_err_aligned           = DeFixedInt(64, 0, signedMode='U', roundMode='trunc', saturateMode= 'saturate')
        self.total_bits                 = DeFixedInt(64, 0, signedMode='U', roundMode='trunc', saturateMode= 'saturate')
        
        self.counter_bits_aligning.value = 0
        self.actual_acum_err.value       = 0
        self.min_acum_err.value          = 511
        self.ptr_min_err.value           = 0
        self.acum_err_aligned.value      = 0
        self.total_bits.value            = 0
        self.iterations_counter.value    = 0
        self.final_ber                   = -1
        
        
    def run(self, reset, enable, control, bit_tx, symb_rx):
        
        if reset:
            self.final_ber                      = -1
            self.flag_aligning                  = 1
            self.flag_aligned                   = 0
            self.ptr_fifo                       = 0
            self.counter_bits_aligning.value    = 0
            self.actual_acum_err.value          = 0
            self.min_acum_err.value             = 511
            self.ptr_min_err.value              = 0
            self.acum_err_aligned.value         = 0
            self.total_bits.value               = 0
            self.iterations_counter.value       = 0
            self.fifo                           = arrayFixedInt(1, 0, np.zeros(self.Lfifo), signedMode='U', roundMode='trunc', saturateMode='saturate')
            self.bit_tx.value                   = 0
            self.bit_rx.value                   = 0
            self.symb_rx.value                  = 0
            
        elif enable:
            
            self.bit_tx.value  = bit_tx
            self.symb_rx.value = symb_rx
            
            if symb_rx >= 0:                                                                    #De-mapper
                self.bit_rx.value = 0
            else:
                self.bit_rx.value = 1
                
            if control == 0:                                                                    # Valid
                for i in range(self.Lfifo-1):
                    self.fifo[self.Lfifo-i-1].value = self.fifo[self.Lfifo-i-2].value
                self.fifo[0].value = self.bit_tx.value
                
                if self.flag_aligning:                                                          # If is in aligning stage, searching best position
                    self.counter_bits_aligning.value += 1

                    if self.fifo[self.ptr_fifo].value ^ self.bit_rx.value:                      #Error/OK
                        self.actual_acum_err.value += 1

                    if self.counter_bits_aligning.value == self.Lfifo:                          # Changing position
                        if self.actual_acum_err.value < self.min_acum_err.value:
                             self.min_acum_err.value = self.actual_acum_err.value
                             self.ptr_min_err.value  = self.ptr_fifo

                        self.actual_acum_err.value          = 0
                        self.ptr_fifo                      += 1
                        self.counter_bits_aligning.value    = 0
                        self.iterations_counter.value      += 1

                    if self.iterations_counter.value >= self.Lfifo:                             # Transition to next stage
                        self.flag_aligning = 0
                        self.flag_aligned  = 1
                        
                if self.flag_aligned:                                                           # If is in aligned stage, counting BER
                    self.total_bits.value += 1

                    if self.fifo[self.ptr_min_err.value].value ^ self.bit_rx.value:
                        self.acum_err_aligned.value += 1

                    if self.total_bits.value > 0:        
                        self.final_ber = self.acum_err_aligned.value / self.total_bits.value    # BER