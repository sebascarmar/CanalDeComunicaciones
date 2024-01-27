import numpy as np
import matplotlib.pyplot as plt

from classes.phase_off import phase_off
fs      = 50    # Sampling freq
Delta_f = 10

# Instancia objeto que genera desplazamiento de fase.
offset_gen =  phase_off(fs, Delta_f)


###########################################################################################
#                                Test simple y "manual"                                   #
###########################################################################################

#symbI = [1.0,-1.0,-1.0,1.0]
#symbQ = [1.0,1.0,-1.0,-1.0]
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




for j in range(4):
    for x in range(4):
        (auxI, auxQ) = offset_gen.get_phase_off(symbI[x], symbQ[x])
        symbI_des.append(auxI)
        symbQ_des.append(auxQ)
    
    plt.figure(figsize=[6,6])
    plt.plot(symbI, symbQ, 'bo', linewidth=2.0, label=b'Constelacion original')
    plt.plot(symbI_des, symbQ_des, 'r.', linewidth=2.0, label=r'Constelacion original')
    plt.xlim((-2, 2))
    plt.ylim((-2, 2))
    plt.grid(True)
    plt.xlabel('Real')
    plt.ylabel('Imag')
    
    plt.show()

