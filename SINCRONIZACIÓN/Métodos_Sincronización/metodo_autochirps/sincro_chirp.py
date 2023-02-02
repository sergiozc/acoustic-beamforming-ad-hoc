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


def correlaMax(rx, N):
    
    'Función que devuelve el pico de la correlación de dos señales. Si tiene'
    'decimales, redondea este máximo hacia arriba'
    
    peak = np.where(rx == max(rx))
   # print(peak[0])
    delay = int(np.ceil(float(peak[0]) - N / 2.0))
    return delay

def RawToWav(file_raw):
    
    'Función que convierte datos en bruto de audio en formato wav, conociendo'
    'previamente sus parámetros'

    with open(file_raw + ".raw", "rb") as inp_f:
        data = inp_f.read()
        with wave.open(file_raw + ".wav", "wb") as out_f:
            out_f.setnchannels(1)
            out_f.setsampwidth(2)
            out_f.setframerate(44100)
            out_f.writeframesraw(data)
        
        with wave.open(file_raw + ".wav", "rb") as in_f:
            print(repr(in_f.getparams()))


def excitacion(Fs, Tchirp):
    
    'Función que genera una excitación en forma de chirp'
    'desde 5kHz hasta 16kHz'
    
    Nsamp = int(Tchirp * Fs)
    Fsw = np.array([5000, 16000]) / Fs
    Inclog = np.log(Fsw[1] / Fsw[0])
    n = np.arange(0, Nsamp+1, 1)
    excit = np.sin(2 * np.pi * Fsw[0] * Nsamp * (np.exp(Inclog * n / Nsamp) - 1) / Inclog)
    
    excit = excit * np.iinfo(np.int16).max
    # plt.figure(15)
    # plt.plot(excit)
    # plt.title('Chirp')
    # plt.xlabel('Muestras')
    # plt.ylabel('Amplitud')
    
    file_name1 = 'chirp_creado'
    wavfile.write('chirp/' + file_name1 + '.wav', Fs, excit.astype('int16'))
    
    return excit



def grad_tf(tdoaest, tdoamed, tf_est):
    
    'Derivadas correspondientes al tiempo de vuelo'
    
    N = len(tf_est)
    
    grd = np.zeros((N, N))
    
    for m in range(N):
        for n in range(N):
            for i in range(N):
                tau_dif = tdoaest[m, n, i] - tdoamed[m, n, i]
                grd[m, n] = grd[m, n] + tau_dif
                
    grd = grd * 4
    
    return grd

def grad_Tc(tdoaest, tdoamed):
    
    'Derivadas correspondientes a los instantes de comienzo'
    
    N = len(tdoaest)
    grd = np.zeros(N)
    
    for n in range(N):
        for k in range(N):
            for i in range(N):
                tau_dif = tdoaest[k, i, n] - tdoamed[k, i, n]
                grd[n] = grd[i] = tau_dif
    
    grd = grd * 4
    
    return grd


def fcriterion(tdoamed, tf_est, tcest):
    
    'Función de referencia la cual se debe minimizar'
    
    N = len(tcest)
    F = 0
    
    for k in range(N):
        for i in range(N):
            for j in range(N):
                tdoaest[k, i, j] = tf_est[i, k] - tf_est[j, k] - tcest[i] + tcest[j]
                F = F + (tdoaest[k, i, j] - tdoamed[k, i, j]) ** 2
            
    return F, tdoaest

def diffNet(Ndevices, timeStamp):
    
    'Función que calcula el retardo en muestras producido por server-app dada una'
    'marca de tiempo absolutan para cada dispositivo'
    
    serverDelay = np.zeros(Ndevices)
    
    for i in range(Ndevices):
        serverDelay[i] = timeStamp[Ndevices-1] - timeStamp[i]
    
    serverDelay = np.floor(serverDelay * 44100)
    
    return serverDelay


            
RawToWav('Device0')
RawToWav('Device1')
RawToWav('Device2')

plt.close('all')

###############################################################################################################
            
