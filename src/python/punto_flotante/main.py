from classes.Polyphase_filter       import Polyphase_filter
from classes.ber_Class              import BitsErrorRate

from classes.awgn_noise_generator   import awgn_noise_generator
from classes.prbs9_Class            import prbs9
from classes.downsampler_Class      import downsampler
from classes.demapper_Class         import demapper

from modules.tx_rcosine_procom      import *
from modules.eyediagram             import *

import numpy as np
from numpy                          import convolve
import copy

import matplotlib.pyplot as plt
from classes.phase_off              import phase_off

import time

def main():

    ##################################################################
    #                           INITIAL DEFS                         #
    ##################################################################
    Lsim            = 5
    BR              = 1000                      # BR baudrate
    beta            = 0.5                       # Rolloff
    M               = 4                         # QPSK modulation factor
    OS              = 4                         # Oversampling
    nbaud           = 6                         # Bauds
    Norm_enable     = True                      # Norm_enablealization enable
    fs              = OS * float(BR) * 1.0e6    # Sampling freq
    fc              = (float(BR) * 1.0e6) / 2
    filter_select   = True                      # True: Root raised cosine, False: Raised cosine
    Nsymb           = 511                       # Total symbols
    offsetI         = 0
    offsetQ         = 0
    phase           = 0
    EbNo            = 15                       
    
    PRBS_Q_seed     = 0b111111110
    PRBS_I_seed     = 0b110101010
    ##################################################################
    #                   DEFINICION DE BUFFERS                        #
    ##################################################################
    # Buffer de recepcion y de comparacion de datos
    prbs_I_bits_out = np.zeros(Nsymb)
    prbs_Q_bits_out = np.zeros(Nsymb)
    
    LOG_SYMBS_I_TX_RRC_IN = []
    LOG_SYMBS_Q_TX_RRC_IN = []
    LOG_SYMBS_I_RX_IN       = []
    LOG_SYMBS_Q_RX_IN       = []
    LOG_SYMB_I_RX_RRC_OUT = []
    LOG_SYMB_Q_RX_RRC_OUT = []
    LOG_SYMBS_I_TX_OUT    = []
    LOG_SYMBS_Q_TX_OUT    = []
    LOG_SYMBS_I_DWS_OUT   = []
    LOG_SYMBS_Q_DWS_OUT   = []
    LOG_SYMBS_I_TX_RRC_OUT = []
    LOG_SYMBS_Q_TX_RRC_OUT = []
    ##################################################################
    #                   CREACION DE OBJETOS                          #
    ##################################################################
    # PRBS9
    prbsI = prbs9(PRBS_I_seed)
    prbsQ = prbs9(PRBS_Q_seed)

    # BER
    ber_rxI = BitsErrorRate(Nsymb)
    ber_rxQ = BitsErrorRate(Nsymb)

    # Definición del filtro RRC para Tx y Rx
    (tf, filt, dot) = filtro_pulso(fc, fs, beta, OS, nbaud, Norm_enable, filter_select, n_taps=0)

    # filtro RRC (root raised cosine) implementacion polifasica
    RRC_tx_I = Polyphase_filter(OS, filt, nbaud)    # Filtro transmisor conformador de pulsos
    RRC_tx_Q = Polyphase_filter(OS, filt, nbaud)    # Filtro transmisor conformador de pulsos
    
    RRC_rx_I = Polyphase_filter(OS, filt, nbaud)    # Filtro receptor
    RRC_rx_Q = Polyphase_filter(OS, filt, nbaud)    # Filtro receptor
    
    # Generador de offset de fase.
    ##offset_gen =  phase_off()  #! FIX ARGUMENTOS  # Instancia objeto que genera desplazamiento de fase.
    
    # filtro RRC (root raised cosine) convolucionado consigo mismo
    #h_rrc_rrc = convolve(filt, filt)

    # filtro Raised Cosine producto de la convolucion del root raised cosine
    #rct, rcv, rc_dot = filtro_pulso(fc, fs, beta, OS, nbaud, Norm, RRC=False, n_taps=len(h_rrc_rrc))

    ds_rx_I  = downsampler(OS) # Downsampler I
    ds_rx_Q  = downsampler(OS) # Downsampler Q
    
    rx_demapper = demapper(M) 
    
    # gauss noise generator
    gng     = awgn_noise_generator(M, OS, EbNo)
    
    ##################################################################
    #                   LOOP                                         #
    ##################################################################
    for isim in range(Lsim):
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
                prbs_I_bits_out    = np.roll(prbs_I_bits_out, 1)
                prbs_I_bits_out[0] = prbsI.generate()      # 1 bit
                prbs_Q_bits_out    = np.roll(prbs_Q_bits_out, 1)
                prbs_Q_bits_out[0] = prbsQ.generate()      # 1 bit

            ################################

            #print("control: " + str(control))
            #print("prbs_I_bits_out: " + str(prbs_I_bits_out))

            # filtro transmisor
            
            RRC_tx_I_symb = RRC_tx_I.map_out_bit_incoming(prbs_I_bits_out[0])
            RRC_tx_Q_symb = RRC_tx_Q.map_out_bit_incoming(prbs_Q_bits_out[0])
            
            #LOG_SYMBS_I_TX_RRC_IN.append(RRC_tx_I_symb)
            #LOG_SYMBS_Q_TX_RRC_IN.append(RRC_tx_Q_symb)
            
            RRC_tx_I.shift_symbols_incoming(RRC_tx_I_symb, control)
            RRC_tx_Q.shift_symbols_incoming(RRC_tx_Q_symb, control)
            
            RRC_tx_I_symbols_in = RRC_tx_I.get_symbols_incoming()
            RRC_tx_Q_symbols_in = RRC_tx_Q.get_symbols_incoming()

            #print("RRC_tx_I_symbols_in: " + str(RRC_tx_I_symbols_in))

            # convolucion entre filtro y entrada
            RRC_tx_I_symb_out = RRC_tx_I.get_symbol_output(RRC_tx_I_symbols_in, control)   # 4 bits de salida debido al oversampling
            RRC_tx_Q_symb_out = RRC_tx_Q.get_symbol_output(RRC_tx_Q_symbols_in, control)

            #LOG_SYMBS_I_TX_RRC_OUT.append(RRC_tx_I_symb_out)
            #LOG_SYMBS_Q_TX_RRC_OUT.append(RRC_tx_Q_symb_out)

            # Desfasaje de símbolos.
            # (phased_symb_I, phased_symb_Q) = offset_gen.get_phase_off(RRC_tx_I_symb_out, RRC_tx_Q_symb_out) ##fix argumentos en declaracion
            #print("filter coef: " + str(RRC_tx_I.get_coef_for_control(control)))
            #print("RRC_tx_I_symb_out: " + str(RRC_tx_I_symb_out))

            #################################

            # IMPLEMENTACION DE RUIDO GAUSSIANO
            Rx_I_symb_in = gng.noise(RRC_tx_I_symb_out)
            Rx_Q_symb_in = gng.noise(RRC_tx_Q_symb_out)
            
            #LOG_SYMBS_I_TX_OUT.append(RRC_tx_I_symb_out)
            #LOG_SYMBS_Q_TX_OUT.append(RRC_tx_Q_symb_out)
            
            #Rx_I_symb_in=RRC_tx_I_symb_out
            #Rx_Q_symb_in=RRC_tx_Q_symb_out

            #LOG_SYMBS_I_RX_IN.append(Rx_I_symb_in)
            #LOG_SYMBS_Q_RX_IN.append(Rx_Q_symb_in)
            
            ################################

            # filtro receptor
            RRC_rx_I.shift_symbols_incoming(Rx_I_symb_in, control)
            RRC_rx_Q.shift_symbols_incoming(Rx_Q_symb_in, control)
            
            RRC_rx_I_symbols_in = RRC_rx_I.get_symbols_incoming()
            RRC_rx_Q_symbols_in = RRC_rx_Q.get_symbols_incoming()
            
            #print("RRC_rx_I_symbols_in: " + str(RRC_rx_I_symbols_in))

            # convolucion entre filtro y entrada
            RRC_rx_I_symb_out = RRC_rx_I.get_symbol_output(RRC_rx_I_symbols_in, control)  # 4 bits de salida debido al oversampling
            RRC_rx_Q_symb_out = RRC_rx_Q.get_symbol_output(RRC_rx_Q_symbols_in, control)

            #LOG_SYMB_I_RX_RRC_OUT.append(RRC_rx_I_symb_out)
            #LOG_SYMB_Q_RX_RRC_OUT.append(RRC_rx_Q_symb_out)

            #print("filter2 coef: " + str(RRC_rx_I.get_coef_for_control(control)))
            #print("RRC_rx_I_symb_out: " + str(RRC_rx_I_symb_out))

            ds_rx_I.insert_symbol(RRC_rx_I_symb_out)
            ds_rx_Q.insert_symbol(RRC_rx_Q_symb_out)

            #################################

            # Downsampling
            if control == phase:
                #dsamp_I_symbols = np.roll(dsamp_I_symbols, 1)
                #dsamp_Q_symbols = np.roll(dsamp_Q_symbols, 1)
                #dsamp_I_symbols[0] = downSampling(RRC_rx_I_symb_out)  # 1 bit
                #dsamp_Q_symbols[0] = downSampling(RRC_rx_Q_symb_out)  # 1 bit

                dsamp_I_symbol = ds_rx_I.get_symbol(phase)
                dsamp_Q_symbol = ds_rx_Q.get_symbol(phase)

                #LOG_SYMBS_I_DWS_OUT.append(dsamp_I_symbol)
                #LOG_SYMBS_Q_DWS_OUT.append(dsamp_Q_symbol)

                #print("dsamp_I_symbols: " + str(dsamp_I_symbols))
                
                rx_I_bit_out = rx_demapper.get_bit(dsamp_I_symbol)
                rx_Q_bit_out = rx_demapper.get_bit(dsamp_Q_symbol)

                # BER
                ber_rxI.contador_bits()
                ber_rxQ.contador_bits()
                ber_rxI.contador_errores(prbs_I_bits_out[offsetI], rx_I_bit_out)
                ber_rxQ.contador_errores(prbs_Q_bits_out[offsetQ], rx_Q_bit_out)
                
                ber_rxI.insert_tx_bit(prbs_I_bits_out[0])
                ber_rxQ.insert_tx_bit(prbs_Q_bits_out[0])
                ber_rxI.insert_rx_bit(rx_I_bit_out)
                ber_rxQ.insert_rx_bit(rx_Q_bit_out)

        ##################################################################
        #                   BER                                          #
        ##################################################################
        # se crea una copia y se correlacionar mientras el sistema continua en marcha
        #tx1I = copy.deepcopy(prbs_I_bits_out)
        #tx1Q = copy.deepcopy(prbs_Q_bits_out)
        #rx1I = copy.deepcopy(dsamp_I_symbols)
        #rx1Q = copy.deepcopy(dsamp_Q_symbols)
        offsetI = - ber_rxI.correlacion()
        offsetQ = - ber_rxQ.correlacion()

        print("bits_errores:" + str(ber_rxI.bits_errores))
        print("bits_totales:" + str(ber_rxI.bits_totales))

        print("offsetI: " + str(offsetI))
        print("offsetQ: " + str(offsetQ))

        time.sleep(1)  # pausa de 1 segundo tras capturar 511 bits
        
