
import numpy as np
import matplotlib.pyplot as plt

class awgn_noise_generator:

    def __init__(self, M, NOS, EbNo):
        self.M          = M
        self.NOS        = NOS
        self.EbNo_db    = EbNo
        self.EbNo       = 10**(EbNo/10)
        self.k          = np.log2(M)
        self.SNR        = self.EbNo*self.k/NOS
        self.fifo       = np.zeros(1000)
        self.media      = 0
        self.sigma      = 1
        self.s_k_energy = 0
        self.No         = 0
        self.n_k        = 0
        self.symb_out   = 0
        self.symb_in    = 0
        self.idx        = 0

    def set_media(self, media):
        self.media = media
        return

    def set_sigma(self, sigma):
        self.sigma = sigma
        return

    def noise(self, symb_in):
        
        #self.idx += 1
        #if self.idx == 400:
        #    plt.plot(self.fifo)
        #    plt.grid(True)
        #    plt.show()
            
        self.fifo = np.roll(self.fifo, 1)
        self.symb_in = symb_in
        self.fifo[0] = symb_in
        #print(symb_in)
        self.s_k_energy = np.var(self.fifo)
        #self.s_k_energy = 0.06254134832912556
        self.No = self.s_k_energy/self.SNR
        
        self.n_k = np.sqrt(self.No)*np.random.normal(self.media, self.sigma)
        
        # Ruido gaussiano de media 0 y desviación estándar 0.2
        #noise = np.random.normal(self.media, self.sigma, size=array.shape)
        # Agregar ruido al arreglo original
        self.symb_out = symb_in + self.n_k
        return self.symb_out
