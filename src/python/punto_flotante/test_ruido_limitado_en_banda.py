import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Parámetros
Fs = 48000 # Frecuencia de muestreo
N = 1024  # numero de muestras
Fc = 1000 # Frecuencia de corte del filtro

# Generar senoide
t = np.linspace(0, N/Fs, N)

# Generar ruido
noise = np.random.randn(N)
fb, fa = 100, 2000

# Diseñar y aplicar filtro FIR pasa-bajos
filtro_lp = signal.firwin(151, Fc, fs=Fs, pass_zero=True)
x_filtrada = np.convolve(filtro_lp, noise)[:N]

# Graficar
plt.subplot(2,1,1)
plt.plot(t, noise)
plt.title('Señal con ruido')

plt.subplot(2,1,2)
plt.plot(t, x_filtrada)
plt.title('Señal filtrada')

plt.tight_layout()
plt.show()