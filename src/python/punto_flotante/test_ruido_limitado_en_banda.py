import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Parámetros
Fs = 48000 # Frecuencia de muestreo
N = 1024  # numero de muestras
Fc = 1000 # Frecuencia de corte del filtro

# Generar senoide
t = np.linspace(0, N/Fs, N)
x = np.sin(2*np.pi*440*t)

# Añadir ruido filtrado en banda
noise = np.random.randn(N)
fb, fa = 100, 2000
filtro_ruido = signal.firwin(151, [fb,fa], fs=Fs, pass_zero=False)
noise = np.convolve(filtro_ruido, noise)[:N]
x_ruido = x + noise

# Diseñar y aplicar filtro FIR pasa-bajos
filtro_lp = signal.firwin(151, Fc, fs=Fs, pass_zero=True)
x_filtrada = np.convolve(filtro_lp, x_ruido)[:N]

# Graficar
plt.subplot(2,1,1)
plt.plot(t, x_ruido)
plt.title('Señal con ruido')

plt.subplot(2,1,2)
plt.plot(t, x_filtrada)
plt.title('Señal filtrada')

plt.tight_layout()
plt.show()