Ndevices = 3
Fs = 44100
record = np.zeros((700000, Ndevices))
serverDelay = np.zeros(Ndevices)
tam = np.arange(Ndevices) #Tamaño de cada grabación
tam_postdelay = np.arange(Ndevices) #Tamaño después de acortar con el delay inicial
correla = np.arange(Ndevices)
lim_exc = 44100 * 4 #Acortamos a 3 segundos para captar el impulso
exc = np.zeros((lim_exc, Ndevices)) #Matriz donde guardamos el impulso de cada señal
ntoa = np.zeros((Ndevices, Ndevices)) #Tiempo de llegada de los chirp para cada móvil (en muestras)
toamed = np.zeros((Ndevices, Ndevices))
tdoamed = np.zeros((Ndevices, Ndevices, Ndevices))
tdoaest = np.zeros((Ndevices, Ndevices, Ndevices))
tf_est = np.zeros((Ndevices, Ndevices)) #Tiempos de vuelo
tcest = np.zeros((Ndevices)) #Tiempos de comienzo
delay_final = np.arange(Ndevices)
mu = 0.001    # Factor de convergencia
RelInc = 0.01 # Criterio de convergencia
#Chirp original de 0.1s de duración    
chirp = excitacion(Fs, 0.1)
Lexc = len(chirp)

################################################################################################################

#Parámetros eje de tiempos absoluto
#PRUEBA 1
timeStamp = np.array([11.245, 11.363, 11.473])
#PRUEBA 3
#timeStamp = np.array([7.826, 7.929, 8.039])
#PRUEBA 4
#timeStamp = np.array([12.126, 12.242, 12.355])

#SEPARADOS 2
#timeStamp = np.array([56.303, 56.390, 56.490])


serverDelay = diffNet(Ndevices, timeStamp)


for i in range(Ndevices):
    #Guardamos en volatil el contenido de la grabación i
    Fs, volatil = wavfile.read('Device'+ str(i) + '.wav')
    #Se implementa un eje de tiempos absoluto, eliminando los retardos de red
    volatil = volatil[int(serverDelay[i]):]
    #Guardamos el número de muestras de la grabación i
    tam[i] = len(volatil)
    #Guardamos la parte de la excitación (los 3 pitidos únicamente)
    exc[:, i] = volatil[:lim_exc]
    #Guardamos en cada columna de 'record' las grabaciones (hasta la fila correspondiente
    #al número de muestras de cada grabación, el resto son ceros)
    record[:tam[i], i] = volatil
    
    #MEDIMOS LOS TOAs haciendo la correlación de cada señal con el chirp original
    #para ver en qué instante comienza cada pitido
    correla = scipy.signal.correlate(exc[:,i], chirp, mode = 'full')
    correla = correla[Lexc:]
    
    plt.figure(i+1)
    plt.subplot(211)
    plt.plot(volatil[:lim_exc])
    plt.subplot(212)
    plt.plot(correla)
    
    
    #Nos quedamos con los índices de los valores de la correlación ordenados
    #de mayor a menor, es decir, el primer índice o instante se corresponde con el índice
    #del máximo valor de la correlación
    indices = np.argsort(correla) #Se ordena de menor a mayor
    indices = indices[::-1] #Ordenado de mayor a menor
    ntoa[i, 0] = indices[0] #El valor máximo de la correlación se corresponde con un TOA
    nfound = 1 #Número de TOAs encontrados
    nsearch = 1 #Por donde empieza la búsqueda
    
    #Iremos comparando valor por valor, en los máximos.
    #Si la distancia es mayor que Lexc, se cumple la condición y se incrementa el contador.
    #Al incrementarse el contador, se incorpora el valor a los toas.
    #Por último se ordenan por orden de llegada
    while nfound < Ndevices:
        cont = 0
        for n in range(nfound):
            cond = np.abs(indices[nsearch] - ntoa[i, n]) >= Lexc #Booleana
            cont = cont + cond
        if cont == (nfound):
            nfound = nfound + 1
            ntoa[i, nfound-1] = indices[nsearch]
        else:
            nsearch = nsearch + 1
    
    ntoa[i, :] = np.sort(ntoa[i, :])
    #Expresado en tiempo
    toamed = (ntoa - 1) / Fs 
    
