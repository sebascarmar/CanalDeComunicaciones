import matplotlib.pyplot as plt
import numpy as np
from classes.tool._fixedInt import *

class slicer_fixed:
    def __init__(self,NB_SL_I, NBF_SL_I,
                 NB_SL_O, NBF_SL_O,
                 NB_ERR, NBF_ERR):
        
        self.slicer_i = DeFixedInt(NB_SL_I, NBF_SL_I, signedMode = 'S', roundMode='trunc', saturateMode='saturate')
        self.slicer_o = DeFixedInt(NB_SL_O, NBF_SL_O, signedMode = 'S', roundMode='trunc', saturateMode='saturate')
        self.error    = DeFixedInt(NB_ERR , NBF_ERR ,signedMode = 'S', roundMode='trunc', saturateMode='saturate')

    def slicer_PAM2(self,input):
        self.slicer_i.value = input
        if(self.slicer_i.fValue >= 0):
            self.slicer_o.value = 1.0
        else:
            self.slicer_o.value = -1.0
        return self.slicer_o.fValue

    def calculate_error(self):
        aux = self.slicer_o.fValue - self.slicer_i.fValue
        self.error.value = aux
        return self.error.fValue