# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 17:43:20 2022

@author: Sergio
"""

import numpy as np
import scipy
import scipy.io
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
import wave

plt.close('all')

Fs = 44100
#Longitud de la señal (2s)
len_tren = 88200
tren = np.zeros(len_tren)
#Longitud en muestras de cada impulso
len_impulso = 10
#Número de impulsos
Nimpulsos = 3
#margen de muestras para que suene el impulso correctamente
margen = 2000 

intervalo = int((len_tren - margen) / Nimpulsos)
pos_ini = 10000

for i in range(3):
    pos = pos_ini + intervalo*i
    for j in range(10):
        tren[pos + j] = np.iinfo(np.int16).max
        
plt.figure(1)
plt.plot(tren)
plt.title('Tren de impulsos')
plt.xlabel('Muestras')
plt.ylabel('Amplitud')
        
#%% Tren largo        
        
Nimpulsos_tren = 15
Fs = 44100
#Unos 5.1 segundos aproximadamente
len_tren_largo = 230000
tren_largo = np.zeros(len_tren_largo + 20000)

margen_largo = 2000
intervalo_largo = int((len_tren_largo - margen) / Nimpulsos_tren)
        
for z in range(Nimpulsos_tren):
    pos_largo = pos_ini + intervalo_largo * z
    for q in range(10):
        tren_largo[pos_largo + q] = np.iinfo(np.int16).max

plt.figure(2)
plt.plot(tren_largo)
plt.title('Tren de impulsos')
plt.xlabel('Muestras')
plt.ylabel('Amplitud')

file_name1 = 'tren_impulsos'
wavfile.write('tren/' + file_name1 + '.wav', Fs, tren.astype('int16'))

file_name2 = 'tren_largo'
wavfile.write('tren_largo/' + file_name2 + '.wav', Fs, tren_largo.astype('int16'))

