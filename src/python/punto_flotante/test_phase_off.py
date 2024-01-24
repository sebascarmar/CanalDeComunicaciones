import numpy as np
import matplotlib.pyplot as plt

from classes.phase_off import phase_off

symbI = [1.0,-1.0,-1.0,1.0]
symbQ = [1.0,1.0,-1.0,-1.0]
symbI_des = []
symbQ_des = []


offset_gen =  phase_off()# Instancia objeto que genera desplazamiento de fase.



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

