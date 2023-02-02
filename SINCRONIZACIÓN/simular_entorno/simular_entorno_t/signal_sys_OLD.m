% signal_sys.m: simulacion de generación de senales en array ad-hoc

% Parametros generales
c=343;      % vel. propagacion sonido (m/s)
Fs=44100;   % freq. muestreo (Hz)
N=3;        % Num microfonos
Tchirp=0.1; % duracion del chirp (s)
Trec=1;     % duracion grabaciones (s)

% Variables conocidas
% Distancias micro-altavoz
d=[0.12 0.10 0.11];
% Posiciones angulares altavoces
phi=[90 45 -90]*pi/180;

% Variables desconocidas
% Posiciones de los microfonos (m)
M=[0 0 1;
   0 1 1];
% Instantes de comienzo de las capturas (s)
Tc=[0 1e-3 2e-3];
% Tiempos de emision de los chirps
Ts=[0.1 0.3 0.5];
% Calculo de los TOAs
S=M+[d.*cos(phi); d.*sin(phi)];
for i=1:N
    for k=1:N
        toaabs=Ts(k)+norm(S(:,k)-M(:,i))/c; %tiempo llegada absoluto
        toa(i,k)=toaabs-Tc(i); %TOA: relativo a comienzo grabacion en i
    end
end
% Tablas de TDOAs
for k=1:N
    tdoa{k}=[];
    for i=1:N
      for j=1:N
          tdoa{k}(i,j)=toa(i,k)-toa(j,k);
      end
    end
end

% Generacion de la excitacion (swept sine chirp)
excit=[];
Tchirp=0.1; % duracion
Nsamp=Tchirp*Fs;
Fsw=[5000 16000]/Fs; Inclog=log(Fsw(2)/Fsw(1));
n=0:Nsamp;
excit=sin(2*pi*Fsw(1)*Nsamp*(exp(Inclog*n/Nsamp)-1)/Inclog);
Lexcit=length(excit);
%excit=sin(2*pi*Fsw(1)*(Fsw(2)/Fsw(1)).^(n/Nsamp).*n);
%plot(excit)

% Simulacion de la transmision de los chirps
% Generacion de canal de transmision altavoz-micro generico
Lfilt=4;
haltmic=ones(Lfilt,1)/Lfilt; %filtro LPF media
exfilt=filter(haltmic,1,excit); Lex=length(exfilt);
% Ganancias transmision gain(i,j) altavoz "j" a micro "i"
gain=[1 0.9 0.8;
      0.9 1 0.9;
      0.8 0.8 0.9];
% Generacion de las senales (cada micro graba Trec sec)
Nsamptot=floor(Trec*Fs);
for i=1:N
    x{i}=0.5*randn(1,Nsamptot); %ruido de fondo blanco
    for k=1:N
        ntoa=round(toa(i,k)*Fs);
        x{i}(ntoa+1:ntoa+Lex)=x{i}(ntoa+1:ntoa+Lex)+gain(i,k)*exfilt;
    end
end

% Estimacion de los TOAs
for i=1:N
    xdec=conv(x{i},excit(end:-1:1));
    xdec=xdec(Lexcit+1:end);
    [~,I]=sort(xdec,'descend');
    Idx{i}=I;
%     subplot(2,1,1), plot(x{i})
%     subplot(2,1,2), plot(xdec)
%     pause
end
ntoaest=[];
%Estimamos TOAs 
for i=1:N
    %Para cada i seleccionamos solo N instantes separados al menos por Lexcit
    ntoaest(i,1)=Idx{i}(1);
    nfound=1;
    nsearch=2;
    while (nfound < N)
        count=0;
        for n=1:nfound
          cond = abs(Idx{i}(nsearch)-ntoaest(i,n)) >= Lexcit;
          count = count + cond;
        end
        if (count == nfound) 
            nfound=nfound+1;
            ntoaest(i,nfound)=Idx{i}(nsearch);
        else
            nsearch=nsearch+1;
        end
    end
    ntoaest(i,:)=sort(ntoaest(i,:));
end
%ntoa=round(toa*Fs)+1
%ntoaest
toa
toaest=(ntoaest-1)/Fs
