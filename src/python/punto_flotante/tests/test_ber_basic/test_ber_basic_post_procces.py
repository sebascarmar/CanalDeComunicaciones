import numpy                as np
import math
import matplotlib.pyplot    as plt

path_logs = "logs/test_ber_basic_"

path_ber_i = path_logs + "BER_I.txt"
path_ber_q = path_logs + "BER_Q.txt"
path_ebno  = path_logs + "ebno.txt"

LOG_BER_I = []
LOG_BER_Q = []
LOG_EBNO  = []

ber_teo   = []

with open(path_ber_i) as f:
    for line in f.readlines():
        LOG_BER_I.append(float(line))

with open(path_ber_q) as f:
    for line in f.readlines():
        LOG_BER_Q.append(float(line))
        
with open(path_ebno) as f:
    for line in f.readlines():
        LOG_EBNO.append(float(line))
        
for idx_ebno in range(len(LOG_EBNO)):
    EbNo  = 10**(LOG_EBNO[idx_ebno]/10)
    M     = 4
    k     = np.log2(M)
    x     = np.sqrt(3*k*EbNo/(M-1))
    ber_t = (4/k)*(1-1/np.sqrt(M))*(1/2)*math.erfc(x/np.sqrt(2))
    ber_teo.append(ber_t)
    
plt.figure(figsize=[14,6])
plt.title('BER vs EbNo - RRC receiver')
plt.semilogy(LOG_EBNO, ber_teo  , 'r', linewidth=2.0)
plt.semilogy(LOG_EBNO, LOG_BER_I, 'b', linewidth=2.0)
plt.semilogy(LOG_EBNO, LOG_BER_Q, 'g', linewidth=2.0)
plt.xlabel('EbNo(dB)')
plt.ylabel('BER')
plt.grid(True)
plt.xlim(0,15)
plt.ylim(0.000001,1)
plt.legend(['BER teo','BER I','BER Q'])

plt.show(block=False)
input('Press enter to finish: ')
plt.close()