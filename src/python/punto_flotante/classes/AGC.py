import numpy as np

class AGC:
    def __init__(self,TAPS_AGC = 10, target=1):
        self.TAPS = TAPS_AGC
        self.target = target
        self.counter = 0

        self.FIFO = np.zeros(self.TAPS)

    def AGC_module(self, input):
        self.FIFO = np.roll(self.FIFO,1)
        self.FIFO[0] = input

        metric = np.std(self.FIFO)
        gain = self.target/metric
        if self.counter < self.TAPS:
            self.counter += 1
            output = 0
        else:
            output = gain * input

        return output