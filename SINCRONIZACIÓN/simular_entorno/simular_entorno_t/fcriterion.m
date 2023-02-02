function [F,tdoaest]=fcriterion(tdoamed,tf_est,Tcest)

N = length(Tcest);
F = 0;
for k=1:N
    for i=1:N
        for j=1:N
            tdoaest{k}(i,j) = tf_est(i,k) - tf_est(j,k) - Tcest(i) + Tcest(j);
            F = F + (tdoaest{k}(i,j) - tdoamed{k}(i,j))^2;
        end
    end
end