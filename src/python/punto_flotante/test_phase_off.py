import numpy as np
import matplotlib.pyplot as plt

from classes.phase_off import phase_off

# Instancia objeto que genera desplazamiento de fase.
offset_gen =  phase_off()

Nsymb   = 1025 #4100, 2060, 1050, 520,270 

symbolsI = 2*(np.random.uniform(-1,1,Nsymb)>0.0)-1;
symbolsQ = 2*(np.random.uniform(-1,1,Nsymb)>0.0)-1;

symbI_des = []
symbQ_des = []
###########################################################################################
#                                Test simple y "manual"                                   #
###########################################################################################

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

for x in range(len(symbolsI)):
    (auxI, auxQ) = offset_gen.get_phase_off(symbolsI[x], symbolsQ[x], 1) #1 a 5
    #(auxI, auxQ) = offset_gen.get_fixed_off(symbolsI[x], symbolsQ[x],1) #1 a 5
    symbI_des.append(auxI)
    symbQ_des.append(auxQ)

offset_gen.plot_sin()

offset = 0
plt.figure(figsize=[6,6])
plt.plot(symbolsI, symbolsQ, 'bo', linewidth=2.0, label=b'Constelacion original')
plt.plot(symbI_des, symbQ_des, 'r.', linewidth=2.0, label=b'Constelacion desfasada')
plt.xlim((-2, 2))
plt.ylim((-2, 2))
plt.grid(True)
plt.xlabel('Real')
plt.ylabel('Imag')

plt.show()
