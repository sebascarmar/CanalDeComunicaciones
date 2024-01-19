
import numpy as np

class awgn_noise_generator:

    def __init__(self, media=0, sigma = 0.2):
        # Ruido gaussiano de media 0 y desviación estándar 0.2
        self.media = media
        self.sigma = sigma

    def set_media(self, media):
        self.media = media
        return

    def set_sigma(self, sigma):
        self.sigma = sigma
        return

    def noise(self, array):
        # Ruido gaussiano de media 0 y desviación estándar 0.2
        noise = np.random.normal(self.media, self.sigma, size=array.shape)
        # Agregar ruido al arreglo original
        array_noise = array + noise
        return array_noise
