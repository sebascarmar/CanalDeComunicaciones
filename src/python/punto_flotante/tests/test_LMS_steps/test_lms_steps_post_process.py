import numpy                as np
import math
import matplotlib.pyplot    as plt

path_logs = "logs/test_ber_"

path_ber_i      = path_logs + "BER_I.txt"
path_ber_q      = path_logs + "BER_Q.txt"
flog_lms_steps  = path_logs + "lms_steps.txt"

LOG_BER_I       = []
LOG_BER_Q       = []
LOG_LMS_STEPS   = []

ber_teo   = []

with open(path_ber_i) as f:
    for line in f.readlines():
        LOG_BER_I.append(float(line))

with open(path_ber_q) as f:
    for line in f.readlines():
        LOG_BER_Q.append(float(line))
        
with open(flog_lms_steps) as f:
    for line in f.readlines():
        LOG_LMS_STEPS.append(float(line))
        

plt.figure(figsize=[14,6])
plt.title('BER vs LMS Steps - Adaptative filter receiver')
plt.semilogx(LOG_LMS_STEPS, LOG_BER_I, 'b', linewidth=2.0)
plt.semilogx(LOG_LMS_STEPS, LOG_BER_Q, 'g', linewidth=2.0)
plt.xlabel('LMS steps')
plt.ylabel('BER')
plt.grid(True)
plt.xlim(1e-5, 1)
plt.ylim(0.000001,0.2)
plt.legend(['BER I','BER Q'])

plt.show(block=False)
input('Press enter to finish: ')
plt.close()


