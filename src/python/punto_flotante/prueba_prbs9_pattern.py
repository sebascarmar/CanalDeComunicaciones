#Este script es util para testear la prbs pero tambien para determinar una posible
#optimizacion de tiempo en el correlador de ser necesario

from initial_with_GUI.classes.prbs9_Class import prbs9
def encontrar_primer_vector_no_periodico(array):
    longitud = len(array)
    for tamaño in range(1, longitud + 1):
        vectores = [tuple(array[i:i+tamaño]) for i in range(longitud - tamaño + 1)]
        if len(vectores) == len(set(vectores)):
            return vectores[0]
    return None


#objetos de prbs9
Q_seed = 0b111111110
#objeto prbs y buffer
prbs = prbs9(Q_seed)
buffer = []

#se generan los datos periodicos de la prbs
for i in range(511):
    buffer.append(prbs.generate())
print(buffer)

#se imprime el primer vector de longitud minima que es aperiodico dentro del buffer
print(encontrar_primer_vector_no_periodico(buffer))
