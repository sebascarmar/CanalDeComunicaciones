from classes.Polyphase_filter import Polyphase_filter
from classes.ber_Class import BitsErrorRate

from classes.awgn_noise_generator import awgn_noise_generator
from classes.prbs9_Class import prbs9

from modules.tx_rcosine_procom import *

import numpy as np
from numpy import convolve
import copy

def main():

    ##################################################################
    #                   DEFINICIONES INICIALES                       #
    ##################################################################
    FB = 1000  # BR baudrate
    beta = 0.5
    OS = 4
    nbaud = 6
    Norm = True
    fs = OS * float(FB) * 1.0e6
    fc= (float(FB) * 1.0e6) / 2
    RRC = True
    Nsymb = 511
    offsetI = 0
    offsetQ = 0;
    phase = 0;
    sigma = 0.1    # cambiar a cero para anular ruido
    ##################################################################
    #                   DEFINICION DE BUFFERS                        #
    ##################################################################
    # Buffer de recepcion y de comparacion de datos
    bits_txI = np.zeros(511)
    bits_rxI = np.zeros(511)
    bits_txQ = np.zeros(511)
    bits_rxQ = np.zeros(511)
    ##################################################################
    #                   CREACION DE OBJETOS                          #
    ##################################################################
    # PRBS9
    Q_seed = 0b111111110;
    I_seed = 0b110101010;
    prbsQ = prbs9(Q_seed);
    prbsI = prbs9(I_seed)

    # BER
    ber_rxQ = BitsErrorRate();
    ber_rxI = BitsErrorRate()

    # definicion del filtro RRC
    (tf, filt, dot) = filtro_pulso(fc, fs, beta, OS, nbaud, Norm, RRC, n_taps=0)

    # filtro RRC (root raised cosine) implementacion polifasica
    pol_filterI = Polyphase_filter(OS, filt, nbaud)
    pol_filterQ = Polyphase_filter(OS, filt, nbaud)
    pol_filterI2 = Polyphase_filter(OS, filt, nbaud)
    pol_filterQ2 = Polyphase_filter(OS, filt, nbaud)

    # filtro RRC (root raised cosine) convolucionado consigo mismo
    #h_rrc_rrc = convolve(filt, filt)

    # filtro Raised Cosine producto de la convolucion del root raised cosine
    #rct, rcv, rc_dot = filtro_pulso(fc, fs, beta, OS, nbaud, Norm, RRC=False, n_taps=len(h_rrc_rrc))

    # gauss noise generator
    gng = awgn_noise_generator(media=0, sigma=sigma)
    ##################################################################
    #                   LOOP                                         #
    ##################################################################
    while True:
    ##################################################################
    #                   MANEJO DEL SISTEMA DE COMUNICACION           #
    ##################################################################
        control = (OS-1)
        for i in range(Nsymb*OS):   # Nsymb*OS
            #print("#############################################################")
            if control == (OS-1):   # contador de control
                control = 0
            else:
                control = control + 1

            if control == 0:
                # generacion de bit por prbs9
                bits_txI = np.roll(bits_txI, 1);
                bits_txI[0] = prbsI.generate()  # 1 bit
                bits_txQ = np.roll(bits_txQ, 1);
                bits_txQ[0] = prbsQ.generate()  # 1 bit

            ################################

            #print("control: " + str(control))
            #print("bits_txI: " + str(bits_txI))

            # filtro transmisor
            bits_entradaI = pol_filterI.get_bits_incoming(bits_txI[0], control)
            bits_entradaQ = pol_filterQ.get_bits_incoming(bits_txQ[0], control)

            #print("bits_entradaI: " + str(bits_entradaI))

            # convolucion entre filtro y entrada
            bits_salidaI = pol_filterI.get_bits_output(bits_entradaI, control)   # 4 bits de salida debido al oversampling
            bits_salidaQ = pol_filterQ.get_bits_output(bits_entradaQ, control)

            print("filter coef: " + str(pol_filterI.get_coef_for_control(control)))
            print("bits_salidaI: " + str(bits_salidaI))

            #################################

            # IMPLEMENTACION DE RUIDO GAUSSIANO
            bits_salidaI = gng.noise(bits_salidaI)
            bits_salidaQ = gng.noise(bits_salidaQ)

            ################################

            # filtro receptor
            bits_entradaI = pol_filterI2.get_bits_incoming(bits_salidaI, control)
            bits_entradaQ = pol_filterQ2.get_bits_incoming(bits_salidaQ, control)

            print("bits_entradaI2: " + str(bits_entradaI))

            # convolucion entre filtro y entrada
            bits_salidaI = pol_filterI2.get_bits_output(bits_entradaI, control)  # 4 bits de salida debido al oversampling
            bits_salidaQ = pol_filterQ2.get_bits_output(bits_entradaQ, control)

            #print("filter2 coef: " + str(pol_filterI2.get_coef_for_control(control)))
            #print("bits_salidaI2: " + str(bits_salidaI))

            #################################

            # Downsampling
            if control == phase:
                bits_rxI = np.roll(bits_rxI, 1)
                bits_rxQ = np.roll(bits_rxQ, 1)
                bits_rxI[0] = downSampling(bits_salidaI)  # 1 bit
                bits_rxQ[0] = downSampling(bits_salidaQ)  # 1 bit

                #print("bits_rxI: " + str(bits_rxI))

                # BER
                ber_rxI.contador_bits()
                ber_rxQ.contador_bits()
                ber_rxI.contador_errores(bits_txI[offsetI], bits_rxI[0])
                ber_rxQ.contador_errores(bits_txQ[offsetQ], bits_rxQ[0])

        ##################################################################
        #                   BER                                          #
        ##################################################################
        # se crea una copia y se correlacionar mientras el sistema continua en marcha
        tx1I = copy.deepcopy(bits_txI)
        tx1Q = copy.deepcopy(bits_txQ)
        rx1I = copy.deepcopy(bits_rxI)
        rx1Q = copy.deepcopy(bits_rxQ)
        offsetI = - ber_rxI.correlacion(tx1I, rx1I)
        offsetQ = - ber_rxQ.correlacion(tx1Q, rx1Q)

        #print("offsetI: " + str(offsetI))

if __name__ == '__main__':
    main()


#correcciones, ber en escala logaritmica (no porcentaje)
#mostrar datos tanto del receptor como del transmisor en la segunda pestaña
#(agregar un widget que me permita alternar entre uno y otro)