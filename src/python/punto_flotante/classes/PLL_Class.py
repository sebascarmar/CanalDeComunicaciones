import numpy as np
import math  as mt


class PLL_Class:
    def __init__(self, Kp, Ki, Lat, L, I1_in, I2_in, Q1_in, Q2_in):
        self.Kp      = Kp                   # Ganancia proporcional
        self.Ki      = Ki                   # Ganancia integral
        self.Lat     = Lat                  # Latencia (minimo es 1 pero se pone abajo)
        self.L       = L                    # Cantidad de simbolos

        self.I1_in   = I1_in                # Simbolo real antes del slicer
        self.I2_in   = I2_in                # Simbolo real despues del slicer
        self.Q1_in   = Q1_in                # Simbolo imaginario antes del slicer
        self.Q2_in   = Q2_in                # Simbolo imaginario despues del slicer

        # Modelado del PLL
        tita1 = mt.atan2(self.Q1_in , self.I1_in)       # Ángulo antes del slicer
        tita2 = mt.atan2(self.Q2_in , self.I2_in)       # Ángulo despues del slicer
        self.tita_in = tita2 - tita1

        self.error      = np.zeros(self.L)
        self.error_prop = np.zeros(self.L)
        self.error_int  = np.zeros(self.L)
        self.nco_in     = np.zeros(self.L)
        self.tita_out   = np.zeros(self.L)
        self.tita_delay = np.zeros(self.L)

        self.DELAY_LINE = np.zeros(self.Lat + 1)

    
    def PLL_process(self):
       
        for n in range(self.L):
            #Entrada - Salida
            self.error     [n] = self.tita_in[n] - self.tita_delay[n - 1]

            #Cálculo del error proporcional
            self.error_prop[n] = self.Kp * self.error[n]
            
            #Cálculo del error integral
            self.error_int [n] = self.Ki * (self.error_prop[n] + self.nco_in[n - 1]) + self.error_int[n - 1]
            
            #NCO
            self.nco_in    [n] = self.error_prop[n] + self.error_int[n]
            
            #Salida
            self.tita_out  [n] = self.tita_out[n - 1] + self.nco_in[n]
            
            #Modelado del retardo
            self.DELAY_LINE     = np.roll(self.DELAY_LINE, -1)
            self.DELAY_LINE[-1] = self.tita_out[n]
            self.tita_delay[n]  = self.DELAY_LINE[0]

        return self.tita_out, np.conj(self.tita_out)