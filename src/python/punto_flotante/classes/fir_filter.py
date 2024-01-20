import numpy as np

class fir_filter:

    def __init__(self, os, pulse_filter, nbaud):
        self.os = os
        self.pulse_filter = pulse_filter
        self.nbaud = nbaud
        self.bits_incoming = np.zeros(self.nbaud*self.os)  # 6 en lugar de 24

    def get_coef(self):
        return self.pulse_filter

    def get_bits_incoming(self, bits_upS):
        self.bits_incoming = np.roll(self.bits_incoming, 1)
        self.bits_incoming[0] = bits_upS
        return self.bits_incoming

    def get_bits_output(self, bits_in):     # entrega cada producto de bit por coeficiente
        bits_salida = 0
        for i in range(self.nbaud*self.os):
            bits_salida += self.pulse_filter[i] * bits_in[i]
        return bits_salida