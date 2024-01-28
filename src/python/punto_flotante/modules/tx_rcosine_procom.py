import numpy as np

#from punto_flotante_with_GUI.tool._fixedInt import arrayFixedInt

Nfreqs = 256         # Cantidad de frecuencias, o numero de puntos de fft

def rcosine(fc, fs, rolloff, oversampling, Nbauds, Norm, n_taps=0):
    #if n_taps == 0:
    #    n_taps = oversampling * Nbauds  # numero de coeficientes o Pulse shaping taps
    #if n_taps%2 == 0: # forzar como impar
    #    n_taps =  n_taps + 1

    BR = fc*2       #Baud Rate
    #rolloff = rolloff + 0.0001
    Tbaud = 1 / BR       #Time interval between two consecutive symbols
    Ts = 1 / fs      #Time between 2 consecutive samples at Tx output
    """ Respuesta al impulso del pulso de caida cosenoidal """

    t_vect = np.arange(-0.5*Nbauds*Tbaud, 0.5*Nbauds*Tbaud, Ts)
    # t_vect = np.arange(-0.5 * (n_taps - 1) * Ts, 0.5 * n_taps * Ts, Ts)
    # tn_vect = t_vect * 2/T

    # filtro pasabajos
    y_vect = []
    #filtro pasabajos
    for t in t_vect:
        y_vect.append(np.sinc(t/Tbaud)*(np.cos(np.pi*rolloff*t/Tbaud)/(1-(4.0*rolloff*rolloff*t*t/(Tbaud*Tbaud)))))

    y_vect = np.array(y_vect)

    if Norm:
        y_vect = y_vect/np.sum(y_vect)   #normaliza ganancia, 0db

    dot = (np.sum(y_vect ** 2))

    return t_vect, y_vect, dot

def r_rcosine(fc, fs, rolloff, oversampling, Nbauds, Norm, n_taps=0):
    #if n_taps == 0:
    #    n_taps = oversampling * Nbauds  # numero de coeficientes o Pulse shaping taps
    #if (n_taps%2 == 0): # forzar como impar
    #    n_taps =  n_taps + 1


    BR = fc*2       #Baud Rate
    #rolloff = rolloff + 0.0001
    Tbaud = 1 / BR       #Time interval between two consecutive symbols
    Ts = 1 / fs      #Time between 2 consecutive samples at Tx output

    """ Respuesta al impulso del pulso de caida cosenoidal """
    t_vect = np.arange(-0.5*Nbauds*Tbaud, 0.5*Nbauds*Tbaud, Ts)
    # t_vect = np.arange(-0.5 * (n_taps - 1) * Ts, 0.5 * n_taps * Ts, Ts)
    t_vect = t_vect / Tbaud

    y_vect = []
    #filtro pasabajos
    for t in t_vect:
        if (t == 0):
            y_vect.append((1+rolloff*(4/np.pi-1)))
        else:
            y_vect.append((4*rolloff*t*np.cos(((1+rolloff)*np.pi*t))+np.sin((1-rolloff)*np.pi*t))/(np.pi*t*(1-(16*rolloff*rolloff*t*t))))
    #para t distinto de 0 y  T/(4*rolloff) o  -T/(4*rolloff) ¿?

    y_vect = np.array(y_vect)

    if Norm:
        y_vect = y_vect/np.sum(y_vect)   #normaliza ganancia, 0db

    dot = (np.sum(y_vect ** 2))

    return t_vect, y_vect, dot

def filtro_pulso(fc, fs, rolloff, oversampling, Nbauds, Norm, RRC, n_taps=0):


    ## calculo de coeficientes de filtro
    if RRC:
        (t,rc0,dot) = r_rcosine(fc, fs, rolloff, oversampling, Nbauds, Norm, n_taps=n_taps)  # t=tiempo, rc0=coeficientes del filtro
    else:
        (t,rc0,dot) = rcosine(fc, fs, rolloff, oversampling, Nbauds, Norm, n_taps=n_taps)  # t=tiempo, rc0=coeficientes del filtro

    #print(rc0)

    return t,rc0,dot


