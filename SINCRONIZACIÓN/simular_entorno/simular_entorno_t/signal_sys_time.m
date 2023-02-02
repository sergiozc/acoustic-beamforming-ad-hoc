%% signal_sys.m: simulacion de generación de senales en array ad-hoc

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
% Calculo de los TOAs
S=M+Mrel_loudsp;
for i=1:N
    for k=1:N
        tf(k,i) = norm(S(:,k)-M(:,i))/c; %Tiempo de vuelo
        toaabs = Ts(k) + tf(k,i); %tiempo llegada absoluto
        toa(i,k)= toaabs - Tc(i); %TOA: relativo a comienzo grabacion en i
    end
end
% Tablas de TDOAs
%Diferencia del tiempo de llegada entre movil1 y movil1, movil1 y movil2,
%movil1 y movilN, movil2 y movilN etc
for k=1:N
    tdoa{k}=[];
    for i=1:N
      for j=1:N
          tdoa{k}(i,j)=toa(i,k) - toa(j,k);
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
plot(excit)

% Simulacion de la transmision de los chirps
% Generacion de canal de transmision altavoz-micro generico
Lfilt=4;
%Generar canal generico fuente-micro
%haltmic=ones(Lfilt,1);
haltmic=exp(-[0:Lfilt-1]);
haltmic=haltmic'/sum(haltmic);
exfilt=filter(haltmic,1,excit); Lex=length(exfilt);
% Ganancias transmision gain(i,j) altavoz "j" a micro "i"
gain=[1 0.9 0.8;
      0.9 1 0.9;
      0.8 0.8 0.9];
% Generacion de las senales (cada micro graba Trec sec)
%randn('seed',50)
varn=0.; %varn=0.01;
Nsamptot=floor(Trec*Fs);
for i=1:N
    x{i}=sqrt(varn)*randn(1,Nsamptot); %ruido de fondo blanco
    for k=1:N
        ntoa=round(toa(i,k)*Fs);
        x{i}(ntoa+1:ntoa+Lex)=x{i}(ntoa+1:ntoa+Lex)+gain(i,k)*exfilt;
    end
end

%%%%%%%%%% Medicion de los TOAs y TDOAs correspondientes
% Detectar instantes de comienzo del chirp en cada señal
for i=1:N
    xdec=conv(x{i},excit(end:-1:1)); % correlacion cruzada
    xdec=xdec(Lexcit+1:end);
    [~,I]=sort(xdec,'descend');
    Idx{i}=I; %Guarda los índices de las correlaciones de los %3 móviles ordenando sus valores de mayor a menor
    
%      subplot(2,1,1), plot(x{i})
%      subplot(2,1,2), plot(xdec)
%      pause
end
ntoamed=[];
% Medimos los TOAs: para cada micro/signal i seleccionamos solo N instantes
% separados al menos por Lexcit
for i=1:N %recorremos micros
    ntoamed(i,1)=Idx{i}(1); % instante primer chirp (máximo de toda la correlación)
    nfound=1; %Encontrados
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
          tdoamed{k}(i,j)=toamed(i,k)-toamed(j,k);
      end
    end
end


%%%%%%%%%%%%%%%%%%% ESTIMACIONES
disp('Valores reales')
tf
Tc
disp('Estimas iniciales')
% Estimamos tiempos de vuelo iniciales
tf_est=[];
for i=1:N
    for j=1:N
        tf_est(i,j) = (tdoamed{j}(i,j) - tdoamed{i}(i,j)) / 2;
    end
end
tf_est

% Estimamos los instantes de comienzo iniciales
Tcest=[];
Tcest(1)=0;
for i=2:N
    Tcest(i)=(toamed(i-1,i-1)-toamed(i,i-1)+toamed(i-1,i)-toamed(i,i))/2+Tcest(i-1);
end
Tcest

% % OPTIMIZACION
% Perturbamos las estimas iniciales para evitar local minima
tf_est=tf_est+10*randn(N,N)/Fs;
Tcest=Tcest+10*randn(1,N)/Fs; Tcest(1)=0;
% Descenso en gradiente
mu=1e-3;
[Func_ant,tdoaest]=fcriterion(tdoamed,tf_est,Tcest);
Func_ant %Valor de la función con las estimas iniciales
RelInc=1e20; %Criterio de convergencia (al principio se le da un valor grande cualquiera)
niter=0;
while (RelInc>0.0001)
    muc=mu*exp(-0.01*niter); %Velocidad de aprendizaje
    tf_est=tf_est-muc*grad_tf(tdoaest,tdoamed,tf_est);
    Tcest=Tcest-muc*grad_Tc(tdoaest,tdoamed);
    Tcest=Tcest-Tcest(1);
    [Func,tdoaest]=fcriterion(tdoamed,tf_est,Tcest);
    niter=niter+1;
    RelInc=(Func_ant-Func)/Func_ant; %Evalúa la cercanía 
    Func_ant=Func;
    cadena=strcat('Niter=',num2str(niter),' F=',num2str(Func),' RelInc=',num2str(RelInc));
    MSE=mean(abs(Tcest-Tc).^2);
    cadena=strcat(cadena,' sqrtMSE_Tc=',num2str(sqrt(MSE)));
    disp(cadena)
    %pause
end
disp('Estimas finales')
tf_est = max(tf_est,0)
Tcest
Func
