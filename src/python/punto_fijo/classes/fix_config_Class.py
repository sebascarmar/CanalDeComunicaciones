from tool._fixedInt                         import *

class config:
    
    def __init__(self):
        self.Lsim                   = 0
        self.enable_plots           = 0
        self.enable_file_log        = 0

        
    def print_cfg(self):
        print('#'*20)
        print("Config Test")
        print('#'*20)
        print('Lsim                 : ', self.Lsim                  )
        print('enable_plots         : ', self.enable_plots          )
        print('enable_file_log      : ', self.enable_file_log       )

        print('#'*20)