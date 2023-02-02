# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 17:05:12 2022

@author: Sergio
"""


import numpy as np
import scipy
import scipy.io
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
import wave

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
            

def timeVector(signal, Fs):
    
    'Función que devuelve el vector de tiempos dada una señal y su frecuecia'
    'de muestreo'
    
    L = len(signal)
    T = L / Fs
    t = np.linspace(0, T, L)
    
    return t


def tren_impulsos(Nimp, len_tren):
    
    'Función que crea una señal acústica de sincronización'
    'correspondiente a un tren de un número de impulsos dado'
    
    Fs = 44100
    tren = np.zeros(len_tren)
    
    #Longitud en muestras de cada impulso
    len_impulso = 10
    #margen de muestras para que se reproduzca correctamente
    margen = 2000 
    #Separación entre impulsos
    intervalo = int((len_tren - margen) / Nimp)
    #Posición primer impulso
    pos_ini = 10000

    for i in range(Nimp):
        pos = pos_ini + intervalo * i
        for j in range(len_impulso):
            tren[pos + j] = np.iinfo(np.int16).max
            
    return tren


def correlaMax(rx, N):
    
    'Función que devuelve el pico de la correlación de dos señales.'
    
    peak = np.where(rx == max(rx))
    delay = int(np.ceil(float(peak[0]) - N / 2.0))
    
    return delay

def correlaPeaks(correla, Npeaks, Lexc):
    
    ntoa = np.zeros(Npeaks)
    #Nos quedamos con los índices de los valores de la correlación ordenados
    #de mayor a menor, es decir, el primer índice o instante se corresponde con el índice
    #del máximo valor de la correlación
    indices = np.argsort(correla) #Se ordena de menor a mayor
    indices = indices[::-1] #Ordenado de mayor a menor
    ntoa[0] = indices[0] #El valor máximo de la correlación se corresponde con un TOA
    nfound = 1 #Número de TOAs encontrados
    nsearch = 1 #Por donde empieza la búsqueda
    
    #Iremos comparando valor por valor, en los máximos.
    #Si la distancia es mayor que Lexc, se cumple la condición y se incrementa el contador.
    #Al incrementarse el contador, se incorpora el valor a los toas.
    #Por último se ordenan por orden de llegada
    while nfound < Npeaks:
        cont = 0
        for n in range(nfound):
            cond = np.abs(indices[nsearch] - ntoa[n]) >= Lexc #Booleana
            cont = cont + cond
        if cont == (nfound):
            nfound = nfound + 1
            ntoa[nfound-1] = indices[nsearch]
        else:
            nsearch = nsearch + 1
    
    ntoa = np.sort(ntoa)
    
    return ntoa

##################################################################################

def sincro(Ndevices):
    
    'Función que dadas dos grabaciones, las sincroniza coherentemente'
    
    RawToWav('Device0')
    RawToWav('Device1')
    RawToWav('Device2')

    
    record = np.zeros((17938000, Ndevices)) #Matriz de las grabaciones
    Lexc = 10000 #Longitud en muestras aprox de un impulso
    tam = np.arange(Ndevices)
    tam_postdelay = np.arange(Ndevices) #Tamaño después de acortar con el delay inicial
    lim_tren = 44100 * 3 #Acortamos a 3 segundos para captar la señal de sincronización
    #lim_tren = 200000
    toa = np.arange(Ndevices) #Tiempo de llegada (en muestras)
    toamed = np.arange(Ndevices) #Tiempo de llegada (en muestras)
    tren = np.zeros((lim_tren, Ndevices)) #Matriz donde guardamos el impulso de cada señal
    delay = np.arange(Ndevices) #Vector de restraso de una señal respecto a la primera en comenzar
    delay_final = np.arange(Ndevices)
    tren_orig = np.zeros(lim_tren)
    
    #Fs, tren_orig = wavfile.read('chirp2.wav')
    Fs, tren_orig = wavfile.read('tren_impulsos.wav')
    #Fs, tren_orig = wavfile.read('impulso.wav')
    #Fs, tren_orig = wavfile.read('chirp_creado.wav')
    
    for i in range(Ndevices):
        #Guardamos en volatil el contenido de la grabación i
        Fs, volatil = wavfile.read('Device'+ str(i) + '.wav')
        
        #Guardamos el número de muestras de la grabación i
        tam[i] = len(volatil)
        #Guardamos en cada columna de 'record' las grabaciones (hasta la fila correspondiente
        #al número de muestras de cada grabación)
        record[:tam[i], i] = volatil
        #Guardamos únicamente la señal de sincronización
        tren[:, i] = volatil[:lim_tren]
        
        rx_tren = scipy.signal.correlate(tren[:, i], tren_orig, mode = 'full', method='fft')
        #Se calcula el pico de correlación central (máximo)
        ntoa = correlaPeaks(rx_tren, 5, Lexc)
        toa[i] = int(np.median(ntoa))
        N = len(rx_tren)
        
        # plt.figure(i+1)
        # plt.plot(volatil)
        # plt.title('Señal inicial')
        # plt.xlabel('Muestras')
        # plt.ylabel('Amplitud')
        
        # plt.figure(i+1)
        # plt.plot(volatil[:lim_tren])
        # plt.title('Tren de impulsos')
        # plt.xlabel('Muestras')
        # plt.ylabel('Amplitud')
        
        # plt.figure(i+10)
        # plt.subplot(211)
        # plt.plot(tren[:, i])
        # plt.subplot(212)
        # plt.plot(k,rx_tren)
        
    # plt.figure(9)
    # plt.plot(tren_orig)
        
    #Cuál es la grabación que comienza antes
    primera = np.argmin(toa)
    print('Comienza Device ' + str(primera))
    for i in range(Ndevices):
    
        rx_tren2 = scipy.signal.correlate(tren[:, i], tren[:,primera], mode = 'full', method='fft')
        N = len(rx_tren2)
        k = np.linspace(-(N/2) +1, (N/2)-1, N)
        
        plt.figure(i+1)
        plt.title('Autocorrelación')
        plt.xlabel('Muestras')
        plt.ylabel('Correlación')
        plt.plot(k,rx_tren2)
        
        toamed[i] = correlaMax(rx_tren2, len(rx_tren2))
        tam_postdelay[i] = tam[i] - toamed[i]
    
    
    #Tamaño de las señales después de aplicar el delay y ajustándose a la señal con menos muestras
    tam_final = min(tam_postdelay)
    #En esta matriz se guardarán las señales sincronizadas
    sincronizadas = np.zeros((tam_final, Ndevices))
    
    plt.figure(4)
    plt.title('Señales sincronizadas')
    plt.xlabel('Muestras')
    plt.ylabel('Amplitud')
    
    #Guardamos las señales en la nueva matriz
    for z in range(Ndevices):
        lim_final = tam_final + toamed[z]
        sincronizadas[:, z] = record[toamed[z]:lim_final, z]
        plt.plot(sincronizadas[:,z])
     
    #Hacemos la correlación de las señales
    for z in range(Ndevices):
        rx_sincro = scipy.signal.correlate(sincronizadas[:,z], sincronizadas[:,primera], mode = 'full')
        N = len(rx_sincro)
        k = np.linspace(-(N/2) +1, (N/2)-1, N)
    
        #plt.figure(z+5)
        #plt.plot(k, rx_sincro)
        #plt.title('Correlación cruzada señales ajustadas')
        
    #MATRIZ DE TODOS LOS RETARDOS FINALES
    delay_matriz = np.zeros((Ndevices, Ndevices))
    
    for i in range(Ndevices):
        for j in range(Ndevices):
            rx_matriz = scipy.signal.correlate(sincronizadas[:,i], sincronizadas[:,j], mode = 'full')
            N = len(rx_matriz)
            delay_matriz[i, j] = correlaMax(rx_matriz, N)
            
    print('Matriz de retardos finales:' )
    print(delay_matriz)
    
    return sincronizadas

##############################################################################################


