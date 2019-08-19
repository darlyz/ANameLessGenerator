\ 显式计算已知量或已求得量的某种表达式的值分布的最小二乘法str.sch
\ 空间离散后矩阵形式为：
\           [S][U]=[F]
\ ---------------------------------------------------
DEFI
STIF s
MASS m
LOAD f
TYPE e
MDTY l

EQUATION
\............ 线性方程组左端项(集中矩阵) .............../
L,MASS = [m]
\................. 线性方程组右端项 ..................../
FORC = [f]

SOLUTION w
VECT w
$CC if (init == 0) init = 1;
$cc // 存储求解的w
WRITE(s,unod) w

@NBDE
 ntype = nbdetype;


END

