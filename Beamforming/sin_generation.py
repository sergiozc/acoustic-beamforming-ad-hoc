# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 09:05:35 2022

@author: Sergio
"""

import numpy as np
import scipy
import scipy.io
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
from scipy.optimize import minimize
import wave

plt.close('all')

def waiterSin(f, t, twait):
    
    'Función que genera un seno a una frecuencia f, 
    'con una duración de t segundos y muestreado
    'cada twait segundos'
    
    Fs = 44100
    nwait = twait * Fs
    Ts = 1 / Fs
    n = t / Ts
    n = np.arange(n)
    t_vector = n * Ts
    A = np.iinfo(np.int16).max

    s = A * np.sin(2 * np.pi * f * t_vector)
    
    for i in range(0, len(s), 2*nwait):
        for j in range(nwait):
            s[i + j] = 0            
            
    plt.figure(1)
    plt.plot(s)
    plt.title('Seno muestreado')
    plt.xlabel('Muestras')
    plt.ylabel('Amplitud')

    file_name1 = 'seno2k'
    wavfile.write('seno/' + file_name1 + '.wav', Fs, s.astype('int16'))
    
    pass

tactivo = 2
twait = 2
barrido = 180
intervalo_angulo = 5

t = (barrido / intervalo_angulo) * twait * tactivo

waiterSin(2000, t, twait)