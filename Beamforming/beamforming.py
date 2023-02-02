# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 11:09:29 2022

@author: Sergio
"""

import numpy as np
import scipy
import scipy.io
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
import wave
import sincronizacion_Ndevices as sincro


plt.close('all')

Fs = 44100
Ndevices = 3

#%% RECORTE DE LA SEÑAL DE SINCRONIZACIÓN + MONTAJE

sincronizadas = sincro.sincro(Ndevices) #Cada columna es la grabación de un dispositivo

recorte = 1575138



#90 grados
phi = np.pi / 4


c = 342
d = 0.08
f = 2000 #2kHz
w = np.zeros((Ndevices),dtype = 'complex_')
barrido = np.arange(0, 180, 5)
barrido_rad = (barrido * np.pi) / 180
y = np.zeros(len(sincronizadas[recorte:, 1]))

n = np.arange(Ndevices)

#%% RETARDO (delay)

retardo = (n * d * np.cos(phi)) / c

#PESOS
for i in range (Ndevices):
    w[i] = np.exp(1j * 2 * np.pi * f * retardo[i])

w = w / Ndevices

#%% PROMEDIO (sum)


for j in range (Ndevices):
    y = y + (sincronizadas[recorte:, j] * w[j])
    
plt.figure(14)
plt.plot(y)
plt.title('Señal tras "SUM"')
plt.xlabel('Muestras')
plt.ylabel('Amplitud')


#%% PATRÓN DE DIRECTIVIDAD EXPERIMENTAL

# SE EMPEZÓ LA PRUEBA EN 270 Y SE LLEGÓ HASTA 90 grados (barrido de 180 grados)

segmento = 160000

A = np.zeros(len(barrido))
barrido_exp = np.linspace(np.pi / 2, 3 * np.pi / 2, 36)
barrido_exp_sim = np.linspace(np.pi / 2, 5 * np.pi / 2, 72)
barrido_real = np.linspace(0, np.pi, 36)

pos = 0
for i in range(len(barrido)):
    valores = np.abs(y[pos:(pos + segmento)])
    valores = np.sort(valores)
    valores = valores[::-1]
    A[i] = np.mean(valores[:30000])
    pos = pos + segmento

Amax = max(A)

#Se da la vuelta a las amplitudes por hacer el barrido de 270 hasta 90
Dexp = A[::-1] / Amax

#Parte simétrica de la directividad (se ha hecho la prueba desde 90 grados)
Dsim_exp = Dexp[::-1]
Dtot_exp = np.concatenate((Dexp, Dsim_exp), axis=0)


plt.figure(18)
plt.polar(barrido_exp, abs(Dexp))
plt.title('Diagrama directividad experimental')

plt.figure(19)
plt.polar(barrido_exp_sim, abs(Dtot_exp))
plt.title('Diagrama directividad experimental')
    
#%% PATRÓN DIRECTIVIDAD TEÓRICO

barrido_exp = np.linspace(0, np.pi, 36) #Barrido experimental
barrido_polar = np.linspace(0, 2*np.pi, 72) #Barrido para representar
D = np.zeros(len(barrido_exp))
Dtot = np.zeros(len(barrido_polar))

#Fórmula página 15 transparencias
for i in range (len(barrido_exp)):
    Dsum = 0
    for n in range (Ndevices):
        Dsum = Dsum + np.exp(2 * np.pi * 1j * f * n * d * np.cos(barrido_exp[i]) / c) * np.conj(w[n])
    
    D[i] = Dsum

#Parte simétrica de la directividad
Dsim = D[::-1]
Dtot = np.concatenate((D, Dsim), axis=0)

plt.figure(15)
plt.polar(barrido_polar, abs(Dtot))
plt.title('Diagrama directividad')

#%% Varianza del ruido
muestras_ruido = 50000

Vbefore = np.var(sincronizadas[7670000:7670000+muestras_ruido])
Vafter = np.var(y[6120000:6120000+muestras_ruido])

difV = Vbefore - Vafter
porcentaje = difV * 100 / Vbefore

print('La potencia del ruido ha disminuido en un ' + str(porcentaje)+ '%' )

#%% MSE directividad

suma = 0
for phi_ in range (len(barrido_polar)):
    suma = suma + (Dtot[phi_] - Dtot_exp[phi_])

MSE = suma **2 / len(barrido_polar)

print('El MSE de la directividad es: ' + str(MSE))

#%%Factor de directividad
denom = 0
num = (abs(Dtot_exp[0]))**2

for phi2 in range (len(barrido_polar)):
    denom = (abs(Dtot_exp[phi2]))**2 + denom
    
denom = denom / len(barrido_polar)
Fd = (num / denom)

#%% Representación

plt.figure(20)
plt.polar(barrido_polar, abs(Dtot))
plt.polar(barrido_exp_sim, abs(Dtot_exp))
plt.title('Comparación')
    
