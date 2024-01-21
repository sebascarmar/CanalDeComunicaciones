import numpy as np

class Polyphase_filter:

    def __init__(self, os, pulse_filter, nbaud):
        self.os             = os
        self.pulse_filter   = pulse_filter
        self.nbaud          = nbaud
        self.symbols_incoming  = np.zeros(self.nbaud)
        self.pol_filter     = []

        for i in range(self.nbaud):  # nbaud * os coeficientes
            self.pol_filter.append([])
            for j in range(self.os):
                self.pol_filter[i].append(pulse_filter[i * self.os + j])

    def get_coef(self):
        return self.pol_filter

    def get_coef_for_control(self, control):
        coef = []
        for i in range(self.nbaud):
            coef.append(self.pol_filter[i][control])
        return coef

    def get_symbols_incoming(self):
        return self.symbols_incoming
    
    def map_out_bit_incoming(self, bit_in):
        if bit_in == 0:
            return -1
        else:
            return 1
    
    def shift_symbols_incoming(self, symb_in, control):
        if control == 0:
            self.symbols_incoming = np.roll(self.symbols_incoming, 1)
            self.symbols_incoming[0] = symb_in
    
    def get_symbol_output(self, symbols_in, control):     # entrega cada producto de simbolo por coeficiente
        symb_out = 0
        for i in range(self.nbaud):
            symb_out += self.pol_filter[i][control] * symbols_in[i]
        return symb_out


