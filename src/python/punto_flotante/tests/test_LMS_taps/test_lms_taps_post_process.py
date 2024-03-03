import numpy                as np
import math
import matplotlib.pyplot    as plt

path_logs = "logs/test_ber_"

path_ber_i      = path_logs + "BER_I.txt"
path_ber_q      = path_logs + "BER_Q.txt"
path_lms_ntaps  = path_logs + "lms_ntaps.txt"

LOG_BER_I       = []
LOG_BER_Q       = []
LOG_LMS_TAPS    = []

ber_teo   = []

with open(path_ber_i) as f:
    for line in f.readlines():
        LOG_BER_I.append(float(line))

with open(path_ber_q) as f:
    for line in f.readlines():
        LOG_BER_Q.append(float(line))
        
with open(path_lms_ntaps) as f:
    for line in f.readlines():
        LOG_LMS_TAPS.append(float(line))
        

plt.figure(figsize=[14,6])
plt.title('BER vs LMS Taps - Adaptative filter receiver')
plt.plot(LOG_LMS_TAPS, LOG_BER_I, 'b', linewidth=2.0)
plt.plot(LOG_LMS_TAPS, LOG_BER_Q, 'g', linewidth=2.0)
plt.xlabel('LMS Taps')
plt.ylabel('BER')
plt.grid(True)
plt.xlim(20,40)
plt.ylim(0.000001, 0.3)
plt.legend(['BER I','BER Q'])

plt.show(block=False)
input('Press enter to finish: ')
plt.close()


