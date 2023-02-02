function Mtrans=transforma(M)

t=M(:,1); z2=M(:,2)-t;
%Phi=atan2(-z2(1),z2(2))
Phi=atan(-z2(1)/z2(2))
if cos(Phi)*z2(2) < sin(Phi)*z2(1)
    Phi=Phi+pi
end
A=[cos(Phi) sin(Phi); -sin(Phi) cos(Phi)];
Mtrans=A*(M-t)