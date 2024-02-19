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
from main import main
from classes.config_Class import config
 
# using

cfg = config()

cfg.Lsim            = 20                        
cfg.enable_plots    = False                     
cfg.enable_file_log = False                     
cfg.BR              = 1000                      
cfg.beta            = 0.5                       
cfg.M               = 4                         
cfg.OS              = 4                         
cfg.nbaud           = 6                         
cfg.Norm_enable     = False                     
cfg.fs              = cfg.OS * float(cfg.BR) * 1.0e6    
cfg.fc              = (float(cfg.BR) * 1.0e6) / 2   
cfg.filter_select   = True                      
cfg.Nsymb           = 511                       
cfg.offsetI         = 0                         
cfg.offsetQ         = 0                         
cfg.phase           = 0                         
cfg.EbNo            = 5                         
cfg.firfilter_order = 10                        
cfg.NTAPS_ad_fil    = 51                        
cfg.LMS_step        = 1e-3                      
cfg.Kp              = 0.01                      
cfg.Ki              = cfg.Kp/1000                   
cfg.Lat             = 0                         
cfg.timer_fcr_on    = 10*cfg.Nsymb                  
cfg.timer_cma_off   = 20*cfg.Nsymb                  
cfg.PRBS_Q_seed     = 0b111111110               
cfg.PRBS_I_seed     = 0b110101010               

# Reset files before start test
path_logs = "logs/test_ber_"
flog_ber_i = open(path_logs + "BER_I.txt", "wt")
flog_ber_q = open(path_logs + "BER_Q.txt", "wt")
flog_ebno  = open(path_logs + "ebno.txt",  "wt")
flog_ber_i.close()
flog_ber_q.close()
flog_ebno.close()

for ebno_value in np.arange(0, 10, 1):
    cfg.EbNo = ebno_value
    cfg.print_cfg()
    main(cfg, path_logs)