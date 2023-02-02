N=3
coef=zeros(N*N+N-1,N*N+N-1);
for m=0:N-1
    for n=0:N-1
        for i=0:N-1
            coef(N*m+n+1,N*m+n+1)=coef(N*m+n+1,N*m+n+1)+1;
            coef(N*m+n+1,N*m+i+1)=coef(N*m+n+1,N*m+i+1)-1;
            if (n>0)
                coef(N*m+n+1,N*N+n)=coef(N*m+n+1,N*N+n)-1;
            end            
            if (i>0)
                coef(N*m+n+1,N*N+i)=coef(N*m+n+1,N*N+i)+1;
            end
        end
    end
end
for n=1:N-1
    for k=0:N-1
        for i=0:N-1
            coef(N*N+n,N*k+i+1)=coef(N*N+n,N*k+i+1)+1;
            coef(N*N+n,N*k+n+1)=coef(N*N+n,N*k+n+1)-1;
        end
    end
end
for n=1:N-1
    for k=0:N-1
        for i=0:N-1
            coef(N*N+n,N*N+n)=coef(N*N+n,N*N+n)+1;
            if (i>0)
                coef(N*N+n,N*N+i)=coef(N*N+n,N*N+i)-1;
            end
        end
    end
end
coef
rcond(coef)