#    plt.figure(figsize=[6,6])
#    plt.title('Constellation Tx')
#    plt.plot(LOG_SYMBS_I_TX_RRC_IN[100:len(LOG_SYMBS_I_TX_RRC_IN)], LOG_SYMBS_Q_TX_RRC_IN[100:len(LOG_SYMBS_Q_TX_RRC_IN)],'.',linewidth=2.0)
#    
#    plt.xlim((-2, 2))
#    plt.ylim((-2, 2))
#    plt.grid(True)
#    plt.xlabel('Real')
#    plt.ylabel('Imag')
#
#    plt.figure(figsize=[6,6])
#    plt.title('Constellation Tx OUT')
#    plt.plot(LOG_SYMBS_I_TX_RRC_OUT[100:len(LOG_SYMBS_I_TX_RRC_OUT)], LOG_SYMBS_Q_TX_RRC_OUT[100:len(LOG_SYMBS_Q_TX_RRC_OUT)],'.',linewidth=2.0)
#    
#    plt.xlim((-2, 2))
#    plt.ylim((-2, 2))
#    plt.grid(True)
#    plt.xlabel('Real')
#    plt.ylabel('Imag')
#
#    plt.figure(figsize=[10,6])
#    plt.subplot(2,1,1)
#    plt.title('Tx RRC symbols I&Q')
#    plt.stem(np.arange(0,50),LOG_SYMBS_I_TX_OUT[0:50])
#    plt.grid(True)
#    plt.ylabel('Magnitud')
#    
#    plt.subplot(2,1,2)
#    plt.stem(np.arange(0,50),LOG_SYMBS_Q_TX_OUT[0:50])
#    plt.grid(True)
#    plt.ylabel('Magnitud')
#    
#    plt.figure(figsize=[6,6])
#    plt.title('Constellation Rx In, post awgn')
#    plt.plot(LOG_SYMBS_I_RX_IN[100:len(LOG_SYMBS_I_RX_IN)], LOG_SYMBS_Q_RX_IN[100:len(LOG_SYMBS_Q_RX_IN)],'.',linewidth=2.0)
#    
#    plt.xlim((-2, 2))
#    plt.ylim((-2, 2))
#    plt.grid(True)
#    plt.xlabel('Real')
#    plt.ylabel('Imag')    
#        
#    eyediagram(LOG_SYMBS_I_RX_IN[100:len(LOG_SYMBS_I_RX_IN)], OS, 0, nbaud, 'Eyediagram RX I - rolloff: {}'.format(beta))
#    eyediagram(LOG_SYMBS_Q_RX_IN[100:len(LOG_SYMBS_Q_RX_IN)], OS, 0, nbaud, 'Eyediagram RX Q - rolloff: {}'.format(beta))
#    
#    plt.figure(figsize=[6,6])
#    plt.title('Constellation Rx RCC Out')
#    plt.plot(LOG_SYMB_I_RX_RRC_OUT[100:len(LOG_SYMB_I_RX_RRC_OUT)], LOG_SYMB_Q_RX_RRC_OUT[100:len(LOG_SYMB_Q_RX_RRC_OUT)],'.',linewidth=2.0)
#    
#    #plt.xlim((-2, 2))
#    #plt.ylim((-2, 2))
#    plt.grid(True)
#    plt.xlabel('Real')
#    plt.ylabel('Imag')
#    
#    plt.figure(figsize=[6,6])
#    plt.title('Constellation Rx Downsampling')
#    plt.plot(LOG_SYMBS_I_DWS_OUT[100:len(LOG_SYMBS_I_DWS_OUT)], LOG_SYMBS_Q_DWS_OUT[100:len(LOG_SYMBS_Q_DWS_OUT)],'.',linewidth=2.0)
#    
#    plt.xlim((-2, 2))
#    plt.ylim((-2, 2))
#    plt.grid(True)
#    plt.xlabel('Real')
#    plt.ylabel('Imag')
#    
#    plt.show(block=False)
#    input('Press enter to finish: ')
#    plt.close()

if __name__ == '__main__':
    main()


#correcciones, ber en escala logaritmica (no porcentaje)
#mostrar datos tanto del receptor como del transmisor en la segunda pestaña
#(agregar un widget que me permita alternar entre uno y otro)
