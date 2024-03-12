
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from classes.fir_filter_fixedPoint import fir_filter
from tool._fixedInt import *


## Generate a signal
samplingFreq = 1000

A1 = 0.5
A2 = 0.3
f1 = 20
f2 = 250
t = np.linspace(0,1,1000)
y = (A1 * np.sin(2 * np.pi * f1 * t)) + (A2 * np.sin(2 * np.pi * f2 * t))

N = 10
Wn = 0.2

NBTot=8
NBFrac=6


# Compute Fourier transform
yhat = np.fft.fft(y)
fcycles = np.fft.fftfreq(len(t), d=1.0 / samplingFreq)

plt.figure(figsize=(10, 6))
plt.plot(t, y)
plt.ylabel("amplitude")
plt.xlabel("time")
plt.show()

# Signal spectrum
plt.figure(figsize=(10, 6))
plt.plot(fcycles, np.absolute(yhat))
plt.xlim([0, 500])
plt.ylabel("amplitude")
plt.xlabel("frequency")
plt.show()


filter_coeff = signal.firwin(N, 30 ,window='hamming', nyq=500)


print(len(filter_coeff))
filter_coeff /= np.sum(filter_coeff)
print(filter_coeff)

#filtrado por clase en punto fijo
filter=fir_filter(filter_coeff,NBTot,NBFrac)
filtered_output_fix = np.zeros(len(y))
for i in range(len(y)):
    filtered_output_fix[i] = filter.filter_symb(y[i]) 


#filtrado en punto flotante por libreria 
filtered_output = signal.lfilter(filter_coeff, 1.0, y)

    

plt.figure(figsize=(12, 8))
plt.plot(t, y)
plt.xlabel("time")
plt.ylabel("amplitude")
plt.plot(t, filtered_output_fix)
plt.plot(t, filtered_output)
plt.legend(['sig in', 'filtered_fixed','filtered'])
plt.show()

# Generate Fourier transform
X = np.fft.fft(filtered_output)
X2 = np.fft.fft(filtered_output_fix)
fcycles = np.fft.fftfreq(len(t), d=1.0 / samplingFreq)

plt.figure(figsize=(12, 8))
plt.plot(fcycles, np.absolute(yhat))
plt.plot(fcycles, np.absolute(X))
plt.plot(fcycles, np.absolute(X2))
plt.xlim([0, 500])
plt.xlabel("frequency")
plt.ylabel("amplitude")
plt.legend(['sig in', 'filtered','filtered_fixed'])
plt.show()