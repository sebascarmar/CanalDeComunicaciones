import math
from tool._fixedInt import *

def cordic_arctan(num, iterations, tot_bits, frac_bits):

    # Tabla de valores precalculados de atan(2^(-i))
    atan_table     = [math.atan(2**(-i)) for i in range(iterations)]
    atan_table_fix = arrayFixedInt(tot_bits, frac_bits, atan_table, signedMode='S', roundMode='round', saturateMode='wrap')


    # Inicialización de variables 
    x       = DeFixedInt(tot_bits, frac_bits, 'S', 'trunc', 'saturate')
    x.value = num

    angle       = DeFixedInt(tot_bits, frac_bits, 'S', 'trunc', 'saturate')
    angle.value = 0

    factor       = DeFixedInt(tot_bits, frac_bits, 'S', 'trunc', 'saturate')
    factor.value = 1.0

    factor_aux = DeFixedInt(tot_bits*2, frac_bits*2, 'S', 'trunc', 'saturate')              
  
    medio = DeFixedInt(tot_bits, frac_bits, 'S', 'trunc', 'saturate')
    medio.value = 0.5
    

    # Iteraciones del algoritmo CORDIC
    for i in range(iterations):
        if x.fValue < 0.0:
            factor_aux.assign(factor * atan_table_fix[i])
            angle.assign(angle - factor_aux)

            factor_aux.value  = factor.fValue/(2.0**i)
            x.assign(x + factor_aux)                        # Me aseguro que satura y trunca


        else:
            factor_aux.assign(factor * atan_table_fix[i])
            angle.assign(angle + factor_aux)

            factor_aux.value  = factor.fValue/(2.0**i)
            x.assign(x - factor_aux)                        # Me aseguro que satura y trunca


        #factor.value = factor.fValue * 0.5                  # Se trabaja todo con flotante
        factor.assign(factor * medio)                         # Se trabaja DeFix, respeta resolución
        print('Ángulo: ', angle.fValue, ' - x: ', x.fValue, ' - factor nuevo: ', factor.fValue)

    return angle.fValue

# Ejemplo de uso
num        = 0.8 

tot_bits   = 8
frac_bits  = 6

iterations = 4

resultado_cordic = cordic_arctan(num, iterations, tot_bits, frac_bits)
resultado_real   = math.atan(num)

print("Resultado CORDIC:", resultado_cordic)
print("Resultado Real:", resultado_real)