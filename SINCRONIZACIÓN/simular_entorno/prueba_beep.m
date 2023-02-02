clc;
clear all;
close all;

f = 20000;
Fs = 44100;
Ts = 1 / Fs;
t = 0:Ts:0.1;

beep = sin(2 * pi * f * t);
figure(1)
plot(beep)
sound(beep)