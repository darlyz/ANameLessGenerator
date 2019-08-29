DEFI
STIF s
MASS m
LOAD f
TYPE e
MDTY l
INIT 1

COEF u

EQUATION
VECT u
READ(s,unod) u
L,MASS=[m]
FORC=[f]

SOLUTION w
VECT w
WRITE(o,unod) w

END
