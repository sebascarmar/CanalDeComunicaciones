import numpy as np

class BitsErrorRate:

    def __init__(self, Lfifo):   # para 9 bits
        self.bits_errores = 0
        self.bits_totales = 0   # acumuladores
        self.fifo_tx      = np.zeros(Lfifo)
        self.fifo_rx      = np.zeros(Lfifo)

    def insert_tx_bit(self, bit_tx):
        self.fifo_tx = np.roll(self.fifo_tx, 1)
        self.fifo_tx[0] = bit_tx
        return
        
    def insert_rx_bit(self, bit_rx):
        self.fifo_rx= np.roll(self.fifo_rx, 1)
        self.fifo_rx[0] = bit_rx
        return

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

    def correlacion(self):

        max_corr = 0
        offset = 0
        length = len(self.fifo_tx)

        for i in range(length):
            corr = 0
            if i > 0:
                self.fifo_tx = np.roll(self.fifo_tx, 1)
            for j in range(length):

                corr += self.fifo_tx[j] * self.fifo_rx[j]  # acumulador

            if corr > max_corr:
                max_corr = corr
                offset = i

        if offset == 0:
            return offset
        else:
            return offset - 511








