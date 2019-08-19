DEFI
STIF s
MASS m
DAMP c
LOAD f
TYPE w
MDTY d
INIT 2

EQUATION
VECT u1,v1
READ(s,unod) u1,v1
\ ---------------------------------------------------------------
\ ................ M*U,tt + C*U,t = LU + F
\ ---------------------------------------------------------------
\ ................ U,t = V
\ ................ M*V,t + C*V - LU = F
\ ---------------------------------------------------------------
\ (V(n+1)+V(n))/2 = (U(n+1)-U(n))/dt
\ M*V,t + C*V - L(U(n+1)+U(n))/2 = F
\ M*(V(n+1)-V(n)) + C*(V(n+1)+V(n))*dt/2 - L(U(n+1)+U(n))*dt/2 = F*dt
\ M*(V(n+1)+V(n)) - M*V(n)*2 + C*(V(n+1)+V(n))*dt/2 - L(U(n+1)+U(n))*dt/2
\ = F*dt
\ M*(U(n+1)-U(n))*2/dt - M*V(n)*2 + C*(U(n+1)-U(n)) - L(U(n+1)+U(n))*dt/2
\ = F*dt
\ M*U(n+1)*2/dt  + C*U(n+1) - LU(n+1)*dt/2
\ = F*dt + M*V(n)*2 + M*U(n)*2/dt + C*U(n) + LU(n)*dt/2
\ M*U(n+1)  + C*U(n+1)*dt/2 - LU(n+1)*dt*dt/4
\ = F*dt*dt/2 + M*V(n)*dt + M*U(n) + C*U(n)*dt/2 + LU(n)*dt*dt/4
\ (M+C*dt/2+S*dt*dt/4)*U(n+1)
\ = F*dt*dt/2 + M*V(n)*dt + M*U(n) + C*U(n)*dt/2 - S*U(n)*dt*dt/4
\ ---------------------------------------------------------------
MATRIX = [s]*(dt/2.)*(dt/2.)+[c]*dt/2.+[m]
FORC = [f]*dt*dt/2.+[m*u1]+[m*v1]*dt+[c*u1]*dt/2.-[s*u1]*dt*dt/4.

SOLUTION u
VECT u,u1,v1
READ(s,unod) u1,v1
[v1] = [u]/dt*2.-[u1]/dt*2.-[v1]
[u1] = [u]
WRITE(o,unod) u1,v1

END
