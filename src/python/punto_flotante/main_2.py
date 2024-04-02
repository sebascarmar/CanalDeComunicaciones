from classes.Polyphase_filter       import Polyphase_filter
from classes.ber_Class              import BitsErrorRate

from classes.awgn_noise_generator   import awgn_noise_generator
from classes.prbs9_Class            import prbs9
from classes.downsampler_Class      import downsampler
from classes.demapper_Class         import demapper
from classes.fir_filter             import fir_filter
from classes.phase_off              import phase_off
# from classes.adaptive_filter        import adaptive_filter
from classes.filter_rx_class        import filter_rx
from classes.config_Class           import config

from modules.tx_rcosine_procom      import *
from modules.eyediagram             import *

import numpy as np
from numpy                          import convolve
import copy
from scipy import signal
 
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
    firfilter_order = cfg.firfilter_order    
    NTAPS_ad_fil    = cfg.NTAPS_ad_fil       # Coeficientes del filtro adaptivo
    LMS_step        = cfg.LMS_step           # Step del LMS
    Kp              = cfg.Kp                 # Consstante proporcional PLL
    Ki              = cfg.Ki                 # Constante integral PLL
    Lat             = cfg.Lat                # Latencia PLL
    timer_fcr_on    = cfg.timer_fcr_on       
    timer_cma_off   = cfg.timer_cma_off      
    PRBS_Q_seed     = cfg.PRBS_Q_seed        
    PRBS_I_seed     = cfg.PRBS_I_seed        
    
    ##################################################################
    #                   DEFINICION DE BUFFERS                        #
    ##################################################################
    # Buffer de recepcion y de comparacion de datos
    prbs_I_bits_out = np.zeros(Nsymb)
    prbs_Q_bits_out = np.zeros(Nsymb)
    
    LOG_SYMBS_I_TX_RRC_IN  = []
    LOG_SYMBS_Q_TX_RRC_IN  = []
    LOG_SYMBS_I_RX_IN      = []
    LOG_SYMBS_Q_RX_IN      = []
    LOG_SYMB_I_RX_RRC_OUT  = []
    LOG_SYMB_Q_RX_RRC_OUT  = []
    LOG_SYMBS_I_TX_OUT     = []
    LOG_SYMBS_Q_TX_OUT     = []
    LOG_SYMBS_I_DWS_OUT    = []
    LOG_SYMBS_Q_DWS_OUT    = []
    LOG_SYMBS_I_TX_RRC_OUT = []
    LOG_SYMBS_Q_TX_RRC_OUT = []

    # Logueo Filtro Adaptivo
    LOG_EQ_O_I   = []
    LOG_EQ_FCR_I = []
    LOG_SL_O_I   = []
    LOG_ERR_I    = []
    LOG_EQ_O_Q   = []
    LOG_EQ_FCR_Q = []
    LOG_SL_O_Q   = []
    LOG_ERR_Q    = []
    LOG_PHI      = []
    
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
        flog_eq_o_I            = open(path_logs + "eq_o_I.txt"                 , "wt") #creates a new file
        flog_eq_o_Q            = open(path_logs + "eq_o_Q.txt"                 , "wt") #creates a new file
        flog_eq_fcr_I          = open(path_logs + "eq_fcr_I.txt"               , "wt") #creates a new file
        flog_eq_fcr_Q          = open(path_logs + "eq_fcr_Q.txt"               , "wt") #creates a new file
        flog_sl_o_I            = open(path_logs + "sl_o_I.txt"                 , "wt") #creates a new file
        flog_sl_o_Q            = open(path_logs + "sl_o_Q.txt"                 , "wt") #creates a new file
        flog_err_I             = open(path_logs + "err_I.txt"                  , "wt") #creates a new file
        flog_err_Q             = open(path_logs + "err_Q.txt"                  , "wt") #creates a new file
        flog_phi               = open(path_logs + "phi.txt"                    , "wt") #creates a new file
    flog_ber_i              = open(path_logs + "BER_I.txt"              , "a")  #append data at the end of the file
    flog_ber_q              = open(path_logs + "BER_Q.txt"              , "a")  #append data at the end of the file
    flog_ebno               = open(path_logs + "ebno.txt"               , "a")  #append data at the end of the file

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
    offset_gen =  phase_off()# Instancia objeto que genera desplazamiento de fase.

    #Generador de coeficientes del filtro fir
    filter_coeff = signal.firwin(firfilter_order, fc ,window='hamming', nyq=fs/2)
    #print(len(filter_coeff))
    #filter_coeff /= np.sum(filter_coeff) #opcional

    #Generador del filtro fir
    fir_filter_symbI = fir_filter(filter_coeff)
    fir_filter_symbQ = fir_filter(filter_coeff)

    # Downsamplers
    ds_rx_I  = downsampler(OS) # Downsampler I
    ds_rx_Q  = downsampler(OS) # Downsampler Q

    # Filtro adaptivo
    # ad_fil_I = adaptive_filter(NTAPS_ad_fil,LMS_step)
    # ad_fil_Q = adaptive_filter(NTAPS_ad_fil,LMS_step)
    RX_filter = filter_rx(NTAPS_ad_fil,LMS_step,Kp,Ki,Lat,timer_fcr_on)#,timer_cma_off)

    # Demapper
    rx_demapper = demapper(M)

    # filtro RRC (root raised cosine) convolucionado consigo mismo
    #h_rrc_rrc = convolve(filt, filt)

    # filtro Raised Cosine producto de la convolucion del root raised cosine
    #rct, rcv, rc_dot = filtro_pulso(fc, fs, beta, OS, nbaud, Norm, RRC=False, n_taps=len(h_rrc_rrc))

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

            # Desfasaje de símbolos.
            if((isim*Nsymb+i/OS)>(timer_fcr_on)):
                (phased_symb_I, phased_symb_Q) = offset_gen.get_phase_off(RRC_tx_I_symb_out, RRC_tx_Q_symb_out,1)
                # (phased_symb_I, phased_symb_Q) = offset_gen.get_fixed_off(RRC_tx_I_symb_out, RRC_tx_Q_symb_out,0)# 0,1,2 o 3
            else:
                phased_symb_I = RRC_tx_I_symb_out
                phased_symb_Q = RRC_tx_Q_symb_out
            #print("filter coef: " + str(RRC_tx_I.get_coef_for_control(control)))
            #print("RRC_tx_I_symb_out: " + str(RRC_tx_I_symb_out))

            #filtrado de símbolos.
            filtered_symb_I=fir_filter_symbI.filter_symb(phased_symb_I)#RRC_tx_I_symb_out
            filtered_symb_Q=fir_filter_symbQ.filter_symb(phased_symb_Q)#RRC_tx_Q_symb_out

            #################################

            # IMPLEMENTACION DE RUIDO GAUSSIANO
            Rx_I_symb_in = gng.noise(filtered_symb_I)
            Rx_Q_symb_in = gng.noise(filtered_symb_Q)
            
            LOG_SYMBS_I_TX_OUT.append(RRC_tx_I_symb_out)
            LOG_SYMBS_Q_TX_OUT.append(RRC_tx_Q_symb_out)
            
            #Rx_I_symb_in=RRC_tx_I_symb_out
            #Rx_Q_symb_in=RRC_tx_Q_symb_out

            LOG_SYMBS_I_RX_IN.append(Rx_I_symb_in)
            LOG_SYMBS_Q_RX_IN.append(Rx_Q_symb_in)
            
            ################################

            # filtro receptor
            # RRC_rx_I.shift_symbols_incoming(Rx_I_symb_in, control)
            # RRC_rx_Q.shift_symbols_incoming(Rx_Q_symb_in, control)
            
            # RRC_rx_I_symbols_in = RRC_rx_I.get_symbols_incoming()
            # RRC_rx_Q_symbols_in = RRC_rx_Q.get_symbols_incoming()
            
            # #print("RRC_rx_I_symbols_in: " + str(RRC_rx_I_symbols_in))

            # # convolucion entre filtro y entrada
            # RRC_rx_I_symb_out = RRC_rx_I.get_symbol_output(RRC_rx_I_symbols_in, control)  # 4 bits de salida debido al oversampling
            # RRC_rx_Q_symb_out = RRC_rx_Q.get_symbol_output(RRC_rx_Q_symbols_in, control)
            
            # LOG_SYMB_I_RX_RRC_OUT.append(RRC_rx_I_symb_out)
            # LOG_SYMB_Q_RX_RRC_OUT.append(RRC_rx_Q_symb_out)

            # print("filter2 coef: " + str(RRC_rx_I.get_coef_for_control(control)))
            # print("RRC_rx_I_symb_out: " + str(RRC_rx_I_symb_out))

            ###############################
            ds_rx_I.insert_symbol(Rx_I_symb_in)#Rx_I_symb_in/filtered_symb_I
            ds_rx_Q.insert_symbol(Rx_Q_symb_in)#Rx_Q_symb_in/filtered_symb_Q

            
            # Downsampling
            if control%(OS/2) == 0: #if control == phase:
                #dsamp_I_symbols = np.roll(dsamp_I_symbols, 1)
                #dsamp_Q_symbols = np.roll(dsamp_Q_symbols, 1)
                #dsamp_I_symbols[0] = downSampling(RRC_rx_I_symb_out)  # 1 bit
                #dsamp_Q_symbols[0] = downSampling(RRC_rx_Q_symb_out)  # 1 bit
                
                dsamp_I_symbol = ds_rx_I.get_symbol(0)
                dsamp_Q_symbol = ds_rx_Q.get_symbol(0)
                
                LOG_SYMBS_I_DWS_OUT.append(dsamp_I_symbol)
                LOG_SYMBS_Q_DWS_OUT.append(dsamp_Q_symbol)

                # # Filtro Adaptivo
                # Slicer_I = ad_fil_I.loop_adaptive_filter(dsamp_I_symbol)
                # Slicer_Q = ad_fil_Q.loop_adaptive_filter(dsamp_Q_symbol)
                (Slicer_I,Slicer_Q) = RX_filter.loop_rx_filter(dsamp_I_symbol, dsamp_Q_symbol)
                

            if control == phase:
                # LOG_EQ_O_I.append(ad_fil_I.get_eq_o())
                # LOG_SL_O_I.append(ad_fil_I.get_slicer_o())
                # LOG_ERR_I.append(ad_fil_I.get_error())
                # LOG_EQ_O_Q.append(ad_fil_Q.get_eq_o())
                # LOG_SL_O_Q.append(ad_fil_Q.get_slicer_o())
                # LOG_ERR_Q.append(ad_fil_Q.get_error())

                LOG_EQ_O_I.append(RX_filter.get_eq_o_I())
                LOG_EQ_FCR_I.append(RX_filter.get_eq_fcr_I())
                LOG_SL_O_I.append(RX_filter.get_slicer_I())
                LOG_ERR_I .append(RX_filter.get_error_I())

                LOG_EQ_O_Q.append(RX_filter.get_eq_o_Q())
                LOG_EQ_FCR_Q.append(RX_filter.get_eq_fcr_Q())
                LOG_SL_O_Q.append(RX_filter.get_slicer_Q())
                LOG_ERR_Q .append(RX_filter.get_error_Q())

                LOG_PHI.append(RX_filter.get_phi())

                #print("dsamp_I_symbols: " + str(dsamp_I_symbols))
                # Demapper
                rx_I_bit_out = rx_demapper.get_bit(Slicer_I)
                rx_Q_bit_out = rx_demapper.get_bit(Slicer_Q)
                
                # BER
                if isim > 0:
                    ber_rxI.contador_bits()
                    ber_rxQ.contador_bits()
                    #print('bit tx: {} , bit rx: {}'.format(prbs_I_bits_out[offsetI], rx_I_bit_out))
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
            
    
    #write files
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

        for idx in range(len(LOG_EQ_O_I)):
            flog_eq_o_I.write(str(LOG_EQ_O_I[idx])+"\n")
            flog_eq_o_Q.write(str(LOG_EQ_O_Q[idx])+"\n")

        for idx in range(len(LOG_EQ_FCR_I)):
            flog_eq_fcr_I.write(str(LOG_EQ_FCR_I[idx])+"\n")
            flog_eq_fcr_Q.write(str(LOG_EQ_FCR_Q[idx])+"\n")

        for idx in range(len(LOG_SL_O_I)):
            flog_sl_o_I.write(str(LOG_SL_O_I[idx])+"\n")
            flog_sl_o_Q.write(str(LOG_SL_O_Q[idx])+"\n")

        for idx in range(len(LOG_ERR_I)):
            flog_err_I.write(str(LOG_ERR_I[idx])+"\n")
            flog_err_Q.write(str(LOG_ERR_Q[idx])+"\n")

        for idx in range(len(LOG_PHI)):
            flog_phi.write(str(LOG_PHI[idx])+"\n")
    
    flog_ber_i.write(str(ber_rxI.bits_errores/ber_rxI.bits_totales)+"\n")       #Store ber I (concatenated)
    flog_ber_q.write(str(ber_rxQ.bits_errores/ber_rxQ.bits_totales)+"\n")       #Store ber Q (concatenated)
    flog_ebno.write(str(EbNo)+"\n")                                             #Store EbNo (concatenated)
    
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
        flog_eq_o_I                 .close()
        flog_eq_o_Q                 .close()
        flog_eq_fcr_I               .close()
        flog_eq_fcr_Q               .close()
        flog_sl_o_I                 .close()
        flog_sl_o_Q                 .close()
        flog_err_I                  .close()
        flog_err_Q                  .close()
        flog_phi                    .close()
        flog_RRC_tx_I_symb          .close()
        flog_RRC_tx_Q_symb          .close()
    flog_ber_i                  .close()
    flog_ber_q                  .close()
    flog_ebno                   .close()
    
    if enable_plots:
        # plt.figure(figsize=[6,6])
        # plt.title('Constellation Tx')
        # plt.plot(LOG_SYMBS_I_TX_RRC_IN[100:len(LOG_SYMBS_I_TX_RRC_IN)], LOG_SYMBS_Q_TX_RRC_IN[100:len(LOG_SYMBS_Q_TX_RRC_IN)],'.',linewidth=2.0)
        
        # plt.xlim((-2, 2))
        # plt.ylim((-2, 2))
        # plt.grid(True)
        # plt.xlabel('Real')
        # plt.ylabel('Imag')

        plt.figure(figsize=[6,6])
        plt.title('Constellation Tx OUT')
        plt.plot(LOG_SYMBS_I_TX_RRC_OUT[100:len(LOG_SYMBS_I_TX_RRC_OUT)], LOG_SYMBS_Q_TX_RRC_OUT[100:len(LOG_SYMBS_Q_TX_RRC_OUT)],'.',linewidth=2.0)
        
        plt.xlim((-2, 2))
        plt.ylim((-2, 2))
        plt.grid(True)
        plt.xlabel('Real')
        plt.ylabel('Imag')

        # plt.figure(figsize=[10,6])
        # plt.subplot(2,1,1)
        # plt.title('Tx RRC symbols I&Q')
        # plt.stem(np.arange(0,50),LOG_SYMBS_I_TX_OUT[0:50])
        # plt.grid(True)
        # plt.ylabel('Magnitud')
        
        # plt.subplot(2,1,2)
        # plt.stem(np.arange(0,50),LOG_SYMBS_Q_TX_OUT[0:50])
        # plt.grid(True)
        # plt.ylabel('Magnitud')
        
        plt.figure(figsize=[6,6])
        plt.title('Constellation Rx In, post awgn')
        plt.plot(LOG_SYMBS_I_RX_IN[100:len(LOG_SYMBS_I_RX_IN)], LOG_SYMBS_Q_RX_IN[100:len(LOG_SYMBS_Q_RX_IN)],'.',linewidth=2.0)
        
        plt.xlim((-2, 2))
        plt.ylim((-2, 2))
        plt.grid(True)
        plt.xlabel('Real')
        plt.ylabel('Imag')    
            
        # eyediagram(LOG_SYMBS_I_RX_IN[100:len(LOG_SYMBS_I_RX_IN)], OS, 0, nbaud, 'Eyediagram RX I - rolloff: {}'.format(beta))
        # eyediagram(LOG_SYMBS_Q_RX_IN[100:len(LOG_SYMBS_Q_RX_IN)], OS, 0, nbaud, 'Eyediagram RX Q - rolloff: {}'.format(beta))
        
        # plt.figure(figsize=[6,6])
        # plt.title('Constellation Rx RCC Out')
        # plt.plot(LOG_SYMB_I_RX_RRC_OUT[100:len(LOG_SYMB_I_RX_RRC_OUT)], LOG_SYMB_Q_RX_RRC_OUT[100:len(LOG_SYMB_Q_RX_RRC_OUT)],'.',linewidth=2.0)
        
        # #plt.xlim((-2, 2))
        # #plt.ylim((-2, 2))
        # plt.grid(True)
        # plt.xlabel('Real')
        # plt.ylabel('Imag')
        
        plt.figure(figsize=[6,6])
        plt.title('Constellation Rx Downsampling')
        plt.plot(LOG_SYMBS_I_DWS_OUT[100:len(LOG_SYMBS_I_DWS_OUT)], LOG_SYMBS_Q_DWS_OUT[100:len(LOG_SYMBS_Q_DWS_OUT)],'.',linewidth=2.0)
        
        plt.xlim((-2, 2))
        plt.ylim((-2, 2))
        plt.grid(True)
        plt.xlabel('Real')
        plt.ylabel('Imag')

        #  -------- Plots Filtro Adaptivo ---------------------------------
        plt.figure(figsize=[10,6])
        plt.subplot(2,1,1)
        plt.plot(LOG_EQ_O_I,'.')
        plt.grid(True)
        plt.ylabel('Salida FFE')
        plt.title('Convergencia filtro adaptivo I')
        plt.subplot(2,1,2)
        plt.plot(np.log10(np.abs(LOG_ERR_I)))
        plt.grid(True)
        plt.xlabel('Simbolos')
        plt.ylabel('Error (Slicer_Out - Eq_Out)')
        plt.title('Convergencia del error I')

        plt.figure(figsize=[10,6])
        plt.subplot(2,1,1)
        plt.plot(LOG_EQ_O_Q,'.')
        plt.grid(True)
        plt.ylabel('Salida FFE')
        plt.title('Convergencia filtro adaptivo Q')
        plt.subplot(2,1,2)
        plt.plot(np.log10(np.abs(LOG_ERR_Q)))
        plt.grid(True)
        plt.xlabel('Simbolos')
        plt.ylabel('Error (Slicer_Out - Eq_Out)')
        plt.title('Convergencia del error Q')

        # plt.figure(figsize=[10,6])
        # plt.plot(ad_fil_I.get_Coef_FFE())
        # plt.grid(True)

        plt.figure(figsize=[10,6]) 
        plt.plot(LOG_PHI) 
        plt.title('FCR Output')
        plt.ylabel('Rad')
        plt.grid(True)      

        plt.figure(figsize=[6,6])
        plt.title('Constellation FSE Output + Slicer Input')
        plt.plot(LOG_EQ_O_I[timer_fcr_on+100:len(LOG_EQ_O_I)], LOG_EQ_O_Q[timer_fcr_on+100:len(LOG_EQ_O_Q)],'.',linewidth=2.0,label='Sin Corrección')
        plt.plot(LOG_EQ_FCR_I[timer_fcr_on+100:len(LOG_EQ_FCR_I)], LOG_EQ_FCR_Q[timer_fcr_on+100:len(LOG_EQ_FCR_Q)],'.',linewidth=2.0,label='Con Corrección')
        plt.xlim((-2, 2))
        plt.ylim((-2, 2))
        plt.grid(True)
        plt.xlabel('Real')
        plt.ylabel('Imag')

        
        plt.show(block=False)
        input('Press enter to finish: ')
        plt.close()

if __name__ == '__main__':
    main()


#correcciones, ber en escala logaritmica (no porcentaje)
#mostrar datos tanto del receptor como del transmisor en la segunda pestaña
#(agregar un widget que me permita alternar entre uno y otro)