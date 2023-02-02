function grd=grad_tf(tdoaest,tdoamed,tf_est)

dim=size(tf_est);
N=dim(1);

grd=zeros(N,N);
for m=1:N
  for n=1:N
    for i=1:N
      tau_dif=tdoaest{m}(n,i)-tdoamed{m}(n,i);
      grd(m,n)=grd(m,n)+tau_dif;
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
%                     deriv = 1;
%                 elseif (a==j)
%                     deriv = -1;
%                 else
%                     deriv=0;
%                 end
%                     
%                 gt = gt + (tdoaest{k}(i,j) - tdoamed{k}(i,j)) * deriv;
% 
%             end
%         end
%     end
%     grd=[grd 2*gt];
% end