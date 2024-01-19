import numpy as np

class Polyphase_filter:

    def __init__(self, os, pulse_filter, nbaud):
        self.os = os
        self.pulse_filter = pulse_filter
        self.nbaud = nbaud
        self.bits_incoming = np.zeros(self.nbaud)
        self.pol_filter = []

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

    def get_bits_incoming(self, bit_in, control):
        if control == 0:
            self.bits_incoming = np.roll(self.bits_incoming, 1)
            if bit_in == 0:
                self.bits_incoming[0] = -1
            else:
                self.bits_incoming[0] = bit_in
        return self.bits_incoming

    def get_bits_output(self, bits_in, control):     # entrega cada producto de bit por coeficiente
        bits_salida = 0
        for i in range(self.nbaud):
            bits_salida += self.pol_filter[i][control] * bits_in[i]
        return bits_salida

        #bits_salida = np.zeros(self.nbaud)
        #for i in range(self.nbaud):
        #    bits_salida = np.roll(bits_salida, 1)
        #    bits_salida[0] += self.pol_filter[i][control] * bits_in[i]

