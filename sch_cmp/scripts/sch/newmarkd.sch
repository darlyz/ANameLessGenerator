DEFI
STIF s
MASS m
DAMP c
LOAD f
TYPE w
MDTY d
INIT 3

EQUATION
\ ---------------------------------------------------------------
\ ................ M*U,tt + C*U,t = LU + F
\ ---------------------------------------------------------------
\ ................ U,t = V
\ ................ M*V,t + C*V - LU = F
\ ---------------------------------------------------------------
VECT u1,v1,w1
READ(s,unod) u1,v1,w1
MATRIX = [s]+[m]*a0+[c]*a1
FORC = [f]+[m*u1]*a0+[m*v1]*a2+[m]*[w1]*a3+[c*u1]*a1+[c]*[v1]*a4+[c]*[w1]*a5

SOLUTION u
VECT u,v,w,,u1,v1,w1
READ(s,unod) u1,v1,w1
[w] = ([u]-[u1])*a0-[v1]*a2-[w1]*a3
[v] = [v1]+[w]*a7+[w1]*a6
WRITE (o,unod) u,v,w

@BEGIN
 double o,a0,a1,a2,a3,a4,a5,a6,a7,aa;
        o = 0.5;
        aa = 0.25*(.5+o)*(.5+o);
        a0 = 1./(dt*dt*aa);
        a1 = o/(aa*dt);
        a2 = 1./(aa*dt);
        a3 = 1./(2.*aa)-1.;
        a4 = o/aa-1.;
        a5 = dt/2.*(o/aa-2.);
        a6 = dt*(1.-o);
        a7 = dt*o;

END
