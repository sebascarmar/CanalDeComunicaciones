import numpy as np

class PLL_Class:
    def __init__(self, Kp, Ki, Lat):
        self.Kp      = Kp                           # Ganancia proporcional
        self.Ki      = Ki                           # Ganancia integral
        self.Lat     = Lat                          # Latencia

        self.error      = np.zeros(2)
        self.error_prop = np.zeros(2)
        self.error_int  = np.zeros(2)
        self.nco_in     = np.zeros(2)
        self.tita_out   = np.zeros(2)
        self.tita_delay = np.zeros(2)
        self.tita_delay = np.zeros(2)               # Realimentación
        self.DELAY_LINE = np.zeros(self.Lat + 1)  

    
    def PLL_process(self, I1_in, I2_in, Q1_in, Q2_in):

        # Cálculo de ángulo
        tita1 = np.angle(I1_in + 1j * Q1_in)        # Ángulo antes del slicer
        #print("Tita 1", tita1)
        tita2 = np.angle(I2_in + 1j * Q2_in)        # Ángulo despues del slicer
        #print("Tita 2", tita2)
        tita_in = tita2 - tita1

        # Se actualizan los valores
        self.error      = np.roll(self.error,      1)
        self.error_prop = np.roll(self.error_prop, 1)
        self.error_int  = np.roll(self.error_int,  1)
        self.nco_in     = np.roll(self.nco_in,     1)
        self.tita_out   = np.roll(self.tita_out,   1)

        # Entrada - Salida
        self.error     [0] = tita_in - self.tita_delay[1]

        # Cálculo del error proporcional
        self.error_prop[0] = self.Kp * self.error[0]

        # Cálculo del error integral
        self.error_int [0] = self.Ki * self.error[0] + self.error_int[1]

        # NCO
        self.nco_in    [0] = self.error_prop[0] + self.error_int[0]

        # Salida
        self.tita_out  [0] = self.tita_out[1] + self.nco_in[0]

        #Modelado del retardo
        self.DELAY_LINE     = np.roll(self.DELAY_LINE, -1)
        self.DELAY_LINE[-1] = self.tita_out  [0]
        self.tita_delay[0]  = self.DELAY_LINE[0]


        return self.tita_out[0]#, np.conj(self.tita_out)       
