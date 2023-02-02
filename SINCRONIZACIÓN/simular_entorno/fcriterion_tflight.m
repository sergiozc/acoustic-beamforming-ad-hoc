function [F,tdoaest] = fcriterion_tflight(tdoamed,T_flight_est, Tcest)

N=length(Tcest);
F=0;
for k=1:N
    for i=1:N
        for j=1:N
            tdoaest{k}(i,j) = T_flight_est(i,k) - T_flight_est(j,k);
            tdoaest{k}(i,j)=tdoaest{k}(i,j) - Tcest(i) + Tcest(j);
            F = F+(tdoaest{k}(i,j)-tdoamed{k}(i,j))^2;
        end
    end
end