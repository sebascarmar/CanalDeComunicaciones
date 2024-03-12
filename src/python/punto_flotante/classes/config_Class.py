class config:
    
    def __init__(self):
        self.Lsim                   = 0
        self.enable_plots           = 0
        self.enable_file_log        = 0
        self.BR                     = 0
        self.beta                   = 0
        self.M                      = 0
        self.OS                     = 0
        self.nbaud                  = 0
        self.Norm_enable            = 0
        self.fs                     = 0
        self.fc                     = 0
        self.filter_select          = 0
        self.Nsymb                  = 0
        self.offsetI                = 0
        self.offsetQ                = 0
        self.phase                  = 0
        self.EbNo                   = 0
        self.firfilter_order        = 0
        self.NTAPS_ad_fil           = 0
        self.LMS_step               = 0
        self.Kp                     = 0
        self.Ki                     = 0
        self.Lat                    = 0
        self.delay_LMS              = 0
        self.timer_fcr_on           = 0
        self.PRBS_Q_seed            = 0
        self.PRBS_I_seed            = 0
        self.enable_phase_shift     = 0
        self.enable_ch_filter       = 0
        self.enable_noise           = 0
        self.enable_adap_filter     = 0
        
    def print_cfg(self):
        print('#'*20)
        print("Config Test")
        print('#'*20)
        print('Lsim                 : ', self.Lsim                  )
        print('enable_plots         : ', self.enable_plots          )
        print('enable_file_log      : ', self.enable_file_log       )
        print('BR                   : ', self.BR                    )
        print('beta                 : ', self.beta                  )
        print('M                    : ', self.M                     )
        print('OS                   : ', self.OS                    )
        print('nbaud                : ', self.nbaud                 )
        print('Norm_enable          : ', self.Norm_enable           )
        print('fs                   : ', self.fs                    )
        print('fc                   : ', self.fc                    )
        print('filter_select        : ', self.filter_select         )
        print('Nsymb                : ', self.Nsymb                 )
        print('offsetI              : ', self.offsetI               )
        print('offsetQ              : ', self.offsetQ               )
        print('phase                : ', self.phase                 )
        print('EbNo                 : ', self.EbNo                  )
        print('firfilter_order      : ', self.firfilter_order       )
        print('NTAPS_ad_fil         : ', self.NTAPS_ad_fil          )
        print('LMS_step             : ', self.LMS_step              )
        print('Kp                   : ', self.Kp                    )
        print('Ki                   : ', self.Ki                    )
        print('Lat                  : ', self.Lat                   )
        print('delay_LMS            : ', self.delay_LMS             )
        print('timer_fcr_on         : ', self.timer_fcr_on          )
        print('PRBS_Q_seed          : ', self.PRBS_Q_seed           )
        print('PRBS_I_seed          : ', self.PRBS_I_seed           )
        print('Enable_phase_shift   : ', self.enable_phase_shift    )
        print('Enable_ch_filter     : ', self.enable_ch_filter      )
        print('Enable_noise         : ', self.enable_noise          )
        print('Enable_adap_filter   : ', self.enable_adap_filter    )
        print('#'*20)