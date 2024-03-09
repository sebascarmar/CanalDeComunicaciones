from tool._fixedInt import *

class prbs9:
    
    def __init__(self, seed):
        self.seed       = seed
        
        self.fifo       = DeFixedInt(9, 0, signedMode = 'U', roundMode='trunc', saturateMode='wrap')
        self.bit_out    = DeFixedInt(1, 0, signedMode = 'U', roundMode='trunc', saturateMode='wrap')
        self.xor_bit    = DeFixedInt(1, 0, signedMode = 'U', roundMode='trunc', saturateMode='wrap')
        self.symb_out   = DeFixedInt(8, 7, signedMode = 'S', roundMode='trunc', saturateMode='wrap')
        
        self.fifo.value         = self.seed
        self.bit_out.value      = 0
        self.xor_bit.value      = 0
        self.symb_out.value     = 0
        
    def run(self, reset, enable, control):
        if reset:
            self.fifo.value         = self.seed
            self.bit_out.value      = 0
            self.xor_bit.value      = 0
            self.symb_out.value     = 1
            
        elif enable:
            if control == 0:                                                                                # Valid
                self.bit_out.value = (self.fifo.value & 0b100000000)>>8

                self.xor_bit.value = ((self.fifo.value & 0b100000000)>>8)^((self.fifo.value & 0b10000)>>4)  # xor bits 5 y 9
                self.fifo.value = (self.fifo.value << 1) | self.xor_bit.value                               # PRBS shift
            
            if self.bit_out.value == 1:                                                                     #Mapper
                self.symb_out.value = -1
            else:
                self.symb_out.value = 1