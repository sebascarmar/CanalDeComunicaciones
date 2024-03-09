from tool._fixedInt import *
import numpy as np

class downsampler:
    
    def __init__(self, OS):
        self.OS                     = OS
        self.fifo                   = arrayFixedInt(8, 7, np.zeros(OS), signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        self.symb_out               = DeFixedInt(8, 7,                  signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        
        self.next_symb_in           = DeFixedInt(8, 7,                  signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        self.symb_in                = DeFixedInt(8, 7,                  signedMode='S', roundMode='trunc', saturateMode= 'wrap')
        
        self.symb_in.value          = 0
        self.next_symb_in.value     = 0
        self.symb_out.value         = 0
        
    def run(self, reset, enable, control, phase, symb_in):
        if reset:
            self.symb_in.value          = 0
            self.next_symb_in.value     = 0
            self.symb_out.value         = 0
            for i in range(self.OS):
                self.fifo[i].value = 0
                
        elif enable:
            self.symb_in.value = self.next_symb_in.value
            self.next_symb_in.value = symb_in
            
            for i in range(self.OS-1):
                self.fifo[self.OS-i-1].value = self.fifo[self.OS-i-2].value
            self.fifo[0].value = self.symb_in.value
        
            if control == 0:                                        # Valid
                if phase == 0:
                    self.symb_out.value = self.fifo[0].value
                elif phase == 1:
                    self.symb_out.value = self.fifo[1].value
                elif phase == 2:
                    self.symb_out.value = self.fifo[2].value
                elif phase == 3:
                    self.symb_out.value = self.fifo[3].value