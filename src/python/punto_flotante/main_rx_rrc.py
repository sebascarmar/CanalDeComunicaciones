from classes.Polyphase_filter       import Polyphase_filter
from classes.ber_Class              import BitsErrorRate

from classes.awgn_noise_generator   import awgn_noise_generator
from classes.prbs9_Class            import prbs9
from classes.downsampler_Class      import downsampler
from classes.demapper_Class         import demapper

from modules.tx_rcosine_procom      import *
from modules.eyediagram             import *
from classes.config_Class           import config

import numpy as np
from numpy                          import convolve
import copy

import matplotlib.pyplot as plt
from classes.phase_off              import phase_off

import time

def main(cfg, path_logs):

    ##################################################################
    #                           INITIAL DEFS                         #
    ##################################################################
    Lsim            = cfg.Lsim
    enable_plots    = cfg.enable_plots
    enable_file_log = cfg.enable_file_log
    BR              = cfg.BR                 # BR baudrate
    beta            = cfg.beta               # Rolloff
    M               = cfg.M                  # QPSK modulation factor
    OS              = cfg.OS                 # Oversampling
    nbaud           = cfg.nbaud              # Bauds
    Norm_enable     = cfg.Norm_enable        # Norm_enablealization enable
    fs              = cfg.fs                 # Sampling freq
    fc              = cfg.fc                 
    filter_select   = cfg.filter_select      # True: Root raised cosine, False: Raised cosine
    Nsymb           = cfg.Nsymb              # Total symbols
    offsetI         = cfg.offsetI            
    offsetQ         = cfg.offsetQ            
    phase           = cfg.phase              
    EbNo            = cfg.EbNo               # [dB]
    
    PRBS_Q_seed     = 0b111111110
    PRBS_I_seed     = 0b110101010
    
    list_bit_I_tx = []
    list_bit_I_rx = []
    list_bit_Q_tx = []
    list_bit_Q_rx = []
    
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
    
    #log descriptors
    if(enable_file_log):
        flog_RRC_tx_I_symb     = open(path_logs + "RRC_tx_I_symb.txt"          , "wt") #creates a new file
        flog_RRC_tx_Q_symb     = open(path_logs + "RRC_tx_Q_symb.txt"          , "wt") #creates a new file
        flog_RRC_tx_I_symb_out = open(path_logs + "RRC_tx_I_symb_out.txt"      , "wt") #creates a new file
        flog_RRC_tx_Q_symb_out = open(path_logs + "RRC_tx_Q_symb_out.txt"      , "wt") #creates a new file
        flog_Rx_I_symb_in      = open(path_logs + "Rx_I_symb_in.txt"           , "wt") #creates a new file
        flog_Rx_Q_symb_in      = open(path_logs + "Rx_Q_symb_in.txt"           , "wt") #creates a new file
        flog_dsamp_I_symbol    = open(path_logs + "dsamp_I_symbol.txt"         , "wt") #creates a new file
        flog_dsamp_Q_symbol    = open(path_logs + "dsamp_Q_symbol.txt"         , "wt") #creates a new file
    flog_ber_i              = open(path_logs + "BER_I.txt"              , "a")  #append data at the end of the file
    flog_ber_q              = open(path_logs + "BER_Q.txt"              , "a")  #append data at the end of the file
    flog_ebno               = open(path_logs + "ebno.txt"               , "a")  #append data at the end of the file
    flog_align_pos_i        = open(path_logs + "align_pos_i.txt"        , "a")
    flog_align_pos_q        = open(path_logs + "align_pos_q.txt"        , "a")
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
    (tf, filt, dot) = filtro_pulso(BR/2, fs, beta, OS, nbaud, Norm_enable, filter_select, n_taps=0)

    #rc = np.convolve(filt, filt)
    #t_vec = np.arange(0, len(rc))
    #plt.plot((1/fs)*t_vec, rc)
    #plt.grid()
    #plt.show()

    # filtro RRC (root raised cosine) implementacion polifasica
    RRC_tx_I = Polyphase_filter(OS, filt, nbaud)    # Filtro transmisor conformador de pulsos
    RRC_tx_Q = Polyphase_filter(OS, filt, nbaud)    # Filtro transmisor conformador de pulsos
    
    buffer_I_rx = np.zeros(len(filt))
    buffer_Q_rx = np.zeros(len(filt))
    
    #RRC_rx_I = Polyphase_filter(OS, filt, nbaud)    # Filtro receptor
    #RRC_rx_Q = Polyphase_filter(OS, filt, nbaud)    # Filtro receptor
    
    ds_rx_I  = downsampler(OS) # Downsampler I
    ds_rx_Q  = downsampler(OS) # Downsampler Q
    
    rx_demapper = demapper(M) 
    
    # gauss noise generator
    gng_i    = awgn_noise_generator(M, OS, EbNo)
    gng_q    = awgn_noise_generator(M, OS, EbNo)
    
    
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
                #prbs_I_bits_out[0] = np.random.randint(0, 1, 1)
                #prbs_Q_bits_out[0] = np.random.randint(0, 1, 1)
                
                prbs_I_bits_out    = np.roll(prbs_I_bits_out, 1)
                prbs_I_bits_out[0] = prbsI.generate()      # 1 bit
                prbs_Q_bits_out    = np.roll(prbs_Q_bits_out, 1)
                prbs_Q_bits_out[0] = prbsQ.generate()      # 1 bit
                
                #prbs_I_bits_out    = np.roll(prbs_I_bits_out, 1)
                #prbs_I_bits_out[0] = np.random.randint(0, 2)
                #prbs_Q_bits_out    = np.roll(prbs_Q_bits_out, 1)
                #prbs_Q_bits_out[0] = np.random.randint(0, 2)

            ################################

            #print("control: " + str(control))
            #print("prbs_I_bits_out: " + str(prbs_I_bits_out))

            # filtro transmisor
            
            RRC_tx_I_symb = RRC_tx_I.map_out_bit_incoming(prbs_I_bits_out[0])
            RRC_tx_Q_symb = RRC_tx_Q.map_out_bit_incoming(prbs_Q_bits_out[0])
            
            LOG_SYMBS_I_TX_RRC_IN.append(RRC_tx_I_symb)
            LOG_SYMBS_Q_TX_RRC_IN.append(RRC_tx_Q_symb)
            
            RRC_tx_I.shift_symbols_incoming(RRC_tx_I_symb, control)
            RRC_tx_Q.shift_symbols_incoming(RRC_tx_Q_symb, control)
            
            RRC_tx_I_symbols_in = RRC_tx_I.get_symbols_incoming()
            RRC_tx_Q_symbols_in = RRC_tx_Q.get_symbols_incoming()

            #print("RRC_tx_I_symbols_in: " + str(RRC_tx_I_symbols_in))

            # convolucion entre filtro y entrada
            RRC_tx_I_symb_out = RRC_tx_I.get_symbol_output(RRC_tx_I_symbols_in, control)   # 4 bits de salida debido al oversampling
            RRC_tx_Q_symb_out = RRC_tx_Q.get_symbol_output(RRC_tx_Q_symbols_in, control)

            LOG_SYMBS_I_TX_RRC_OUT.append(RRC_tx_I_symb_out)
            LOG_SYMBS_Q_TX_RRC_OUT.append(RRC_tx_Q_symb_out)


            #################################

            # IMPLEMENTACION DE RUIDO GAUSSIANO
            Rx_I_symb_in = gng_i.noise(RRC_tx_I_symb_out)
            Rx_Q_symb_in = gng_q.noise(RRC_tx_Q_symb_out)
            
            LOG_SYMBS_I_TX_OUT.append(RRC_tx_I_symb_out)
            LOG_SYMBS_Q_TX_OUT.append(RRC_tx_Q_symb_out)
            
            #Rx_I_symb_in=RRC_tx_I_symb_out
            #Rx_Q_symb_in=RRC_tx_Q_symb_out

            LOG_SYMBS_I_RX_IN.append(Rx_I_symb_in)
            LOG_SYMBS_Q_RX_IN.append(Rx_Q_symb_in)
            
            ################################

            # filtro receptor
            #RRC_rx_I.shift_symbols_incoming(Rx_I_symb_in, control)
            #RRC_rx_Q.shift_symbols_incoming(Rx_Q_symb_in, control)
            #
            #RRC_rx_I_symbols_in = RRC_rx_I.get_symbols_incoming()
            #RRC_rx_Q_symbols_in = RRC_rx_Q.get_symbols_incoming()
            
            #print("RRC_rx_I_symbols_in: " + str(RRC_rx_I_symbols_in))

            # convolucion entre filtro y entrada
            #RRC_rx_I_symb_out = RRC_rx_I.get_symbol_output(RRC_rx_I_symbols_in, control)  # 4 bits de salida debido al oversampling
            #RRC_rx_Q_symb_out = RRC_rx_Q.get_symbol_output(RRC_rx_Q_symbols_in, control)

            buffer_I_rx = np.roll(buffer_I_rx, 1)
            buffer_Q_rx = np.roll(buffer_Q_rx, 1)

              # filtro receptor
            buffer_I_rx[0] = Rx_I_symb_in
            buffer_Q_rx[0] = Rx_Q_symb_in
            
            RRC_rx_I_symb_out = np.dot(buffer_I_rx, filt)
            RRC_rx_Q_symb_out = np.dot(buffer_Q_rx, filt)

            LOG_SYMB_I_RX_RRC_OUT.append(RRC_rx_I_symb_out)
            LOG_SYMB_Q_RX_RRC_OUT.append(RRC_rx_Q_symb_out)

            #print("filter2 coef: " + str(RRC_rx_I.get_coef_for_control(control)))
            #print("RRC_rx_I_symb_out: " + str(RRC_rx_I_symb_out))

            #ds_rx_I.insert_symbol(RRC_rx_I_symb_out)
            #ds_rx_Q.insert_symbol(RRC_rx_Q_symb_out)

            #################################

            # Downsampling
            if control == phase:
                
                # if i%200 == 0:
                #     print("EbNo [dB]:               "   +str(gng_i.EbNo_db))
                #     print("EbNo [veces]:            "   +str(gng_i.EbNo))
                #     print("SNR canal [veces]:       "   +str(gng_i.SNR))
                #     print("symbols_in_energy:       "   +str(gng_i.s_k_energy))
                #     print("Noise_energy:            "   +str(gng_i.No))
                #     print("n_k:                     "   +str(gng_i.n_k))
                #     print("symb_in:                 "   +str(gng_i.symb_in))
                #     print("symb_out = symb_in+n_k:  "   +str(gng_i.symb_out))
                #     print("#########################")

                #dsamp_I_symbol = ds_rx_I.get_symbol(0)
                #dsamp_Q_symbol = ds_rx_Q.get_symbol(0)

                #LOG_SYMBS_I_DWS_OUT.append(dsamp_I_symbol)
                #LOG_SYMBS_Q_DWS_OUT.append(dsamp_Q_symbol)

                #print("dsamp_I_symbols: " + str(dsamp_I_symbols))
                
                rx_I_bit_out = rx_demapper.get_bit(RRC_rx_I_symb_out)
                rx_Q_bit_out = rx_demapper.get_bit(RRC_rx_Q_symb_out)

                list_bit_I_tx.append(prbs_I_bits_out[0])
                list_bit_I_rx.append(rx_I_bit_out)
                list_bit_Q_tx.append(prbs_Q_bits_out[0])
                list_bit_Q_rx.append(rx_Q_bit_out)

                # BER
                if(isim > 4):
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
        
        offsetI = - ber_rxI.correlacion()
        offsetQ = - ber_rxQ.correlacion()