def resp_freq(filt, Ts, Nfreqs):
    """Computo de la respuesta en frecuencia de cualquier filtro FIR"""
    H = [] # Lista de salida de la magnitud
    A = [] # Lista de salida de la fase
    filt_len = len(filt)

    #### Genero el vector de frecuencias
    freqs = np.matrix(np.linspace(0,1.0/(2.0*Ts),Nfreqs))
    #### Calculo cuantas muestras necesito para 20 ciclo de
    #### la mas baja frec diferente de cero
    Lseq = 20.0/(freqs[0,1]*Ts)

    #### Genero el vector tiempo
    t = np.matrix(np.arange(0,Lseq))*Ts

    #### Genero la matriz de 2pifTn
    Omega = 2.0j*np.pi*(t.transpose()*freqs)

    #### Valuacion de la exponencial compleja en todo el
    #### rango de frecuencias
    fin = np.exp(Omega)

    #### Suma de convolucion con cada una de las exponenciales complejas
    for i in range(0,np.size(fin,1)):
        fout = np.convolve(np.squeeze(np.array(fin[:,i].transpose())),filt)
        mfout = abs(fout[filt_len:len(fout)-filt_len])
        afout = np.angle(fout[filt_len:len(fout)-filt_len])
        H.append(mfout.sum()/len(mfout))
        A.append(afout.sum()/len(afout))

    return [H,A,list(np.squeeze(np.array(freqs)))]

def bode(rc0, Ts, Nfreqs):
    ### Calculo respuesta en frec para los tres pulsos
    [H0,A0,F0] = resp_freq(rc0, Ts, Nfreqs)

    x1 = F0
    y1 = 20 * np.log10(H0)

    return (x1, y1)


def upsampling(os, symbol):

    if symbol == 0:
        symbol = -1

    zsymb = np.zeros(os*1)
    zsymb[:len(zsymb):int(os)]=symbol

    return zsymb

def other_convolution(pol_filter, bits_entrada):

    bits_salida = np.zeros(len(pol_filter))  # 4 en lugar de 24

    t = np.arange(len(bits_salida))

    for i in range(len(pol_filter)): # 4
        bits_salida = np.roll(bits_salida, 1)
        for j in range(len(pol_filter[0])):  # 6
            bits_salida[0] += pol_filter[i][j]*bits_entrada[j]

    #bits_salida = bits_salida * 2.5  # se escala la salida

    # el primer dato que entro quedara al final de la matriz
    return [t, bits_salida]   # longitud del vector de salida = 4, se hacen 4=os operaciones por bit


def downSampling(symb_out):
    #Turn into INTEGER values
    downsampled_signal = np.where(symb_out >= 0, 1, 0)

    return downsampled_signal



def eyediagram(n, offset, period, symb_out):
    # para B chico el ojo estara cerrado, para B grande estara abierto
    # el punto optimo de muestreo es en el corte donde viene el simbolo o bit, el centro de ojo
    data = symb_out[100:len(symb_out) - 100]
    span     = 2*n
    segments = int(len(data)/span)
    xmax     = (n-1)*period
    xmin     = -(n-1)*period
    x        = list(np.arange(-n,n,)*period)
    xoff     = offset

    data_segments = []
    for i in range(0, segments - 1):
        data_segments.append((x, data[(i * span + xoff) : ((i + 1) * span + xoff)]))

    return [data_segments, [xmin, xmax]]


def dispersion(offset, os, symb_out0I, symb_out0Q):

    x = symb_out0I[100+offset:len(symb_out0I)-(100-offset):int(os)]
    y = symb_out0Q[100+offset:len(symb_out0Q)-(100-offset):int(os)]

    return x, y