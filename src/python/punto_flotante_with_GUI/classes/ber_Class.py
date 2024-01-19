import numpy as np

class BitsErrorRate:

    def __init__(self):   # para 9 bits
        self.bits_errores = 0
        self.bits_totales = 0   # acumuladores

    def contador_bits(self):
        self.bits_totales += 1

    def contador_errores(self, bit_tx, bit_rx):

        if int(bit_tx) ^ int(bit_rx):
            self.bits_errores += 1

        return self.bits_errores

    def calculo_BER(self):
        if self.bits_totales > 0:
            return self.bits_errores / self.bits_totales * 100
        else:
            return 0

    def correlacion(self, tx, rx):

        max_corr = 0
        offset = 0
        length = len(tx)

        for i in range(length):
            corr = 0
            if i > 0:
                tx = np.roll(tx, 1)
            for j in range(length):

                corr += tx[j] * rx[j]  # acumulador

            if corr > max_corr:
                max_corr = corr
                offset = i

        if offset == 0:
            return offset
        else:
            return offset - 511








