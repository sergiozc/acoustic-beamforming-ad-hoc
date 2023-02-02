# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 15:45:53 2022

@author: Usuario
"""

import numpy as np
import scipy
import scipy.io
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
from scipy.optimize import minimize
import wave


def excitacion(Fs, Tchirp):
    
    'Función que genera una excitación en forma de chirp'
    'desde 5kHz hasta 16kHz'
    
    Nsamp = int(Tchirp * Fs)
    Fsw = np.array([5000, 16000]) / Fs
    Inclog = np.log(Fsw[1] / Fsw[0])
    n = np.arange(0, Nsamp+1, 1)
    excit = np.sin(2 * np.pi * Fsw[0] * Nsamp * (np.exp(Inclog * n / Nsamp) - 1) / Inclog)
    
    excit = excit * np.iinfo(np.int16).max
    
    return excit

plt.close('all')

x = excitacion(44100, 0.1)

x2 = np.zeros(len(x) + 500)
x2[500:] = x

rx = scipy.signal.correlate(x2, x, mode = 'full')
N = len(rx)
k = np.linspace(-(N/2) +1, (N/2)-1, N)

plt.figure(1)
plt.title('Correlación cruzada')
plt.xlabel('Muestras')
plt.ylabel('Correlación')
plt.plot(k,rx)
