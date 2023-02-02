function grd=grad_Tc(tdoaest,tdoamed)

N=length(tdoaest);

grd=zeros(1,N);
for n=1:N
  for k=1:N
    for i=1:N
        tau_dif=tdoaest{k}(i,n)-tdoamed{k}(i,n);
        grd(n)=grd(i)+tau_dif;
    end
  end
end
grd=grd*4;

% grd=[];
% for a=1:N
%     gt=0;
%     for k=1:N
%         for i=1:N
%             for j=1:N
%                 
%                 if (a==i)
%                     deriv=-1;
%                 elseif (a==j)
%                     deriv=1;
%                 else
%                     deriv=0;
%                 end
%                     
%                 gt=gt+(tdoaest{k}(i,j)-tdoamed{k}(i,j))*deriv;
% 
%             end
%         end
%     end
%     grd=[grd 2*gt];
% end