##################Fin del primer bucle#####################################

toaRef = np.argsort(toamed[:, 0]) #Hace referencia a las señales ordenadas por instante de comienzo
print('Comienza el Device ' + str(toaRef[0]))


#DIFERENCIA DE LOS TIEMPOS DE LLEGADA
for k in range (Ndevices):
    for i in range (Ndevices):
        for j in range (Ndevices):
            tdoamed[k, i, j] = toamed[i, k] - toamed[j, k]

#TIEMPOS DE VUELO            
for i in range (Ndevices):
    for j in range (Ndevices):
        tf_est[i, j] = (tdoamed[j, i, j] - tdoamed[i, i, j]) / 2.0
        
#INSTANTES DE COMIENZO (tcest[0] = 0)
for i in range(1, Ndevices):
    tcest[i] = (toamed[i-1,i-1] - toamed[i,i-1] + toamed[i-1,i] - toamed[i,i]) / 2 + tcest[i-1]
    
print(tcest)
# %% DESCENSO EN GRADIENTE

tf_est = tf_est + 10 * np.random.randn(Ndevices, Ndevices) / Fs
tcest = tcest + 10 * np.random.randn(Ndevices) / Fs
tcest[0] = 0
#Estimas iniciales y tdoaest
Func_ant, tdoaest = fcriterion(tdoamed, tf_est, tcest)

RelInc = 10**20
niter = 0
while RelInc > 0.0001:
    muc = mu * np.exp(-0.01 * niter) #Velocidad de aprendizaje
    tf_est = tf_est - muc * grad_tf(tdoaest, tdoamed, tf_est)
    tcest = tcest - muc * grad_Tc(tdoaest, tdoamed)
    tcest = tcest - tcest[0]
    Func, tdoaest = fcriterion(tdoamed, tf_est, tcest)
    niter = niter + 1
    RelInc = (Func_ant - Func) / Func_ant #Evalúa la cercanía
    Func_ant = Func
    cadena = 'Niter=' + str(niter) + ' F=' + str(Func) + ' RelInc=' + str(RelInc)
    print(cadena)

print(tcest)
#--------------------------------------------------------------------------------------------------------------

#Determinamos las muestras de comienzo de cada señal
mcest = np.ceil(tcest * Fs)

#Determinamos el nuevo tamaño de cada señal aplicando el corte del tiempo de comienzo en cada caso
for i in range(Ndevices):
    tam_postdelay[i] = tam[i] - mcest[toaRef[i]]

#Adaptamos el tamaño de las señales con la señal de menos muestras (acortamos por abajo)
tam_final = min(tam_postdelay)

#En esta matriz se guardarán las señales sincronizadas
sincronizadas = np.zeros((tam_final, Ndevices))

plt.figure(4)
plt.title('Señales sincronizadas')
plt.xlabel('Muestras')
plt.ylabel('Amplitud')

#Recortamos las señales
for i in range(Ndevices):
    limite = tam_final + int(mcest[toaRef[i]])
    sincronizadas[:, i] = record[int(mcest[toaRef[i]]):limite, i] #Acortamos por arriba
    plt.plot(sincronizadas[:,i])


#Hacemos la correlación de las señales
for z in range(Ndevices):
    rx_sincro = scipy.signal.correlate(sincronizadas[:,z], sincronizadas[:, toaRef[0]], mode = 'full')
    N = len(rx_sincro)
    k = np.linspace(-(N/2) +1, (N/2)-1, N)
    
    plt.figure(z+5)
    plt.plot(k, rx_sincro)
    plt.title('Correlación cruzada señales ajustadas')
    # Calculamos el delay final para todas las señales
    delay_final[z] = correlaMax(rx_sincro, N)
    print('El delay es de:', delay_final[z], 'muestras')    
#----------------------------------------------------------------------------------------------------


