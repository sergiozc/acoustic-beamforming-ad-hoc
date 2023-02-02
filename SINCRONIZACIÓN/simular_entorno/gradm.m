function grd=gradm(tdoaest,tdoamed,Sest,Mest,c)

[dim,N]=size(Sest);

grd=[];
for a=1:N
    ga=zeros(2,1);
    for k=1:N
        for i=1:N
            for j=1:N
                
                if (a==i)&&(a~=j)&&(a~=k)
                    deriv=-(Sest(:,k)-Mest(:,i)) / norm(Sest(:,k)-Mest(:,i));
                elseif (a~=i)&&(a==j)&&(a~=k)
                    deriv=(Sest(:,k)-Mest(:,j)) / norm(Sest(:,k)-Mest(:,j));
                elseif (a~=i)&&(a~=j)&&(a==k)
                    deriv=(Sest(:,k)-Mest(:,i)) / norm(Sest(:,k)-Mest(:,i));
                    deriv=deriv-(Sest(:,k)-Mest(:,j)) / norm(Sest(:,k)-Mest(:,j));
                elseif (a~=i)&&(a==j)&&(a==k)
                    deriv=(Sest(:,k)-Mest(:,i)) / norm(Sest(:,k)-Mest(:,i));
                elseif (a==i)&&(a~=j)&&(a==k)
                    deriv=-(Sest(:,k)-Mest(:,j)) / norm(Sest(:,k)-Mest(:,j));
                else
                    deriv=zeros(2,1);
                end
                    
                deriv=deriv/c;
                ga=ga+(tdoaest{k}(i,j)-tdoamed{k}(i,j))*(deriv);

            end
        end
    end
    grd=[grd 2*ga];
end