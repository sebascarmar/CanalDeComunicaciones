import numpy as np
import matplotlib.pyplot as plt

from classes.phase_off import phase_off

# Cuantización
NBTot  = 8
NBFrac = 6

# Instancia objeto que genera desplazamiento de fase.
offset_gen =  phase_off(NBTot,NBFrac)


###########################################################################################
#                                Test simple y "manual"                                   #
###########################################################################################

#symbI = 2*(np.random.uniform(-1,1,Nsymb)>0.0)-1;
#symbQ = 2*(np.random.uniform(-1,1,Nsymb)>0.0)-1;
#symbI_des = []
#symbQ_des = []

#for j in range(100):
#
#    # Desfasa los 4 símbolos
#    for x in range(4):
#        (auxI, auxQ) = offset_gen.get_phase_off(symbI[x], symbQ[x])
#        symbI_des.append(auxI)
#        symbQ_des.append(auxQ)
#    
#    # Gráfica la constelación orignial y la desfasada
#    plt.figure(figsize=[6,6])
#    plt.plot(symbI, symbQ, 'bo', linewidth=2.0, label=b'Constelacion original')
#    plt.plot(symbI_des, symbQ_des, 'r.', linewidth=2.0, label=r'Constelacion original')
#    plt.xlim((-2, 2))
#    plt.ylim((-2, 2))
#    plt.grid(True)
#    plt.xlabel('Real')
#    plt.ylabel('Imag')
#    
#    plt.show()



###########################################################################################
#                                     Test automático                                     #
###########################################################################################
### Número de ciclos
iteraciones  = 270 #4100, 2060, 1050, 520,270 

### Frecuencia de offset
freq = 4 #2,3,4 (24k3,48k7,97k5,195k1,390k2)

### PRBS I
reg_PRBS_I  = np.array([0,1,0,1,0,1,0,1,1])

### PRBS Q
reg_PRBS_Q  = np.array([0,1,1,1,1,1,1,1,1])

### Logueo
symbolsI = []
symbolsQ = []

symbI_des = []
symbQ_des = []

for i in range(iteraciones):
    # Obtiene la salida de la prbs
    symbI = -1.0 if(reg_PRBS_I[8]) else 1.0
    # Calcula el nuevo bit de entrada al registro
    new_in   = reg_PRBS_I[4]^reg_PRBS_I[8]
    # Desplaza el registro e ingresa el nuevo bit con LSB
    reg_PRBS_I    = np.roll(reg_PRBS_I,1)
    reg_PRBS_I[0] = new_in
    
    # Obtiene la salida de la prbs
    symbQ = -1.0 if(reg_PRBS_Q[8]) else 1.0
    # Calcula el nuevo bit de entrada al registro
    new_in   = reg_PRBS_Q[4]^reg_PRBS_Q[8]
    # Desplaza el registro e ingresa el nuevo bit con LSB
    reg_PRBS_Q    = np.roll(reg_PRBS_Q,1)
    reg_PRBS_Q[0] = new_in
    

    ### Generación de desfasaje
    (auxI, auxQ) = offset_gen.get_phase_off(symbI, symbQ,freq)

    ### Guarda los símbolos generados
    symbolsI.append(symbI)
    symbolsQ.append(symbQ)
    ### Guarda los símbolos generados con el offset de fase
    symbI_des.append(auxI)
    symbQ_des.append(auxQ)


### Gráfica
plt.figure(figsize=[6,6])
plt.plot(symbolsI, symbolsQ, 'bo', linewidth=2.0, label='Constelacion original')
plt.plot(symbI_des, symbQ_des, 'r.', linewidth=2.0, label='Constelacion desfasada')
plt.xlim((-2, 2))
plt.ylim((-2, 2))
plt.legend()
plt.grid(True)
plt.xlabel('Real')
plt.ylabel('Imag')

plt.show()

