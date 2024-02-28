import matplotlib.pyplot as plt

data = []

shifter_divider = -1

with open('D:/run/gng_test/datos.txt') as f:
  for line in f: 

    num = int(line)

    if (shifter_divider == -1):
       shifter_divider = num
       continue

    #print(f"num = {num}, line = {line}")

    # Separar parte entera, fraccional y signo
    sign_mask = 0x8000>>shifter_divider
    signo = (num & sign_mask) >> (15-shifter_divider)

    if (shifter_divider < 4): # con parte entera
        integer_mask = (0xF>>shifter_divider) << 11
        integer = (num & integer_mask) >> 11
        fractional = (num & 0x07FF) / (2**11)
    else:   # sin parte entera, solo parte fraccional
        fractional_mask = (0x7FF>>(shifter_divider-4)) 
        integer = 0
        fractional = (num & fractional_mask) / (2**11)
    
    #print(f"signo = {signo}, integer = {integer}, fractional = {fractional}")

    # Convertir a float
    if (signo == 1):
        num_float = (-16/(2**shifter_divider)) + integer + fractional
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