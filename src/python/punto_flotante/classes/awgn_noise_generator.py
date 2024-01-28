
import numpy as np

class awgn_noise_generator:

    def __init__(self, M, NOS, EbNo):
        self.M      = M
        self.NOS    = NOS
        self.EbNo   = EbNo
        self.k      = np.log2(M)
        self.SNR    = EbNo*self.k/NOS
        self.fifo   = np.zeros(50)
        self.media  = 0
        self.sigma  = 1

    def set_media(self, media):
        self.media = media
        return

    def set_sigma(self, sigma):
        self.sigma = sigma
        return

    def noise(self, symb_in):
        
        np.roll(self.fifo, 1)
        self.fifo[0] = symb_in
        s_k_energy = np.var(self.fifo)
        No = s_k_energy/self.SNR
        
        noise = np.sqrt(No)*np.random.normal(self.media, self.sigma, size=symb_in.shape)
        
        # Ruido gaussiano de media 0 y desviación estándar 0.2
        #noise = np.random.normal(self.media, self.sigma, size=array.shape)
        # Agregar ruido al arreglo original
        symb_out = symb_in + noise
        return symb_out