#        print("bits_errores:" + str(ber_rxI.bits_errores))
#        print("bits_totales:" + str(ber_rxI.bits_totales))
#
#        print("offsetI: " + str(offsetI))
#        print("offsetQ: " + str(offsetQ))
        
        #print("EbNo veces: " +str(gng_i.EbNo))
        #print("SNR canal: "  +str(gng_i.SNR))
        #print("sk_energy: "  +str(gng_i.s_k_energy))
        #print("No: "         +str(gng_i.No))
        #print("n_k: "        +str(gng_i.n_k))
        #print("symb_in: "    +str(gng_i.symb_in))
        #print("symb_out: "   +str(gng_i.symb_out))
        #
        #print("#########################")

    errors = 0
    cnt = 0
    guard = 1000
    for idx in range(offsetI+guard, len(list_bit_I_rx)):
        # print(f"rx_I: {list_bit_I_rx[idx]}, tx_I: {list_bit_I_tx[idx-delay]}")
        # print(f"rx_Q: {list_bit_I_rx[idx]}, tx_Q: {list_bit_I_tx[idx-delay]}")
        cnt += 2
        if list_bit_I_rx[idx] != list_bit_I_tx[idx-offsetI]:
            errors += 1
        if list_bit_Q_rx[idx] != list_bit_Q_tx[idx-offsetI]:
            errors += 1

    ber = errors/cnt

    print("EbNo: {}".format(EbNo))
    print("errors: {}\n".format(errors))
    print("cnt: {}\n".format(cnt))
    print("ber: {}\n".format(ber))
    print("ber: {}\n".format(ber_rxI.bits_errores/ber_rxI.bits_totales))
    
    if(enable_file_log):
        for idx in range(len(LOG_SYMBS_I_TX_RRC_IN)):
            flog_RRC_tx_I_symb.write(str(LOG_SYMBS_I_TX_RRC_IN[idx])+"\n")
            flog_RRC_tx_Q_symb.write(str(LOG_SYMBS_Q_TX_RRC_IN[idx])+"\n")

        for idx in range(len(LOG_SYMBS_I_TX_RRC_OUT)):
            flog_RRC_tx_I_symb_out.write(str(LOG_SYMBS_I_TX_RRC_OUT[idx])+"\n")
            flog_RRC_tx_Q_symb_out.write(str(LOG_SYMBS_Q_TX_RRC_OUT[idx])+"\n")

        for idx in range(len(LOG_SYMBS_I_RX_IN)):
            flog_Rx_I_symb_in.write(str(LOG_SYMBS_I_RX_IN[idx])+"\n")
            flog_Rx_Q_symb_in.write(str(LOG_SYMBS_Q_RX_IN[idx])+"\n")

        for idx in range(len(LOG_SYMBS_I_DWS_OUT)):
            flog_dsamp_I_symbol.write(str(LOG_SYMBS_I_DWS_OUT[idx])+"\n")
            flog_dsamp_Q_symbol.write(str(LOG_SYMBS_Q_DWS_OUT[idx])+"\n")
            
    flog_ber_i.write(str(ber_rxI.bits_errores/ber_rxI.bits_totales)+"\n")       #Store ber I (concatenated)
    flog_ber_q.write(str(ber_rxQ.bits_errores/ber_rxQ.bits_totales)+"\n")       #Store ber Q (concatenated)
    flog_ebno.write(str(EbNo)+"\n")                                             #Store EbNo (concatenated)
    flog_align_pos_i.write(str(offsetI)+"\n")
    flog_align_pos_q.write(str(offsetQ)+"\n")
    #close all files
    if(enable_file_log):
        flog_RRC_tx_I_symb          .close()
        flog_RRC_tx_Q_symb          .close()
        flog_RRC_tx_I_symb_out      .close()
        flog_RRC_tx_Q_symb_out      .close()
        flog_Rx_I_symb_in           .close()
        flog_Rx_Q_symb_in           .close()
        flog_dsamp_I_symbol         .close()
        flog_dsamp_Q_symbol         .close()
        flog_RRC_tx_I_symb          .close()
        flog_RRC_tx_Q_symb          .close()
    flog_ber_i                  .close()
    flog_ber_q                  .close()
    flog_ebno                   .close()
    flog_align_pos_i            .close()
    flog_align_pos_q            .close()
    
    if enable_plots:
        
        plt.figure(figsize=[6,6])
        plt.title('Constellation Tx')
        plt.plot(LOG_SYMBS_I_TX_RRC_IN[100:len(LOG_SYMBS_I_TX_RRC_IN)], LOG_SYMBS_Q_TX_RRC_IN[100:len(LOG_SYMBS_Q_TX_RRC_IN)],'.',linewidth=2.0)

        plt.xlim((-2, 2))
        plt.ylim((-2, 2))
        plt.grid(True)
        plt.xlabel('Real')
        plt.ylabel('Imag')

        plt.figure(figsize=[6,6])
        plt.title('Constellation Tx OUT')
        plt.plot(LOG_SYMBS_I_TX_RRC_OUT[100:len(LOG_SYMBS_I_TX_RRC_OUT)], LOG_SYMBS_Q_TX_RRC_OUT[100:len(LOG_SYMBS_Q_TX_RRC_OUT)],'.',linewidth=2.0)

        plt.xlim((-2, 2))
        plt.ylim((-2, 2))
        plt.grid(True)
        plt.xlabel('Real')
        plt.ylabel('Imag')

        plt.figure(figsize=[10,6])
        plt.subplot(2,1,1)
        plt.title('Tx RRC symbols I&Q')
        plt.stem(np.arange(0,50),LOG_SYMBS_I_TX_OUT[0:50])
        plt.grid(True)
        plt.ylabel('Magnitud')

        plt.subplot(2,1,2)
        plt.stem(np.arange(0,50),LOG_SYMBS_Q_TX_OUT[0:50])
        plt.grid(True)
        plt.ylabel('Magnitud')

        plt.figure(figsize=[6,6])
        plt.title('Constellation Rx In, post awgn')
        plt.plot(LOG_SYMBS_I_RX_IN[100:len(LOG_SYMBS_I_RX_IN)], LOG_SYMBS_Q_RX_IN[100:len(LOG_SYMBS_Q_RX_IN)],'.',linewidth=2.0)

        plt.xlim((-2, 2))
        plt.ylim((-2, 2))
        plt.grid(True)
        plt.xlabel('Real')
        plt.ylabel('Imag')    

        eyediagram(LOG_SYMBS_I_RX_IN[100:len(LOG_SYMBS_I_RX_IN)], OS, 0, nbaud, 'Eyediagram RX I - rolloff: {}'.format(beta))
        eyediagram(LOG_SYMBS_Q_RX_IN[100:len(LOG_SYMBS_Q_RX_IN)], OS, 0, nbaud, 'Eyediagram RX Q - rolloff: {}'.format(beta))

        plt.figure(figsize=[6,6])
        plt.title('Constellation Rx RCC Out')
        plt.plot(LOG_SYMB_I_RX_RRC_OUT[100:len(LOG_SYMB_I_RX_RRC_OUT)], LOG_SYMB_Q_RX_RRC_OUT[100:len(LOG_SYMB_Q_RX_RRC_OUT)],'.',linewidth=2.0)

        #plt.xlim((-2, 2))
        #plt.ylim((-2, 2))
        plt.grid(True)
        plt.xlabel('Real')
        plt.ylabel('Imag')

        plt.figure(figsize=[6,6])
        plt.title('Constellation Rx Downsampling')
        plt.plot(LOG_SYMBS_I_DWS_OUT[100:len(LOG_SYMBS_I_DWS_OUT)], LOG_SYMBS_Q_DWS_OUT[100:len(LOG_SYMBS_Q_DWS_OUT)],'.',linewidth=2.0)

        plt.xlim((-0.2, 0.2))
        plt.ylim((-0.2, 0.2))
        plt.grid(True)
        plt.xlabel('Real')
        plt.ylabel('Imag')

        plt.show(block=False)
        input('Press enter to finish: ')
        plt.close()