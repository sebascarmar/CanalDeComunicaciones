import PySimpleGUI as sg

from classes.DspGuiClass import dsp_gui
from classes.Polyphase_filter import Polyphase_filter
from classes.ber_Class import BitsErrorRate

from classes.awgn_noise_generator import awgn_noise_generator
from classes.prbs9_Class import prbs9

from modules.DPI import get_dpi
from modules.build_tab import build_tab
from modules.tx_rcosine_procom import *

import numpy as np
from numpy import convolve
import copy


def main():
    ##################################################################
    #                   INICIAR GUI                                  #
    ##################################################################
    dpi = get_dpi()
    aplicacion = dsp_gui(dpi, (475, 215))
    ##################################################################
    #                   DEFINICIONES INICIALES                       #
    ##################################################################
    FB = 1000  # BR baudrate
    beta = 0.5
    OS = 4
    nbaud = 6
    Norm = True
    n_taps = nbaud * OS
    fs = OS * float(FB) * 1.0e6
    fc= (float(FB) * 1.0e6) / 2
    Ts = 1 / fs
    RRC = True
    T = 1 / (float(FB) * 1.0e6)
    Q_I = False
    current_tab = ''
    event = 0
    values = 0
    Nsymb = 511
    Nfreqs = 256
    offsetI = 0
    offsetQ = 0;
    phase = 0;
    gauss = False
    sigma = 0.1
    freerun = False
    ##################################################################
    #                   DEFINICION DE BUFFERS                        #
    ##################################################################
    # Buffer de recepcion y de comparacion de datos
    bits_txI = np.zeros(511)
    bits_rxI = np.zeros(511)
    bits_txQ = np.zeros(511)
    bits_rxQ = np.zeros(511)
    bits_salI_first_stage = np.zeros(511 * OS)
    bits_salQ_first_stage = np.zeros(511 * OS)
    bits_salI = np.zeros(511 * OS)      # os  #fixme
    bits_salQ = np.zeros(511 * OS)      # os
    bits_upSI_plot = np.zeros(511 * OS)     # os
    bits_upSQ_plot = np.zeros(511 * OS)     # os
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
        if event == sg.WIN_CLOSED:
            break
        # if [event, values] == aplicacion.window.read(timeout=100):
        #    continue
        event, values = aplicacion.window.read(timeout=100)  # timeout=100
        ##################################################################
        #                   MANEJO DE ELEMENTOS DE GUI                   #
        ##################################################################
        changes = beta != float(values['B']) or OS != int(values['OS']) or nbaud != int(values['N Bauds']) or  \
                Norm != values['Norm'] or RRC != values['RRC'] or \
                phase != int(values['PConst']) or  FB != int(values['FB']) or \
                sigma != float(values['sigma']) or freerun != (values['freerun'])

        # Cambios frecuencia de baudios
        if FB != int(values['FB']):
            FB = int(values['FB'])
            T = 1 / (float(FB) * 1.0e6)
            fc = (float(FB) * 1.0e6) / 2

        # Cambios oversampling
        if OS != int(values['OS']):
            OS = int(values['OS'])
            bits_salI = np.zeros(511 * OS)
            bits_salQ = np.zeros(511 * OS)
            bits_salI_first_stage = np.zeros(511 * OS)
            bits_salQ_first_stage = np.zeros(511 * OS)
            bits_upSI_plot = np.zeros(511 * OS)
            bits_upSQ_plot = np.zeros(511 * OS)
            aplicacion.window['PConst'].update(range=(0, int(values['OS']) - 1))  # Cambiar el rango del slider
        # Cambio de fase
        if phase != int(values['PConst']):
            ber_rxQ.__init__()
            ber_rxI.__init__()
            phase = int(values['PConst'])

        # Actualizacion de parametros
        beta = float(values['B']);
        nbaud = int(values['N Bauds']);
        n_taps = nbaud * OS;
        fs = OS * float(FB) * 1.0e6;
        Ts = 1 / fs;
        Norm = values['Norm'];
        RRC = values['RRC']
        gauss = values['gauss']
        sigma = float(values['sigma'])
        gng.set_sigma(sigma)
        freerun = values['freerun']

        # Redefinicion del filtro
        if changes:

            # actualizar filtro RRC
            (tf, filt, dot) = filtro_pulso(fc, fs, beta, OS, nbaud, Norm, RRC, n_taps=0)

            # crear filtro polifasico
            pol_filterI = Polyphase_filter(OS, filt, nbaud)
            pol_filterQ = Polyphase_filter(OS, filt, nbaud)
            pol_filterI2 = Polyphase_filter(OS, filt, nbaud)
            pol_filterQ2 = Polyphase_filter(OS, filt, nbaud)

            # filtro RRC (root raised cosine) convolucionado consigo mismo
            #h_rrc_rrc = convolve(filt, filt)

            # filtro Raised Cosine producto de la convolucion del root raised cosine
            #rct, rcv, rc_dot = filtro_pulso(fc, fs, beta, OS, nbaud, Norm, RRC=False, n_taps=len(h_rrc_rrc))

        ##################################################################
        #                   MANEJO DEL SISTEMA DE COMUNICACION           #
        ##################################################################
        if changes or gauss or freerun:
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
                bits_upSI_plot = np.roll(bits_upSI_plot, 1)  # BUFFERS PARA PLOT
                bits_upSQ_plot = np.roll(bits_upSQ_plot, 1)
                if control == 0:
                    bits_upSI_plot[0] = 1 if bits_txI[0] else -1
                    bits_upSQ_plot[0] = 1 if bits_txQ[0] else -1
                else:
                    bits_upSI_plot[0] = 0
                    bits_upSQ_plot[0] = 0
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

                #print("filter coef: " + str(pol_filterI.get_coef_for_control(control)))
                #print("bits_salidaI: " + str(bits_salidaI))

                #################################
                bits_salI_first_stage = np.roll(bits_salI_first_stage, 1)  # BUFFERS PARA PLOT
                bits_salQ_first_stage = np.roll(bits_salQ_first_stage, 1)
                bits_salI_first_stage[0] = bits_salidaI
                bits_salQ_first_stage[0] = bits_salidaQ
                #################################

                # IMPLEMENTACION DE RUIDO GAUSSIANO
                if gauss:
                    bits_salidaI = gng.noise(bits_salidaI)
                    bits_salidaQ = gng.noise(bits_salidaQ)

                # filtro receptor
                if RRC:
                    bits_entradaI = pol_filterI2.get_bits_incoming(bits_salidaI, control)
                    bits_entradaQ = pol_filterQ2.get_bits_incoming(bits_salidaQ, control)

                    #print("bits_entradaI2: " + str(bits_entradaI))

                    # convolucion entre filtro y entrada
                    bits_salidaI = pol_filterI2.get_bits_output(bits_entradaI, control)  # 4 bits de salida debido al oversampling
                    bits_salidaQ = pol_filterQ2.get_bits_output(bits_entradaQ, control)

                    #print("filter2 coef: " + str(pol_filterI2.get_coef_for_control(control)))
                    #print("bits_salidaI2: " + str(bits_salidaI))

                #################################
                bits_salI = np.roll(bits_salI, 1)  # BUFFERS PARA PLOT
                bits_salQ = np.roll(bits_salQ, 1)
                bits_salI[0] = bits_salidaI
                bits_salQ[0] = bits_salidaQ
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
        ##################################################################
        #                   ACTUALIZACION GUI                            #
        ##################################################################
        if changes or gauss or freerun or current_tab != values.get('tabgroup1'):
            current_tab = values.get('tabgroup1')
            #build_tab(current_tab, rct, rcv, rc_dot, beta, T, OS, values, nbaud, aplicacion, bits_txI, bits_txQ,
            #          ber_rxI, ber_rxQ, Q_I, offsetQ, offsetI, bits_salI, bits_salQ, bits_upSI_plot, bits_upSQ_plot, phase, bits_salI_first_stage, bits_salQ_first_stage)
            build_tab(current_tab, tf, filt, dot, beta, T, OS, values, nbaud, aplicacion, bits_txI, bits_txQ,
              ber_rxI, ber_rxQ, Q_I, offsetQ, offsetI, bits_salI, bits_salQ, bits_upSI_plot, bits_upSQ_plot, phase,
              bits_salI_first_stage, bits_salQ_first_stage)

    aplicacion.window.close()

if __name__ == '__main__':
    main()


#correcciones, ber en escala logaritmica (no porcentaje)
#mostrar datos tanto del receptor como del transmisor en la segunda pestaña
#(agregar un widget que me permita alternar entre uno y otro)