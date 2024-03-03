import sys
import os
import numpy as np
 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
parent = os.path.dirname(parent)
 
# adding the parent directory to 
# the sys.path.
sys.path.append(parent)
 
# now we can import the module in the parent
# directory.
from main_rx_rrc import main
from classes.config_Class import config
 
# using

cfg = config()

cfg.Lsim                = 2000                      
cfg.enable_plots        = False                     
cfg.enable_file_log     = False                     
cfg.BR                  = 25e6                      
cfg.beta                = 0.9                       
cfg.M                   = 4                         
cfg.OS                  = 4                         
cfg.nbaud               = 20                         
cfg.Norm_enable         = True                     
cfg.fs                  = cfg.OS * float(cfg.BR)
cfg.fc                  = float(cfg.BR) / 2   
cfg.filter_select       = True                      
cfg.Nsymb               = 511                       
cfg.offsetI             = 0                         
cfg.offsetQ             = 0                         
cfg.phase               = 0                         
#cfg.EbNo            = 5                         

# Reset files before start test
path_logs = "logs/test_ber_basic_"
flog_ber_i          = open(path_logs + "BER_I.txt", "wt")
flog_ber_q          = open(path_logs + "BER_Q.txt", "wt")
flog_ebno           = open(path_logs + "ebno.txt",  "wt")
flog_align_pos_i    = open(path_logs + "align_pos_i.txt"        , "wt")
flog_align_pos_q    = open(path_logs + "align_pos_q.txt"        , "wt")
flog_ber_i.close()
flog_ber_q.close()

flog_ebno.close()
flog_align_pos_i.close()
flog_align_pos_q.close()

for ebno_value in np.arange(0, 15, 1):
    cfg.EbNo = ebno_value
    cfg.print_cfg()
    main(cfg, path_logs)