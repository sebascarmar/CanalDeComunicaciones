import numpy as np
from numpy import convolve
import matplotlib.pyplot as plt


def rcosine_by_taps(fc, fs, rolloff, oversampling, Nbauds, Norm, n_taps=0):
    if n_taps == 0:
        n_taps = oversampling * Nbauds  # numero de coeficientes o Pulse shaping taps

    if n_taps%2 == 0: # forzar como impar
        n_taps =  n_taps + 1

    BR = fc*2       #Baud Rate
    rolloff = rolloff + 0.0001
    T = 1 / fc       #Time interval between two consecutive symbols
    Ts = 1 / fs      #Time between 2 consecutive samples at Tx output
    """ Respuesta al impulso del pulso de caida cosenoidal """

    t_vect = np.arange(-0.5 * (n_taps - 1) * Ts, 0.5 * n_taps * Ts, Ts)
    tn_vect = t_vect * 2/T

    # filtro pasabajos
    y_vect = []
    for t in tn_vect:
        y_vect.append(np.sinc(t)*(np.cos(np.pi*rolloff*t)/(1-(4.0*rolloff*rolloff*t*t))))
    y_vect = np.array(y_vect)

    if Norm:
        y_vect = y_vect/np.sum(y_vect)   #normaliza ganancia, 0db

    return tn_vect, y_vect


def r_rcosine_by_taps(fc, fs, rolloff, oversampling, Nbauds, Norm, n_taps=0):
    if n_taps == 0:
        n_taps = oversampling * Nbauds  # numero de coeficientes o Pulse shaping taps

    if (n_taps%2 == 0): # forzar como impar
        n_taps =  n_taps + 1

    BR = fc*2       #Baud Rate
    rolloff = rolloff + 0.0001
    T = 1 / fc       #Time interval between two consecutive symbols
    Ts = 1 / fs      #Time between 2 consecutive samples at Tx output

    """ Respuesta al impulso del pulso de caida cosenoidal """

    t_vect = np.arange(-0.5 * (n_taps - 1) * Ts, 0.5 * n_taps * Ts, Ts)
    tn_vect = t_vect * 2/T

    y_vect = []
    #filtro pasabajos
    for t in tn_vect:
        if (t == 0):
            y_vect.append((1+rolloff*(4/np.pi-1)))
        else:
            y_vect.append((4*rolloff*t*np.cos(((1+rolloff)*np.pi*t))+np.sin((1-rolloff)*np.pi*t))/(np.pi*t*(1-(16*rolloff*rolloff*t*t))))

    y_vect = np.array(y_vect)

    if Norm:
        y_vect = y_vect/np.sum(y_vect)   #normaliza ganancia, 0db

    return tn_vect, y_vect

###################################################

BR = 100e9     # Baud Rate
OV = 3          # Oversampling rate
rolloff = 0.5  # Pulse shaping rolloff
Nbauds = 5
h_taps = 15     # Pulse shaping taps
fs = OV*BR      # Sampling rate to emulate analog domain
T = 1/BR       # Time interval between two consecutive symbols
Ts = 1/fs      # Time between 2 consecutive samples at Tx output


rrct, rrcv = r_rcosine_by_taps(BR/2, fs, 0.5, OV, Nbauds, True)
print ("######################### ROOT RAISED COSINE FILTER #########################")
print (rrct)
print (rrcv)

h_rrc_rrc = convolve(rrcv, rrcv)
print ("######################### ROOT RAISED COSINE CONVOLVED FILTER #########################")
print(h_rrc_rrc)  # deberia ser equivalente al rcv (raised cosine)


rct, rcv = rcosine_by_taps(BR/2, fs, 0.5, OV, Nbauds, True, n_taps=len(h_rrc_rrc))
print ("######################### RAISED COSINE FILTER #########################")
print (rct)
print (rcv)

#plot de del rrc convolucionado y el rc
plt.figure(figsize=[14,7])
plt.plot(rct, h_rrc_rrc, '-g', linewidth=2)
plt.plot(rct, rcv, 'r.', markersize=12)
plt.legend()
plt.grid(True)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

plt.show()

#plot de del rrrc
#plt.plot(rrct,rrcv,'ro-',linewidth=2.0)
#plt.show()
