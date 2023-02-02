% signal_sys_tflight.m: simulacion de generación de senales en array ad-hoc

% Parametros generales
c=343;      % vel. propagacion sonido (m/s)
Fs=44100;   % freq. muestreo (Hz)
N=3;        % Num microfonos
Tchirp=0.1; % duracion del chirp (s)
Trec=1;     % duracion grabaciones (s)
P=2;        % No. dimensiones operativas
mu=0.01;    % Factor de convergencia
RelInc=0.01;% Criterio de convergencia

% Variables conocidas
% Distancias micro-altavoz
d=[0.12 0.10 0.11];
% Posiciones angulares altavoces
phi=[90 45 -90]*pi/180;
Mrel_loudsp=[d.*cos(phi); d.*sin(phi)];

% Variables desconocidas
% Posiciones de los microfonos (m)
M=[0 0 1;
   0 1 1];
% Calculo de las distancias
D=[];
for i=1:N
    for j=1:N
        D(i,j)=norm(M(:,i)-M(:,j));
    end
end
% Instantes de comienzo de las capturas (s)
Tc=[0 1e-3 2e-3];
% Tiempos de emision de los chirps
Ts=[0.1 0.3 0.5];

% CÁLCULO TOA
S = M + Mrel_loudsp;
for i=1:N
    for k=1:N
        t_flight(i,k) = norm(S(:,k)-M(:,i))/c;
        toaabs = Ts(k) + t_flight(i,k); %tiempo llegada absoluto
        toa(i,k) = toaabs - Tc(i); %TOA: relativo a comienzo grabacion en i
    end
end

% Tablas de TDOAs
for k=1:N
    tdoa{k}=[];
    for i=1:N
      for j=1:N
          tdoa{k}(i,j) = toa(i,k) - toa(j,k);
      end
    end
end

% GENERACIÓN DE LA EXCITACIÓN (swept sine chirp)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
excit=[];
Tchirp=0.1; % duracion
Nsamp = Tchirp * Fs;
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
randn('seed',50)
Nsamptot=floor(Trec*Fs);
for i=1:N
    x{i}=0.2*randn(1,Nsamptot); %ruido de fondo blanco
    for k=1:N
        ntoa=round(toa(i,k)*Fs);
        x{i}(ntoa+1:ntoa+Lex)=x{i}(ntoa+1:ntoa+Lex)+gain(i,k)*exfilt;
    end
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%MEDICIÓN DE LOS TOAs
for i=1:N
    xdec = conv(x{i},excit(end:-1:1)); %Correlación
    xdec=xdec(Lexcit+1:end);
    [~,I]=sort(xdec,'descend');
    Idx{i}=I;
     subplot(2,1,1), plot(x{i})
     subplot(2,1,2), plot(xdec)
     pause
end
ntoamed=[];
% Medimos los TOAs 
for i=1:N
    %Para cada i seleccionamos solo N instantes separados al menos por Lexcit
    ntoamed(i,1)=Idx{i}(1);
    nfound=1;
    nsearch=2;
    while (nfound < N)
        count=0;
        for n=1:nfound
          cond = abs(Idx{i}(nsearch)-ntoamed(i,n)) >= Lexcit;
          count = count + cond;
        end
        if (count == nfound) 
            nfound=nfound+1;
            ntoamed(i,nfound)=Idx{i}(nsearch);
        else
            nsearch=nsearch+1;
        end
    end
    ntoamed(i,:)=sort(ntoamed(i,:));
end
%ntoa=round(toa*Fs)+1
%ntoamed
toa
toamed=(ntoamed-1)/Fs
% Tablas de TDOAs medidos
for k=1:N
    tdoamed{k}=[];
    for i=1:N
      for j=1:N
          tdoamed{k}(i,j) = toamed(i,k) - toamed(j,k);
      end
    end
end

% Estimamos posiciones iniciales (esto no interesa en caso de beamforming)
Dest=[];
for i=1:N
    for j=1:N
        Dest(i,j)=c*(toamed(j,i)-toamed(i,i)+toamed(i,j)-toamed(j,j))/2;
    end
end
Q=eye(N)-ones(N,N)/N;
Best=-Q*Dest*Q/2;
[V,Lamb]=eig(Best);
[Lamb,I]=sort(diag(Lamb),'descend');
Lamb=diag(Lamb(1:P));
V=V(:,I(1:P));
Sig=Lamb.^(1/2);
Mest=V*Sig;
Mest=Mest';
Mest=transforma(Mest);
Sest=Mest+Mrel_loudsp;

% Estimamos los INSTANTES DE COMIENZO INICIALES
Tcest=[];
Tcest(1)=0;
for i=2:N
    Tcest(i)=(toamed(i-1,i-1)-toamed(i,i-1)+toamed(i-1,i)-toamed(i,i))/2+Tcest(i-1);
end
Tcest

% % OPTIMIZACION
% Perturbamos las estimas iniciales para evitar local minima
maskM=ones(P,N); maskM(:,1)=zeros(P,1); maskM(1,2)=0;
Mest=Mest+0.2*randn(P,N).*maskM;
%Mest=transforma(Mest);
Tcest=Tcest+10*randn(1,N)/Fs; Tcest(1)=0;
% Descenso en gradiente
mu=1e-2;
[Func_ant,tdoaest]=fcriterion(tdoamed,Sest,Mest,Tcest,c);
%[Func_ant,tdoaest] = fcriterion_tflight(tdoamed, T_flight_est, Tcest);
Func_ant
RelInc=1e20; niter=0;
while (RelInc>0.0001)
    Mest=Mest-mu*gradm(tdoaest,tdoamed,Sest,Mest,c);
    %T_flight_est = T_flight_est - mu*gradt_flight(tdoaest,tdoamed);
    Tcest=Tcest-mu*gradt(tdoaest,tdoamed);
    Sest=Mest+Mrel_loudsp;
    Tcest=Tcest-Tcest(1);
    [Func,tdoaest]=fcriterion(tdoamed,Sest,Mest,Tcest,c);
    %[Func,tdoaest] = fcriterion_tflight(tdoamed, T_flight_est, Tcest);
    niter = niter + 1;
    RelInc=(Func_ant-Func)/Func_ant;
    Func_ant=Func;
    MSE=mean(sum(abs(Mest-M).^2));
    cadena=strcat('Niter=',num2str(niter),' F=',num2str(Func),' RelInc=',num2str(RelInc));
    cadena=strcat(cadena,' sqrtMSE=',num2str(sqrt(MSE)));
    disp(cadena)
    %pause
end