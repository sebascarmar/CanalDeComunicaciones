import matplotlib.pyplot as plt

data = []

sigma = ''

with open('D:/run/gng_test/datos.txt') as f:
  for line in f: 

    num = int(line)

    if (sigma == ''):
       sigma = num
       continue

    #print(f"num = {num}, line = {line}")

    # Separar parte entera, fraccional y signo
    signo = (num & 0x80000000) >> 31

    integer = (num & 0x7FC00000) >> 22
    fractional = (num & 0x003FFFFF) / (2**22)
    
    #print(f"num = {num}, signo = {signo}, integer = {integer}, fractional = {fractional}")

    # Convertir a float
    if (signo == 1):
        pass
        num_float = -(2**9) + integer + fractional
    else:
        num_float = integer + fractional

    #print(f"num_float = {num_float}")

    data.append(num_float)

# Crear histograma  
plt.hist(data, bins=100) # bins=cantidad divisiones del grafico

# Título y etiquetas
plt.title("Histograma de Datos")
plt.xlabel("Valor")
plt.ylabel("Frecuencia")

# Mostrar gráfico
plt.show()