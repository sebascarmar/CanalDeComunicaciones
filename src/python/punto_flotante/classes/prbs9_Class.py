
class prbs9:

    def __init__(self, seed):
        self.seed = seed

    def generate(self):

        # Calcula el siguiente bit utilizando una compuerta XOR
        next_bit = ((self.seed >> 8) ^ (self.seed >> 4)) & 1
        # Desplaza el registro y agrega el siguiente bit
        self.seed = ((self.seed << 1) | next_bit) & 0b111111111

        return next_bit










