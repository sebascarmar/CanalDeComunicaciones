from tool._fixedInt                         import *

from classes.phase_off                      import  phase_off
from classes.prbs9_class                    import  prbs9
from classes.polyfilter_class               import  poly_filter

from punto_fijo.classes.fix_config_Class    import config

from modules.tx_rcosine_procom              import *


def main(cfg, path_logs):
    ##################################################################
    #                           INITIAL DEFS                         #
    ##################################################################
    Lsim                = cfg.Lsim                        
    enable_plots        = cfg.enable_plots
    enable_file_log     = cfg.enable_file_log
    BR                  = cfg.BR                 # BR baudrate
    beta                = cfg.beta               # Rolloff
    OS                  = cfg.OS                 # Oversampling
    nbaud               = cfg.nbaud              # Bauds
    fs                  = cfg.fs                 # Sampling freq
    fc                  = cfg.fc                 
    Norm_enable         = cfg.Norm_enable        # Norm_enablealization enable
    filter_select       = cfg.filter_select      # True: Root raised cosine, False: Raised cosine
    PRBS_I_seed         = cfg.PRBS_I_seed        
    PRBS_Q_seed         = cfg.PRBS_Q_seed        
    
    ##################################################################
    #                   CREACION DE OBJETOS                          #
    ##################################################################
    
    # Definición del filtro RRC para Tx y Rx
    (tf, filt, dot) = filtro_pulso(fc, fs, beta, OS, nbaud, Norm_enable, filter_select, n_taps=0)
    
    rcc_coefs = arrayFixedInt(8, 7, filt, signedMode='S', roundMode='trunc', saturateMode='wrap')
    
    # PRBS9
    prbs9_i = prbs9(PRBS_I_seed)
    prbs9_q = prbs9(PRBS_Q_seed)
    
    tx_filter_i = poly_filter(nbaud, OS, list_rc_ph0, list_rc_ph1, list_rc_ph2, list_rc_ph3)
    tx_filter_q = poly_filter(nbaud, OS, list_rc_ph0, list_rc_ph1, list_rc_ph2, list_rc_ph3)
    
    for isim in range(Lsim):