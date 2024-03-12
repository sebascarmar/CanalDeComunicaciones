import numpy                as np
import math
import matplotlib.pyplot    as plt

path_logs = "logs/test_ber_"

path_ber_i = path_logs + "BER_I.txt"
path_ber_q = path_logs + "BER_Q.txt"

LOG_BER_I = []
LOG_BER_Q = []

with open(path_ber_i) as f:
    for line in f.readlines():
        LOG_BER_I.append(float(line))

with open(path_ber_q) as f:
    for line in f.readlines():
        LOG_BER_Q.append(float(line))
        
plt.figure(figsize=[14,6])
plt.title('BER vs LMS delay - Adaptative filter receiver')
plt.plot(range(0,10), LOG_BER_I, 'b', linewidth=2.0)
plt.plot(range(0,10), LOG_BER_Q, 'g', linewidth=2.0)
plt.xlabel('EbNo(dB)')
plt.ylabel('BER')
plt.grid(True)
#plt.xlim(0,15)
#plt.ylim(0.000001,1)
plt.legend(['BER I','BER Q'])

plt.show(block=False)
input('Press enter to finish: ')
plt.close()


