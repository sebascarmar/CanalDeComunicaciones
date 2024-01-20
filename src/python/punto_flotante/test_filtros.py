
from modules.tx_rcosine_procom import *
from numpy import convolve
import matplotlib.pyplot as plt


BR = 100e9     # Baud Rate
N = 3          # Oversampling rate
rolloff = 0.5  # Pulse shaping rolloff
Nbauds = 5
h_taps = 15     # Pulse shaping taps
fs = N*BR      # Sampling rate to emulate analog domain
T = 1/BR       # Time interval between two consecutive symbols
Ts = 1/fs      # Time between 2 consecutive samples at Tx output

rrct, rrcv, dot = r_rcosine(BR/2, fs, 0.5, N, Nbauds, True)
print ("######################### ROOT RAISED COSINE FILTER #########################")
print (rrct)
print (rrcv)

h_rrc_rrc = convolve(rrcv, rrcv)
print ("######################### ROOT RAISED COSINE CONVOLVED FILTER #########################")
print(h_rrc_rrc)  # deberia ser equivalente al rcv (raised cosine)


rct, rcv, dot = rcosine(BR/2, fs, 0.5, N, Nbauds, True, n_taps=len(h_rrc_rrc))
print ("######################### RAISED COSINE FILTER #########################")
print (rct)
print (rcv)

#plot de del rrc convolucionado y el rc
plt.figure(figsize=[14,7])
plt.plot(rct,h_rrc_rrc,'gs-',linewidth=2.0)
plt.plot(rct,rcv,'k^-',linewidth=2.0)
plt.legend()
plt.grid(True)
#plt.xlim(0,len(rc0)-1)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

plt.show()

#plot de del rrrc
#plt.plot(rrct,rrcv,'ro-',linewidth=2.0)
#plt.show()
